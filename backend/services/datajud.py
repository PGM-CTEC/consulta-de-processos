import httpx
import logging
from typing import Dict, Any, Optional
from config import settings
from exceptions import DataJudAPIException, InvalidProcessNumberException

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

        url = f"{self.base_url}/{alias}/_search"
        logger.info(f"Requesting DataJud API: {alias}/_search for process {process_number}")

        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"APIKey {self.api_key}"

        # CNJ stores number WITHOUT formatting in the index
        clean_number = "".join(filter(str.isdigit, process_number))

        # Elasticsearch query
        payload = {
            "query": {
                "match": {
                    "numeroProcesso": clean_number
                }
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                logger.debug(f"DataJud query payload: {payload}")

                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=float(self.timeout)
                )

                # Handle HTTP errors with specific messages
                if response.status_code == 404:
                    logger.info(f"Process {process_number} not found in {alias} (404)")
                    return None

                elif response.status_code == 401:
                    logger.error("DataJud API authentication failed (401)")
                    raise DataJudAPIException(
                        "Falha na autenticação com DataJud API. Verifique a chave de API."
                    )

                elif response.status_code == 429:
                    logger.error("DataJud API rate limit exceeded (429)")
                    raise DataJudAPIException(
                        "Limite de requisições ao DataJud excedido. Tente novamente mais tarde."
                    )

                elif response.status_code >= 500:
                    logger.error(f"DataJud server error {response.status_code}: {response.text[:200]}")
                    raise DataJudAPIException(
                        "Serviço DataJud temporariamente indisponível. Tente novamente."
                    )

                elif response.status_code != 200:
                    logger.error(f"DataJud unexpected status {response.status_code}: {response.text[:200]}")
                    raise DataJudAPIException(
                        f"Erro ao consultar DataJud (código {response.status_code})"
                    )

                # Parse JSON response
                try:
                    data = response.json()
                except Exception as e:
                    logger.error(f"Failed to parse DataJud JSON response: {str(e)}")
                    raise DataJudAPIException("Resposta inválida da API DataJud") from e

                # Extract data from Elasticsearch response format
                if "hits" in data and "hits" in data["hits"]:
                    hits = data["hits"]["hits"]
                    if len(hits) > 0:
                        logger.info(f"Process {process_number} found in {alias}")
                        return hits[0]["_source"]

                # No results found
                logger.info(f"Process {process_number} not found in {alias} (no hits)")
                return None

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
                # Re-raise our custom exceptions
                raise

            except Exception as e:
                # Catch any unexpected errors
                logger.exception(f"Unexpected error querying DataJud: {type(e).__name__}")
                raise DataJudAPIException(
                    "Erro inesperado ao consultar DataJud"
                ) from e
