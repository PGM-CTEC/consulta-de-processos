"""
DocumentPhaseClassifier — classifica fase processual a partir dos batismos
de peças do Fusion/PAV (tipoMovimentoLocal).

Usa lógica de âncoras em ordem cronológica decrescente.
Trânsito em Julgado: somente com documento explícito (certidão ou peça nomeada).
Sentença: somente para peças nomeadas exclusivamente como sentença.
'Despacho / Sentença / Decisão' é ignorado (nome genérico do DCP).
"""
import unicodedata
import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FusionMovimento:
    data: datetime
    tipo_local: str   # "batismo" — principal âncora de classificação
    tipo_cnj: str     # código CNJ (referência)


# ---------------------------------------------------------------------------
# Anchor patterns (after normalization)
# ---------------------------------------------------------------------------

# Fase 15 — Arquivado Definitivamente
_ANCHOR_ARQUIVAMENTO = re.compile(r'\barquivamento\b')

# Fase 03 — Trânsito em Julgado (somente documento explícito)
_ANCHOR_TRANSITO = re.compile(
    r'(certidao\s+de\s+transito\s+em\s+julgado|transito\s+em\s+julgado)'
)

# Fase 02 / 03 — Sentença pura (NÃO "despacho / sentenca / decisao")
# Aceita: "Sentença", "Sentença de Mérito", "Sentença Homologatória", "Sentença Parcial"
# Rejeita: "Despacho / Sentença / Decisão"
_ANCHOR_SENTENCA = re.compile(r'^sentenca(\s+(de\s+merito|homologatoria|parcial|condenatoria|declaratoria|constitutiva))?$')

# Fase 04+ — Remessa / recurso para instância superior
_ANCHOR_REMESSA = re.compile(r'(remessa\b|declinio\s+de\s+competencia|redistribuicao)')

# Fase 13 — Suspenso/Sobrestado
_ANCHOR_SUSPENSO = re.compile(r'(suspensao|sobrestamento|processo\s+suspenso)')

# Classes processuais que indicam execução (fases 10-12, 14)
_CLASSES_EXECUCAO = {
    "cumprimento de sentenca",
    "cumprimento provisorio de sentenca",
    "execucao fiscal",
    "execucao de titulo extrajudicial",
    "execucao",
    "execucao por quantia certa",
    "execucao de alimentos",
}


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class DocumentPhaseClassifier:
    """
    Classifica fase processual a partir de movimentos do Fusion/PAV.
    Stateless — todos os métodos são classmethod.
    """

    @classmethod
    def classify(cls, movimentos: List[FusionMovimento], classe_processual: str) -> str:
        """
        Retorna código de fase (string "01"–"15").

        Args:
            movimentos: lista ordenada cronologicamente (ASC por data).
            classe_processual: classe do processo no tribunal.

        Returns:
            Fase processual como string de 2 dígitos.
        """
        classe_norm = cls._normalize(classe_processual)

        # Contexto de execução → branch específico
        if classe_norm in _CLASSES_EXECUCAO:
            return cls._classify_execucao(movimentos)

        return cls._classify_conhecimento(movimentos)

    # ------------------------------------------------------------------
    # Branch: conhecimento (fases 01–09, 13, 15)
    # ------------------------------------------------------------------

    @classmethod
    def _classify_conhecimento(cls, movimentos: List[FusionMovimento]) -> str:
        if not movimentos:
            return "01"

        # Percorre do mais recente para o mais antigo
        ordered = sorted(movimentos, key=lambda m: m.data, reverse=True)
        nomes = [cls._normalize(m.tipo_local) for m in ordered]

        # P1: Arquivamento
        for nome in nomes:
            if _ANCHOR_ARQUIVAMENTO.search(nome):
                return "15"

        # P2: Trânsito em Julgado (explícito)
        transito_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_TRANSITO.search(n)), None
        )

        # P3: Sentença pura
        sentenca_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_SENTENCA.match(n)), None
        )

        if transito_idx is not None:
            # Trânsito encontrado
            if sentenca_idx is not None:
                # Sentença também existe → fase 03
                return "03"
            # Trânsito sem sentença explícita → fase 03 (documento independente)
            return "03"

        if sentenca_idx is not None:
            # Sentença sem trânsito → fase 02
            return "02"

        # P5: Suspensão
        for nome in nomes:
            if _ANCHOR_SUSPENSO.search(nome):
                return "13"

        # Fallback conservador: antes da sentença
        return "01"

    # ------------------------------------------------------------------
    # Branch: execução (fases 10–12, 14, 15)
    # ------------------------------------------------------------------

    @classmethod
    def _classify_execucao(cls, movimentos: List[FusionMovimento]) -> str:
        if not movimentos:
            return "10"

        ordered = sorted(movimentos, key=lambda m: m.data, reverse=True)
        nomes = [cls._normalize(m.tipo_local) for m in ordered]

        # Arquivamento também termina execução
        for nome in nomes:
            if _ANCHOR_ARQUIVAMENTO.search(nome):
                return "15"

        # Suspensão de execução
        for nome in nomes:
            if _ANCHOR_SUSPENSO.search(nome):
                return "11"

        return "10"

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    @classmethod
    def _normalize(cls, texto: str) -> str:
        """Remove acentos, converte para minúsculas, normaliza espaços."""
        if not texto:
            return ""
        # Remove acentos via NFD decomposition
        nfkd = unicodedata.normalize("NFKD", texto)
        ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
        # Lowercase, strip, normalizar espaços múltiplos
        return re.sub(r'\s+', ' ', ascii_text.lower().strip())
