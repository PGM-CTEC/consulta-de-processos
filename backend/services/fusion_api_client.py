"""
FusionAPIClient — consome a API REST do PAV/Fusion para obter
árvore de documentos de um processo por número CNJ.

Endpoint descoberto:
GET https://pav.procuradoria.rio/services/custom-consulta-rapida-de-procesos/
    dados-da-consulta/{numero_cnj_sem_formatacao}
"""
import re
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

import httpx

from .document_phase_classifier import FusionMovimento

logger = logging.getLogger(__name__)

_DATE_FMT_SHORT = "%d/%m/%Y %H:%M"
_DATE_FMT_LONG  = "%d/%m/%Y %H:%M:%S"


def _parse_date(valor: str) -> datetime:
    """Tenta parsear data nos formatos curto e longo do PAV."""
    for fmt in (_DATE_FMT_LONG, _DATE_FMT_SHORT):
        try:
            return datetime.strptime(valor.strip(), fmt)
        except ValueError:
            continue
    # Fallback: data mínima para não quebrar a ordenação
    logger.warning(f"Não foi possível parsear data: {valor!r}")
    return datetime.min


@dataclass
class FusionResult:
    numero_cnj: str
    neo_id: Optional[int]
    classe_processual: str
    sistema: str
    movimentos: list          # List[FusionMovimento], ordenado ASC por data
    fonte: str                # "fusion_api" | "fusion_sql"
    data_consulta: datetime = None

    def __post_init__(self):
        if self.data_consulta is None:
            self.data_consulta = datetime.utcnow()


class FusionAPIClient:
    """
    Cliente HTTP para a API REST do PAV.
    Requer cookie de sessão JSESSIONID configurado.
    """

    _ENDPOINT = (
        "/services/custom-consulta-rapida-de-procesos"
        "/dados-da-consulta/{cnj}"
    )

    def __init__(self, base_url: str, session_cookie: str, timeout: int = 30):
        self._base_url = base_url.rstrip("/")
        self._session_cookie = session_cookie
        self._http = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Cookie": session_cookie,
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/plain, */*",
            } if session_cookie else {},
            follow_redirects=True,
        )

    def update_cookie(self, new_cookie: str) -> None:
        """
        Atualiza o cookie de sessão PAV em runtime sem recriar o cliente HTTP.
        Permite renovar a sessão sem reiniciar o servidor.
        """
        self._session_cookie = new_cookie
        self._http.headers["Cookie"] = new_cookie
        logger.info("FusionAPIClient: cookie de sessão PAV atualizado")

    @property
    def session_cookie(self) -> str:
        """Retorna o cookie de sessão atual (para uso no keepalive)."""
        return self._session_cookie

    async def check_session(self) -> tuple[bool, int]:
        """
        Verifica se a sessão PAV está ativa fazendo um ping leve.
        Usa o endpoint dados-da-consulta com CNJ inválido — apenas para
        resetar o timeout de inatividade do servidor.

        Returns:
            (is_alive: bool, status_code: int)
        """
        if not self._session_cookie:
            return False, 0

        url = self._base_url + self._ENDPOINT.format(cnj="00000000000000000000")
        try:
            response = await self._http.get(url)
            alive = response.status_code < 400
            return alive, response.status_code
        except httpx.RequestError as e:
            logger.warning(f"FusionAPIClient.check_session error: {e}")
            return False, -1

    async def get_document_tree(self, numero_cnj: str) -> Optional[FusionResult]:
        """
        Busca árvore de documentos pelo número CNJ.
        Retorna None se o processo não for encontrado no PAV.

        Args:
            numero_cnj: número CNJ (com ou sem formatação).

        Returns:
            FusionResult com movimentos ou None se não encontrado.
        """
        cnj_digits = re.sub(r"\D", "", numero_cnj)
        url = self._base_url + self._ENDPOINT.format(cnj=cnj_digits)

        try:
            response = await self._http.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.warning(f"PAV API HTTP error for {cnj_digits}: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"PAV API request error for {cnj_digits}: {e}")
            raise

        data = response.json()

        if not data.get("encontradoTribunal", False):
            logger.info(f"Processo {cnj_digits} não encontrado no tribunal via PAV")
            return None

        return self._parse(data, numero_cnj)

    def _parse(self, data: dict, numero_cnj: str) -> FusionResult:
        """Converte resposta JSON do PAV em FusionResult."""
        dados_pav = data.get("dadosPAV", {})
        dados_gerais = data.get("dadosGerais", {})

        movimentos = []
        for m in data.get("movimentos", []):
            try:
                movimentos.append(FusionMovimento(
                    data=_parse_date(m.get("dataDoMovimento", "")),
                    tipo_local=m.get("tipoMovimentoLocal", ""),
                    tipo_cnj=m.get("tipoMovimentoCNJ", ""),
                ))
            except Exception as e:
                logger.warning(f"Erro ao parsear movimento {m}: {e}")

        # Ordenar ASC por data
        movimentos.sort(key=lambda m: m.data)

        return FusionResult(
            numero_cnj=numero_cnj,
            neo_id=dados_pav.get("wfProcessNeoId") or dados_pav.get("neoId"),
            classe_processual=dados_gerais.get("classeProcessual", ""),
            sistema=dados_gerais.get("descricaoSistema", ""),
            movimentos=movimentos,
            fonte="fusion_api",
        )

    async def aclose(self):
        await self._http.aclose()
