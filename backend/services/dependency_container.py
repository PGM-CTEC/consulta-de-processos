"""
Dependency Container for ProcessService and related components.

This module provides a simple DI container for managing service dependencies.
Enables:
- Easy testing with mock implementations
- Loose coupling between services
- Clear dependency declaration
"""

import logging
import pathlib
from typing import Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Arquivo de persistência local do cookie PAV (git-ignorado).
# Salvo na raiz do projeto (onde o servidor é iniciado).
_PAV_SESSION_FILE = pathlib.Path(".pav_session")


def _load_persisted_cookie() -> str:
    """Carrega o cookie PAV salvo no arquivo local, se existir."""
    try:
        if _PAV_SESSION_FILE.exists():
            cookie = _PAV_SESSION_FILE.read_text(encoding="utf-8").strip()
            if cookie and "JSESSIONID" in cookie:
                logger.info(f"Cookie PAV carregado do arquivo ({cookie[-8:]})")
                return cookie
    except Exception as e:
        logger.warning(f"Não foi possível carregar cookie PAV salvo: {e}")
    return ""


def _persist_cookie(cookie: str) -> None:
    """Salva o cookie PAV no arquivo local para sobreviver reinícios."""
    try:
        _PAV_SESSION_FILE.write_text(cookie, encoding="utf-8")
        logger.info(f"Cookie PAV persistido em {_PAV_SESSION_FILE}")
    except Exception as e:
        logger.warning(f"Não foi possível persistir cookie PAV: {e}")

from .datajud import DataJudClient
from .phase_analyzer import PhaseAnalyzer
from .process_service import ProcessService
from .fusion_api_client import FusionAPIClient
from .fusion_sql_client import FusionSQLClient
from .fusion_service import FusionService
from ..config import settings


class ServiceContainer:
    """
    Simple dependency container for service initialization.

    Usage:
        # Production
        container = ServiceContainer(db_session)
        process_service = container.process_service()

        # Testing with mocks
        container = ServiceContainer(
            db_session,
            client=mock_client,
            phase_analyzer=mock_analyzer
        )
        process_service = container.process_service()
    """

    def __init__(
        self,
        db: Session,
        client: Optional[DataJudClient] = None,
        phase_analyzer: Optional[PhaseAnalyzer] = None,
    ):
        """
        Initialize the service container with dependencies.

        Args:
            db: SQLAlchemy database session
            client: DataJudClient instance (optional)
            phase_analyzer: PhaseAnalyzer instance (optional)
        """
        self.db = db
        self._client = client
        self._phase_analyzer = phase_analyzer

    def datajud_client(self) -> DataJudClient:
        """Get or create DataJudClient."""
        if self._client is None:
            self._client = DataJudClient()
        return self._client

    def phase_analyzer(self) -> PhaseAnalyzer:
        """Get or create PhaseAnalyzer."""
        if self._phase_analyzer is None:
            self._phase_analyzer = PhaseAnalyzer
        return self._phase_analyzer

    def process_service(self) -> ProcessService:
        """Get ProcessService with all dependencies injected."""
        return ProcessService(
            db=self.db,
            client=self.datajud_client(),
            phase_analyzer=self.phase_analyzer(),
        )


def create_process_service(
    db: Session,
    client: Optional[DataJudClient] = None,
    phase_analyzer: Optional[PhaseAnalyzer] = None,
) -> ProcessService:
    """
    Factory function to create ProcessService with optional dependencies.

    This is a simpler alternative to ServiceContainer for single-service creation.

    Args:
        db: SQLAlchemy database session
        client: DataJudClient instance (optional, defaults to DataJudClient())
        phase_analyzer: PhaseAnalyzer instance (optional, defaults to PhaseAnalyzer)

    Returns:
        ProcessService instance with all dependencies injected

    Example:
        # Production
        service = create_process_service(db)

        # Testing
        service = create_process_service(db, client=mock_client)
    """
    return ProcessService(
        db=db,
        client=client or DataJudClient(),
        phase_analyzer=phase_analyzer or PhaseAnalyzer,
    )


_fusion_service_singleton: Optional[FusionService] = None
_fusion_api_client_singleton: Optional[FusionAPIClient] = None


def _create_fusion_service() -> tuple[FusionService, FusionAPIClient]:
    """Cria instâncias de FusionService e FusionAPIClient.
    Prioridade do cookie: arquivo .pav_session > variável de ambiente."""
    # Carrega cookie persistido (sobrevive reinícios); fallback para .env
    cookie = _load_persisted_cookie() or settings.FUSION_PAV_SESSION_COOKIE
    api_client = FusionAPIClient(
        base_url=settings.FUSION_PAV_BASE_URL,
        session_cookie=cookie,
        timeout=settings.FUSION_PAV_TIMEOUT,
    )
    sql_client = None
    if settings.fusion_sql_configured:
        sql_client = FusionSQLClient(
            host=settings.FUSION_SQL_HOST,
            port=settings.FUSION_SQL_PORT,
            database=settings.FUSION_SQL_DATABASE,
            user=settings.FUSION_SQL_USER,
            password=settings.FUSION_SQL_PASSWORD,
        )
    return FusionService(sql_client=sql_client, api_client=api_client), api_client


def get_fusion_service() -> FusionService:
    """
    Retorna o singleton FusionService.
    Na primeira chamada, cria e armazena a instância.
    Garante que update_cookie() afete todas as requisições subsequentes.
    """
    global _fusion_service_singleton, _fusion_api_client_singleton
    if _fusion_service_singleton is None:
        _fusion_service_singleton, _fusion_api_client_singleton = _create_fusion_service()
    return _fusion_service_singleton


def get_fusion_api_client() -> Optional[FusionAPIClient]:
    """Retorna o FusionAPIClient singleton (para uso no keepalive e update de cookie)."""
    global _fusion_api_client_singleton
    if _fusion_api_client_singleton is None:
        get_fusion_service()  # inicializa o singleton
    return _fusion_api_client_singleton


def update_fusion_cookie(new_cookie: str) -> None:
    """
    Atualiza o cookie de sessão PAV no singleton em runtime.
    Persiste em arquivo local para sobreviver reinícios do servidor.
    Não requer reinicialização do servidor.
    """
    global _fusion_api_client_singleton
    if _fusion_api_client_singleton is None:
        get_fusion_service()  # inicializa o singleton
    if _fusion_api_client_singleton:
        _fusion_api_client_singleton.update_cookie(new_cookie)
        _persist_cookie(new_cookie)
