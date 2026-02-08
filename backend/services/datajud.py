import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from ..config import settings
from ..exceptions import DataJudAPIException, InvalidProcessNumberException

logger = logging.getLogger(__name__)

class DataJudClient:
    def __init__(self):
        self.api_key = settings.DATAJUD_API_KEY
        self.base_url = settings.DATAJUD_BASE_URL
        self.timeout = settings.DATAJUD_TIMEOUT
        
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
        }

    def _instance_key(self, source: Dict[str, Any]) -> str:
        orgao = source.get("orgaoJulgador", {}) or {}
        orgao_id = orgao.get("codigo") or orgao.get("nome") or ""
        return f"{source.get('grau')}|{source.get('tribunal')}|{orgao_id}"

    def _select_latest_instance(
        self, hits: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        sources = [h.get("_source", h) for h in hits if isinstance(h, dict)]
        if not sources:
            return {}, None

        if len(sources) == 1:
            return sources[0], None

        selected_index = max(range(len(sources)), key=lambda i: self._instance_sort_key(sources[i]))
        selected = sources[selected_index]
        meta = {
            "instances_count": len(sources),
            "selected_by": "latest_movement_or_timestamp",
            "selected_index": selected_index,
            "instances": [self._summarize_instance(s) for s in sources],
        }
        return selected, meta

    async def _search_index(self, alias: str, clean_number: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/{alias}/_search"
        logger.info(f"Requesting DataJud API: {alias}/_search for process {clean_number}")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"APIKey {self.api_key}"

        payload = {
            "query": {"match": {"numeroProcesso": clean_number}},
            "size": 50,
        }

        async def _post(trust_env: bool) -> httpx.Response:
            async with httpx.AsyncClient(trust_env=trust_env) as client:
                return await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=float(self.timeout)
                )

        try:
            response = await _post(trust_env=True)
        except httpx.RequestError as e:
            logger.warning(f"Network error connecting to DataJud with env proxy: {str(e)}")
            response = await _post(trust_env=False)

        try:
            if response.status_code == 404:
                logger.info(f"Process {clean_number} not found in {alias} (404)")
                return []
            if response.status_code == 401:
                logger.error("DataJud API authentication failed (401)")
                raise DataJudAPIException(
                    "Falha na autenticação com DataJud API. Verifique a chave de API."
                )
            if response.status_code == 429:
                logger.error("DataJud API rate limit exceeded (429)")
                raise DataJudAPIException(
                    "Limite de requisições ao DataJud excedido. Tente novamente mais tarde."
                )
            if response.status_code >= 500:
                logger.error(f"DataJud server error {response.status_code}: {response.text[:200]}")
                raise DataJudAPIException(
                    "Serviço DataJud temporariamente indisponível. Tente novamente."
                )
            if response.status_code != 200:
                logger.error(f"DataJud unexpected status {response.status_code}: {response.text[:200]}")
                raise DataJudAPIException(
                    f"Erro ao consultar DataJud (código {response.status_code})"
                )

            try:
                data = response.json()
            except Exception as e:
                logger.error(f"Failed to parse DataJud JSON response: {str(e)}")
                raise DataJudAPIException("Resposta inválida da API DataJud") from e

            hits = data.get("hits", {}).get("hits", [])
            return [h.get("_source", h) for h in hits if isinstance(h, dict)]

        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to DataJud API: {url}")
            raise DataJudAPIException(
                f"Timeout ao consultar DataJud (limite: {self.timeout}s)"
            )
        except httpx.RequestError as e:
            logger.error(f"Network error connecting to DataJud: {str(e)}")
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

    async def get_process(self, process_number: str) -> Optional[Dict[str, Any]]:
        """
        Fetches detailed process data from DataJud API using the correct tribunal index.

        Args:
            process_number: CNJ format process number

        Returns:
            Dict with process data from DataJud API, or None if not found

        Raises:
            InvalidProcessNumberException: If number format is invalid
            DataJudAPIException: If API returns an error
        """
        # Get tribunal alias (validates format)
        try:
            alias = self._get_tribunal_alias(process_number)
        except (InvalidProcessNumberException, DataJudAPIException):
            raise
        except Exception as e:
            raise DataJudAPIException(f"Erro ao determinar tribunal: {str(e)}") from e
        clean_number = "".join(filter(str.isdigit, process_number))
        hits = await self._search_index(alias, clean_number)

        if hits:
            logger.info(f"Process {process_number} found in {alias}")
            selected, meta = self._select_latest_instance(hits)
            if meta:
                selected["__meta__"] = meta
                logger.info(
                    "Multiple instances found for %s (count=%s). Selected most recent.",
                    process_number,
                    meta.get("instances_count"),
                )
            return selected

        logger.info(f"Process {process_number} not found in {alias} (no hits)")
        return None

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
        hits = await self._search_index(alias, clean_number)
        if not hits:
            return None, None

        if len(hits) <= 1 and alias != "api_publica_cnj":
            cnj_hits = await self._search_index("api_publica_cnj", clean_number)
            if cnj_hits:
                hits = self._merge_sources(hits, cnj_hits)

        selected, meta = self._select_latest_instance(hits)
        return selected, meta
