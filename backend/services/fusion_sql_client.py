"""
FusionSQLClient — acesso direto ao SQL Server do Fusion.

As queries SQL dependem do schema real do banco Fusion e devem ser
validadas com o DBA antes de ativar esta via. Por padrão a via API REST
é usada como fallback.

Requer: pyodbc instalado (`pip install pyodbc`)
"""
import logging
import re
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class FusionSQLException(Exception):
    pass


class FusionSQLClient:
    """
    Cliente SQL Server para acesso direto ao banco do Fusion.
    Stateless — cria conexão por request.
    """

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

    def is_available(self) -> bool:
        """True se todas as credenciais obrigatórias estiverem configuradas."""
        return bool(self._host and self._database and self._user and self._password)

    def _build_connection_string(self) -> str:
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self._host},{self._port};"
            f"DATABASE={self._database};"
            f"UID={self._user};"
            f"PWD={self._password};"
            f"TrustServerCertificate=yes;"
        )

    async def get_document_tree(self, numero_cnj: str):
        """
        Busca árvore de documentos via SQL Server.

        TODO: Queries a serem confirmadas com DBA após verificar schema.
        Estrutura esperada no Fusion:
          - Tabela de processos com campo numeroJudicial (CNJ sem formatação)
          - Tabela de movimentos com tipoMovimentoLocal e dataMovimento

        Raises:
            FusionSQLException: em caso de erro de conexão ou query.
        """
        if not self.is_available():
            raise FusionSQLException("SQL Server não configurado")

        try:
            import pyodbc  # noqa: F401 — importação lazy
        except ImportError:
            raise FusionSQLException(
                "pyodbc não instalado. Execute: pip install pyodbc"
            )

        cnj_digits = re.sub(r"\D", "", numero_cnj)

        # ---------------------------------------------------------------
        # PLACEHOLDER — substituir pelas queries reais após mapeamento
        # do schema do banco Fusion com o DBA
        # ---------------------------------------------------------------
        raise FusionSQLException(
            f"FusionSQLClient: queries SQL ainda não mapeadas para o schema Fusion. "
            f"CNJ: {cnj_digits}. Configure as queries após verificar o schema com o DBA."
        )
