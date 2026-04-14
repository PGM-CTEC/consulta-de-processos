import asyncio
import httpx
import logging
import copy
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Story: REM-050 — External API Resilience (in-memory TTL cache)
from utils.ttl_cache import process_cache

# Story: BE-ARCH-002 - Retry Logic for Transient Failures
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    RETRY_AVAILABLE = True
except ImportError:
    RETRY_AVAILABLE = False

from config import settings
from exceptions import DataJudAPIException, InvalidProcessNumberException
from patterns.circuit_breaker import get_registry

logger = logging.getLogger(__name__)

class DataJudClient:
    def __init__(self):
        self.api_key = settings.DATAJUD_API_KEY
        self.base_url = settings.DATAJUD_BASE_URL
        self.timeout = settings.DATAJUD_TIMEOUT
        existing = get_registry().get("datajud-api")
        self._breaker = existing if existing else get_registry().create(
            name="datajud-api",
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=httpx.HTTPError,
        )
        
    def _get_tribunal_alias(self, process_number: str) -> str:
        """
        Determines the DataJud alias based on CNJ number segments.
        Format: NNNNNNN-DD.AAAA.J.TR.OOOO

        Raises:
            InvalidProcessNumberException: If process number format is invalid
            DataJudAPIException: If tribunal code is not recognized
        """
        # Remove formatting and validate
        clean = "".join(filter(str.isdigit, process_number))

        if len(clean) != 20:
            raise InvalidProcessNumberException(
                f"Número do processo deve ter 20 dígitos (recebido: {len(clean)})"
            )

        # Extract J (judicial segment) and TR (court code)
        # Position: NNNNNNN DD AAAA J TR OOOO
        #                        ↑ ↑↑
        #                       13 14-15
        j = clean[13]
        tr = clean[14:16]

        # State mapping for J=8 (State Courts - TJ)
        state_map = {
            "01": "tjac", "02": "tjal", "03": "tjam", "04": "tjap", "05": "tjba",
            "06": "tjce", "07": "tjdft", "08": "tjes", "09": "tjgo", "10": "tjma",
            "11": "tjmt", "12": "tjms", "13": "tjmg", "14": "tjpa", "15": "tjpb",
            "16": "tjpr", "17": "tjpe", "18": "tjpi", "19": "tjrj", "20": "tjrn",
            "21": "tjrs", "22": "tjro", "23": "tjrr", "24": "tjsc", "25": "tjsp",
            "26": "tjse", "27": "tjto"
        }

        # J=8: State Courts (TJ)
        if j == "8":
            court = state_map.get(tr)
            if not court:
                logger.warning(f"Unknown state court code: {tr}, using fallback CNJ API")
                return "api_publica_cnj"
            return f"api_publica_{court}"

        # J=4: Federal Regional Courts (TRF 1-5)
        elif j == "4":
            try:
                trf_num = int(tr)
                if trf_num < 1 or trf_num > 5:
                    raise DataJudAPIException(f"TRF inválido: {trf_num} (deve ser entre 1 e 5)")
                return f"api_publica_trf{trf_num}"
            except ValueError:
                raise DataJudAPIException(f"Código de TRF inválido: {tr}")

        # J=5: Labor Courts (TRT 1-24)
        elif j == "5":
            try:
                trt_num = int(tr)
                if trt_num < 1 or trt_num > 24:
                    raise DataJudAPIException(f"TRT inválido: {trt_num} (deve ser entre 1 e 24)")
                return f"api_publica_trt{trt_num}"
            except ValueError:
                raise DataJudAPIException(f"Código de TRT inválido: {tr}")

        # J=3: Electoral Courts (TRE)
        elif j == "3":
            court = state_map.get(tr)
            if court:
                return f"api_publica_tre{tr}"
            logger.warning(f"Unknown TRE code: {tr}, using fallback")
            return "api_publica_cnj"

        # J=6: Military Courts (TJM/STM)
        elif j == "6":
            if tr == "00":
                return "api_publica_stm"  # Superior Military Court
            return f"api_publica_tjm{tr}"

        # Unknown segment - use generic CNJ API
        logger.warning(f"Unknown judicial segment J={j}, TR={tr}, using fallback CNJ API")
        return "api_publica_cnj"

    @staticmethod
    def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value or not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _latest_movement_datetime(self, movements: List[Dict[str, Any]]) -> Optional[datetime]:
        latest: Optional[datetime] = None
        for mov in movements:
            dt = self._parse_iso_datetime(mov.get("dataHora"))
            if dt and (latest is None or dt > latest):
                latest = dt
        return latest

    def _instance_sort_key(self, source: Dict[str, Any]) -> datetime:
        latest_movement = self._latest_movement_datetime(source.get("movimentos", []))
        updated_at = self._parse_iso_datetime(source.get("dataHoraUltimaAtualizacao"))
        timestamp = self._parse_iso_datetime(source.get("@timestamp"))
        if not (latest_movement or updated_at or timestamp):
            logger.warning("No valid timestamps found in process data")
        return latest_movement or updated_at or timestamp or datetime.min

    def _summarize_instance(self, source: Dict[str, Any]) -> Dict[str, Any]:
        latest_movement = self._latest_movement_datetime(source.get("movimentos", []))
        orgao = source.get("orgaoJulgador", {}) or {}
        return {
            "grau": source.get("grau"),
            "tribunal": source.get("tribunal"),
            "orgao_julgador": orgao.get("nome") or orgao.get("codigo"),
            "latest_movement_at": latest_movement.isoformat() if latest_movement else None,
            "updated_at": source.get("dataHoraUltimaAtualizacao") or source.get("@timestamp"),
            "has_baixa_definitiva": self._has_baixa_definitiva(source),
        }

    def _instance_key(self, source: Dict[str, Any]) -> str:
        orgao = source.get("orgaoJulgador", {}) or {}
        orgao_id = orgao.get("codigo") or orgao.get("nome") or ""
        return f"{source.get('grau')}|{source.get('tribunal')}|{orgao_id}"

    def _has_baixa_definitiva(self, source: Dict[str, Any]) -> bool:
        """Verifica se algum dos últimos 5 movimentos é 'Baixa Definitiva' (código 22).

        Instâncias com Baixa Definitiva já remeteram o processo para outra instância
        e não devem ser selecionadas como padrão de visualização quando há alternativas.
        """
        movements = source.get("movimentos", []) or []
        sorted_movs = sorted(
            movements,
            key=lambda m: self._parse_iso_datetime(m.get("dataHora")) or datetime.min,
            reverse=True,
        )[:5]
        return any(m.get("codigo") == 22 for m in sorted_movs)

    def _select_latest_instance(
        self, hits: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        sources = [h.get("_source", h) for h in hits if isinstance(h, dict)]
        if not sources:
            return {}, {}

        selected_index = 0
        selected_by = "single_hit"

        if len(sources) > 1:
            # Prefer instances WITHOUT "Baixa Definitiva" in last 5 movements.
            # A instance with Baixa Definitiva already remitted the case and is not active.
            active_indices = [i for i, s in enumerate(sources) if not self._has_baixa_definitiva(s)]

            if active_indices:
                selected_index = max(active_indices, key=lambda i: self._instance_sort_key(sources[i]))
                has_baixa_skipped = len(active_indices) < len(sources)
                selected_by = "skip_baixa_definitiva" if has_baixa_skipped else "latest_movement_or_timestamp"
            else:
                # All instances have Baixa Definitiva — fall back to timestamp-based selection
                selected_index = max(range(len(sources)), key=lambda i: self._instance_sort_key(sources[i]))
                selected_by = "latest_movement_or_timestamp_all_baixada"

        selected = sources[selected_index]
        meta = {
            "instances_count": len(sources),
            "selected_by": selected_by,
            "selected_index": selected_index,
            "instances": [self._summarize_instance(s) for s in sources],
            "all_hits": [copy.deepcopy(s) for s in sources],
        }
        return copy.deepcopy(selected), meta

    async def _search_index(self, alias: str, clean_number: str) -> List[Dict[str, Any]]:
        if not self._breaker.allow_request():
            raise DataJudAPIException(
                "DataJud temporariamente indisponível (circuit breaker OPEN). Tente novamente em instantes."
            )

        url = f"{self.base_url}/{alias}/_search"
        logger.info(f"Requesting DataJud API: {alias}/_search for process {clean_number}")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"APIKey {self.api_key}"

        payload = {
            "query": {"match": {"numeroProcesso": clean_number}},
            "size": 50,
        }

        # Story: BE-ARCH-002 - Retry logic with exponential backoff
        if RETRY_AVAILABLE:
            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
                reraise=True
            )
            async def _post_with_retry(trust_env: bool) -> httpx.Response:
                async with httpx.AsyncClient(trust_env=trust_env) as client:
                    return await client.post(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=float(self.timeout)
                    )
        else:
            async def _post_with_retry(trust_env: bool) -> httpx.Response:
                async with httpx.AsyncClient(trust_env=trust_env) as client:
                    return await client.post(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=float(self.timeout)
                    )

        try:
            response = await _post_with_retry(trust_env=True)
        except httpx.RequestError as e:
            logger.warning(f"Network error connecting to DataJud with env proxy after retries: {str(e)}")
            try:
                response = await _post_with_retry(trust_env=False)
            except Exception as e:
                logger.error(f"Network error with both proxy modes after retries: {str(e)}")
                self._breaker.record_failure()
                raise

        try:
            if response.status_code == 404:
                logger.info(f"Process {clean_number} not found in {alias} (404)")
                self._breaker.record_success()  # 404 is a successful API response
                return []
            if response.status_code == 401:
                logger.error("DataJud API authentication failed (401)")
                self._breaker.record_failure()
                raise DataJudAPIException(
                    "Falha na autenticação com DataJud API. Verifique a chave de API."
                )
            if response.status_code == 429:
                logger.error("DataJud API rate limit exceeded (429)")
                self._breaker.record_failure()
                raise DataJudAPIException(
                    "Limite de requisições ao DataJud excedido. Tente novamente mais tarde."
                )
            if response.status_code >= 500:
                logger.error(f"DataJud server error {response.status_code}: {response.text[:200]}")
                self._breaker.record_failure()
                raise DataJudAPIException(
                    "Serviço DataJud temporariamente indisponível. Tente novamente."
                )
            if response.status_code != 200:
                logger.error(f"DataJud unexpected status {response.status_code}: {response.text[:200]}")
                raise DataJudAPIException(
                    f"Erro ao consultar DataJud (código {response.status_code})"
                )

            # Force UTF-8 encoding as DataJud often omits charset or sends mixed signals
            response.encoding = "utf-8"

            try:
                data = response.json()
            except Exception as e:
                logger.error(f"Failed to parse DataJud JSON response: {str(e)}")
                raise DataJudAPIException("Resposta inválida da API DataJud") from e

            hits = data.get("hits", {}).get("hits", [])
            result = [h.get("_source", h) for h in hits if isinstance(h, dict)]
            self._breaker.record_success()
            return result

        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to DataJud API: {url}")
            self._breaker.record_failure()
            raise DataJudAPIException(
                f"Timeout ao consultar DataJud (limite: {self.timeout}s)"
            )
        except httpx.RequestError as e:
            logger.error(f"Network error connecting to DataJud: {str(e)}")
            self._breaker.record_failure()
            raise DataJudAPIException(
                "Erro de conexão com DataJud. Verifique sua conexão de internet."
            ) from e
        except DataJudAPIException:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error querying DataJud: {type(e).__name__}")
            raise DataJudAPIException(
                "Erro inesperado ao consultar DataJud"
            ) from e

    def _merge_sources(self, primary: List[Dict[str, Any]], extra: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        merged: Dict[str, Dict[str, Any]] = {}
        for src in primary + extra:
            key = self._instance_key(src)
            current = merged.get(key)
            if not current or self._instance_sort_key(src) > self._instance_sort_key(current):
                merged[key] = src
        return list(merged.values())

    @staticmethod
    def _diagnose_missing_instances(hits: List[Dict[str, Any]]) -> List[str]:
        graus_present = {
            (h or {}).get("grau")
            for h in hits
            if isinstance(h, dict) and (h or {}).get("grau")
        }
        missing: List[str] = []
        # G2 sem G1: recurso ordinário sem 1ª instância correspondente.
        if "G2" in graus_present and "G1" not in graus_present:
            missing.append("G1")
        # TR sem JE: Turma Recursal (2ª instância) sem o Juizado Especial de origem (1ª instância).
        # O DataJud frequentemente indexa apenas o TR sem expor a tramitação do JE,
        # especialmente em processos anteriores a 2018.
        if "TR" in graus_present and "G1" not in graus_present and "JE" not in graus_present:
            missing.append("JE")
        return missing

    @staticmethod
    def _dedupe_aliases(aliases: List[str]) -> List[str]:
        unique: List[str] = []
        seen = set()
        for alias in aliases:
            if alias and alias not in seen:
                unique.append(alias)
                seen.add(alias)
        return unique

    def _expand_aliases_for_instances(self, alias: str) -> List[str]:
        """
        Expands a tribunal alias to include 1º/2º grau indexes when applicable.
        Some tribunals expose instance-specific indexes (e.g. _1g, _2g).
        """
        aliases = [alias]
        if alias.startswith("api_publica_tj") or alias.startswith("api_publica_trf") or alias.startswith("api_publica_trt"):
            aliases.extend([f"{alias}_1g", f"{alias}_2g"])
        return self._dedupe_aliases(aliases)

    @staticmethod
    def _has_second_instance(hits: List[Dict[str, Any]]) -> bool:
        # TR (Turma Recursal) é a 2ª instância dos Juizados Especiais,
        # assim como G2 é a 2ª instância do rito ordinário.
        return any((h or {}).get("grau") in ("G2", "TR") for h in hits if isinstance(h, dict))

    async def _search_aliases(self, aliases: List[str], clean_number: str) -> List[Dict[str, Any]]:
        deduped = self._dedupe_aliases(aliases)
        if not deduped:
            return []

        tasks = [self._search_index(alias, clean_number) for alias in deduped]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        merged_hits: List[Dict[str, Any]] = []
        for alias, result in zip(deduped, results):
            if isinstance(result, Exception):
                if isinstance(result, DataJudAPIException):
                    raise result
                logger.warning(f"Unexpected error querying alias {alias}: {type(result).__name__}: {result}")
                continue
            merged_hits = self._merge_sources(merged_hits, result)

        return merged_hits

    async def get_process(self, process_number: str) -> Optional[Dict[str, Any]]:
        """
        Fetches detailed process data from DataJud API.
        Attempts to find all instances across tribunal and CNJ indexes.

        Returns cached data (TTL=1h) when available to reduce API calls
        and provide resilience during API outages. (REM-050)
        """
        # Return from cache if available (TTL: 1 hour)
        cached = process_cache.get(process_number)
        if cached is not None:
            logger.debug("cache_hit", extra={"process_number": process_number})
            return cached

        selected, meta = await self.get_process_instances(process_number)

        if not selected:
            return None

        if meta:
            selected["__meta__"] = meta

        # Store result in cache for future requests
        process_cache.set(process_number, selected)
        return selected

    async def get_process_instances(
        self, process_number: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Busca instâncias do processo no índice principal e, se necessário,
        tenta ampliar via índice CNJ para detectar múltiplas instâncias.
        """
        try:
            alias = self._get_tribunal_alias(process_number)
        except (InvalidProcessNumberException, DataJudAPIException):
            raise
        except Exception as e:
            raise DataJudAPIException(f"Erro ao determinar tribunal: {str(e)}") from e

        clean_number = "".join(filter(str.isdigit, process_number))
        queried_aliases = self._expand_aliases_for_instances(alias)
        hits = await self._search_aliases(queried_aliases, clean_number)
        cnj_queried = False

        if not hits and alias != "api_publica_cnj":
            cnj_alias = "api_publica_cnj"
            queried_aliases.append(cnj_alias)
            hits = await self._search_aliases([cnj_alias], clean_number)
            cnj_queried = True

        if not hits:
            return None, None

        if len(hits) <= 1 and alias != "api_publica_cnj" and not cnj_queried:
            cnj_alias = "api_publica_cnj"
            queried_aliases.append(cnj_alias)
            cnj_hits = await self._search_aliases([cnj_alias], clean_number)
            if cnj_hits:
                hits = self._merge_sources(hits, cnj_hits)

        # If second instance is present, also inspect superior courts that may carry
        # the same CNJ number in a 3rd-instance path.
        if self._has_second_instance(hits):
            superior_aliases = ["api_publica_tst", "api_publica_stj", "api_publica_stf"]
            queried_aliases.extend(superior_aliases)
            superior_hits = await self._search_aliases(superior_aliases, clean_number)
            if superior_hits:
                hits = self._merge_sources(hits, superior_hits)

        selected, meta = self._select_latest_instance(hits)
        if meta:
            meta["aliases_queried"] = self._dedupe_aliases(queried_aliases)
            meta["total_hits_after_merge"] = len(meta.get("all_hits", []))
            missing_expected = self._diagnose_missing_instances(meta.get("all_hits", []))
            meta["missing_expected_instances"] = missing_expected
            meta["source_limited"] = bool(missing_expected)
            if missing_expected:
                meta["diagnostic_note"] = (
                    "Fonte DataJud não retornou todas as instâncias esperadas "
                    f"({', '.join(missing_expected)}) nos aliases consultados."
                )
            else:
                meta["diagnostic_note"] = "Cobertura de instâncias consistente com os dados retornados pela fonte."
        return selected, meta
