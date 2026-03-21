"""
FusionAPIClient — consome a API REST do PAV/Fusion para obter
lista completa de movimentos (com ou sem documentos anexados) de um processo por número CNJ.

Endpoint:
GET {base_url}/services/custom-consulta-rapida-de-procesos/dados-da-consulta/{numero_cnj_sem_formatacao}

Estrutura da resposta:
{
  "dadosPAV": {
    "neoId": 950453990,
    "wfProcessNeoId": 950453990,
    "situacao": "Ativo"
  },
  "dadosGerais": {
    "numeroJudicial": "00754816320208190001",
    "classeProcessual": "Cumprimento de sentença",
    "orgaoJulgador": "Cartório da 3ª Vara da Fazenda Pública",
    "descricaoSistema": "TJRJ_DCP"
  },
  "movimentos": [
    {
      "dataDoMovimento": "08/04/2020 15:59",
      "tipoMovimentoCNJ": "Distribuição",
      "tipoMovimentoLocal": "DISTRIBUIÇÃO Sorteio",
      "documentos": ["783447489", ...]
    },
    ...
  ],
  "urlConsultaAutos": "http://...",
  "encontradoTribunal": true,
  "uuid": "..."
}
"""
import json
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


@dataclass
class PAVArvoreResult:
    numero_cnj: str
    movimentos: list          # List[FusionMovimento], ordenado ASC por data
    tribunais: list           # Raw tribunal data para contexto/debug
    data_consulta: datetime = None

    def __post_init__(self):
        if self.data_consulta is None:
            self.data_consulta = datetime.utcnow()


class FusionAPIClient:
    """
    Cliente HTTP para a API REST do PAV.
    Requer cookie de sessão JSESSIONID configurado.
    """

    _ENDPOINT = "/services/custom-consulta-rapida-de-procesos/dados-da-consulta/{cnj}"
    _ARVORE_ENDPOINT = "/services/arquivos/arvore-processo-by-sistema/{cnj}"

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
        Usa o endpoint arvore-processo-by-sistema com CNJ dummy — apenas para
        checar autenticação e resetar o timeout de inatividade do servidor.

        Returns:
            (is_alive: bool, status_code: int)
        """
        if not self._session_cookie:
            return False, 0

        url = self._base_url + self._ENDPOINT.format(cnj="00000000000000000000")
        try:
            response = await self._http.get(url)
            # 401/403 = sessão inválida/expirada.
            # Qualquer outro status (200, 404, 400…) = sessão ativa,
            # pois o endpoint pode retornar não-2xx para CNJ dummy mesmo com sessão válida.
            alive = response.status_code not in (401, 403)
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

        # PAV envia UTF-8 na maioria dos casos; fallback para ISO-8859-1 em dados legados
        try:
            raw_text = response.content.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = response.content.decode("iso-8859-1")
        data = json.loads(raw_text)

        if not data.get("encontradoTribunal", False):
            logger.info(f"Processo {cnj_digits} não encontrado no PAV (encontradoTribunal=false)")
            return None

        return self._parse(data, numero_cnj)

    def _parse(self, data: dict, numero_cnj: str) -> FusionResult:
        """Converte resposta JSON do PAV (dados-da-consulta) em FusionResult."""
        dados_gerais = data.get("dadosGerais", {})
        dados_pav = data.get("dadosPAV", {})

        movimentos = []
        for m in data.get("movimentos", []):
            try:
                movimentos.append(FusionMovimento(
                    data=_parse_date(m.get("dataDoMovimento", "")),
                    tipo_local=m.get("tipoMovimentoLocal", ""),
                    tipo_cnj=m.get("tipoMovimentoCNJ", ""),
                    descricao=m.get("descricao", ""),
                ))
            except Exception as e:
                logger.warning(f"Erro ao parsear movimento {m}: {e}")

        # Ordenar ASC por data
        movimentos.sort(key=lambda m: m.data)

        return FusionResult(
            numero_cnj=numero_cnj,
            neo_id=dados_pav.get("wfProcessNeoId"),
            classe_processual=dados_gerais.get("classeProcessual", ""),
            sistema=dados_gerais.get("descricaoSistema", ""),
            movimentos=movimentos,
            fonte="fusion_api",
        )

    async def get_arvore_processo(self, numero_cnj: str) -> Optional[PAVArvoreResult]:
        """
        Busca a árvore de documentos do processo no PAV.

        Retorna PAVArvoreResult com todos os documentos da árvore convertidos em
        FusionMovimento (nomeArquivo → tipo_local), prontos para classificação.
        Retorna None se o endpoint falhar ou não retornar documentos.

        Ordenação:
          - DCP (TJRJ-DCP): por numeroFolha (int) ASC
          - Demais: por id (int) ASC
        """
        cnj_digits = re.sub(r"\D", "", numero_cnj)
        url = self._base_url + self._ARVORE_ENDPOINT.format(cnj=cnj_digits)

        try:
            response = await self._http.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.warning(f"PAV árvore HTTP error for {cnj_digits}: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.warning(f"PAV árvore request error for {cnj_digits}: {e}")
            return None

        try:
            raw_text = response.content.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = response.content.decode("iso-8859-1")

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.warning(f"PAV árvore JSON decode error for {cnj_digits}: {e}")
            return None

        tribunais = data.get("tribunal") or []
        if not tribunais:
            logger.info(f"PAV árvore: nenhum tribunal retornado para {cnj_digits}")
            return None

        movimentos: list = []
        for tribunal in tribunais:
            destino = (tribunal.get("destino") or "").upper()
            is_dcp = "DCP" in destino
            documentos = tribunal.get("documentos") or []

            # Ordenar dentro do tribunal antes de converter
            if is_dcp:
                documentos = sorted(
                    documentos,
                    key=lambda d: int(d.get("numeroFolha") or 0),
                )
            else:
                documentos = sorted(
                    documentos,
                    key=lambda d: int(d.get("id") or 0),
                )

            for doc in documentos:
                nome = doc.get("nomeArquivo") or ""
                data_aut = doc.get("dataAutuacao") or ""
                tipo = str(doc.get("tipo") or "")
                if not nome and not data_aut:
                    continue
                try:
                    movimentos.append(FusionMovimento(
                        data=_parse_date(data_aut) if data_aut else None,
                        tipo_local=nome,
                        tipo_cnj=tipo,
                        descricao="",
                    ))
                except Exception as e:
                    logger.warning(f"PAV árvore: erro ao parsear documento {doc}: {e}")

        # Filtrar movimentos sem data e re-ordenar por data ASC global
        movimentos = [m for m in movimentos if m.data is not None]
        movimentos.sort(key=lambda m: m.data)

        if not movimentos:
            logger.info(f"PAV árvore: nenhum documento válido para {cnj_digits}")
            return None

        logger.info(f"PAV árvore: {len(movimentos)} documentos carregados para {cnj_digits}")
        return PAVArvoreResult(
            numero_cnj=numero_cnj,
            movimentos=movimentos,
            tribunais=tribunais,
        )

    async def aclose(self):
        await self._http.aclose()
