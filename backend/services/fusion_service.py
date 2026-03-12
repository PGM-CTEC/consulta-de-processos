"""
FusionService — orquestra o acesso ao Fusion/PAV.

Tenta SQL Server direto primeiro (se configurado),
usa API REST PAV como fallback.
"""
import logging
from typing import Optional

from .fusion_sql_client import FusionSQLClient, FusionSQLException
from .fusion_api_client import FusionAPIClient, FusionResult

logger = logging.getLogger(__name__)


class FusionService:
    """
    Orquestrador dual-source para consulta ao Fusion/PAV.

    Priority:
      1. SQL Server direto (se is_available())
      2. API REST PAV (fallback)
    """

    def __init__(
        self,
        sql_client: Optional[FusionSQLClient],
        api_client: FusionAPIClient,
    ):
        self._sql = sql_client
        self._api = api_client

    async def get_document_tree(self, numero_cnj: str) -> Optional[FusionResult]:
        """
        Busca movimentos do processo no Fusion.

        Args:
            numero_cnj: número CNJ (com ou sem formatação).

        Returns:
            FusionResult ou None se não encontrado em nenhuma fonte.
        """
        # Via 1: SQL Server direto
        if self._sql and self._sql.is_available():
            try:
                result = await self._sql.get_document_tree(numero_cnj)
                if result is not None:
                    logger.info(f"Fusion SQL: processo {numero_cnj} encontrado")
                    return result
            except FusionSQLException as e:
                logger.warning(
                    f"Fusion SQL falhou para {numero_cnj}, usando API REST: {e}"
                )

        # Via 2: API REST PAV
        try:
            result = await self._api.get_document_tree(numero_cnj)
            if result is not None:
                logger.info(f"Fusion API: processo {numero_cnj} encontrado")
            else:
                logger.info(f"Fusion API: processo {numero_cnj} não encontrado")
            return result
        except Exception as e:
            logger.error(f"Fusion API erro para {numero_cnj}: {e}")
            return None

    async def get_process_complete(self, numero_cnj: str) -> Optional[dict]:
        """
        Busca dados COMPLETOS do processo via novo endpoint PAV consolidado.

        Este método usa o endpoint /services/custom-consulta-rapida-de-procesos/dados-da-consulta
        que retorna tudo: dados cadastrais, movimentos, partes, etc. em um único JSON.

        Args:
            numero_cnj: número CNJ (com ou sem formatação).

        Returns:
            dict completo do PAV ou None se não encontrado.

        Raises:
            Exception: Se houver erro de rede/timeout/API.
        """
        try:
            result = await self._api.get_process_complete(numero_cnj)
            if result is not None:
                logger.info(f"PAV completo: processo {numero_cnj} encontrado")
            else:
                logger.info(f"PAV completo: processo {numero_cnj} não encontrado")
            return result
        except Exception as e:
            logger.error(f"PAV API erro para {numero_cnj}: {e}")
            raise
