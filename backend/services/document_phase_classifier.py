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
from typing import List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FusionMovimento:
    data: datetime
    tipo_local: str   # "batismo" — principal âncora de classificação
    tipo_cnj: str     # código CNJ (referência)


@dataclass
class ClassificationResult:
    """Resultado estruturado da classificação de fase, com trace de decisão."""
    phase: str                                    # "01"–"15" ou "Indefinido"
    branch: str                                   # "conhecimento" | "execucao"
    classe_normalizada: str                       # classe processual normalizada
    total_movimentos: int                         # total de movimentos analisados
    rule_applied: str                             # regra que disparou (ex: "P2_transito_em_julgado")
    decisive_movement: Optional[str] = None       # tipo_local do movimento decisivo
    decisive_movement_date: Optional[str] = None  # ISO date do movimento decisivo
    anchor_matches: dict = field(default_factory=dict)
    # anchor_matches: posição na lista DESC de cada âncora, ou None

    def to_dict(self) -> dict:
        """Retorna dict serializável para JSON."""
        return {
            "phase": self.phase,
            "branch": self.branch,
            "classe_normalizada": self.classe_normalizada,
            "total_movimentos": self.total_movimentos,
            "rule_applied": self.rule_applied,
            "decisive_movement": self.decisive_movement,
            "decisive_movement_date": self.decisive_movement_date,
            "anchor_matches": self.anchor_matches,
        }


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
# Aceita: "Sentença", "Sentença de Mérito", "Minutar Sentença", "Sentença Parcial", etc.
# Rejeita: "Despacho / Sentença / Decisão" (nome genérico do DCP)
_ANCHOR_SENTENCA = re.compile(
    r'^(minutar\s+)?sentenca(\s+(de\s+merito|homologatoria|parcial|condenatoria|declaratoria|constitutiva))?$'
)

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
        return cls.classify_with_trace(movimentos, classe_processual).phase

    @classmethod
    def classify_with_trace(
        cls, movimentos: List[FusionMovimento], classe_processual: str
    ) -> ClassificationResult:
        """
        Classifica fase processual e retorna trace completo da decisão.

        Args:
            movimentos: lista ordenada cronologicamente (ASC por data).
            classe_processual: classe do processo no tribunal.

        Returns:
            ClassificationResult com fase, regra aplicada, movimento decisivo, etc.
        """
        classe_norm = cls._normalize(classe_processual)

        if classe_norm in _CLASSES_EXECUCAO:
            return cls._classify_execucao_traced(movimentos, classe_norm)

        return cls._classify_conhecimento_traced(movimentos, classe_norm)

    # ------------------------------------------------------------------
    # Branch: conhecimento (fases 01–09, 13, 15)
    # ------------------------------------------------------------------

    @classmethod
    def _classify_conhecimento_traced(
        cls, movimentos: List[FusionMovimento], classe_norm: str
    ) -> ClassificationResult:
        if not movimentos:
            return ClassificationResult(
                phase="01", branch="conhecimento", classe_normalizada=classe_norm,
                total_movimentos=0, rule_applied="empty_list_fallback",
                anchor_matches={},
            )

        # Percorre do mais recente para o mais antigo
        ordered = sorted(movimentos, key=lambda m: m.data, reverse=True)
        nomes = [cls._normalize(m.tipo_local) for m in ordered]

        # Escaneia todas as âncoras de uma vez
        arq_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_ARQUIVAMENTO.search(n)), None
        )
        transito_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_TRANSITO.search(n)), None
        )
        sentenca_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_SENTENCA.match(n)), None
        )
        remessa_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_REMESSA.search(n)), None
        )
        suspenso_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_SUSPENSO.search(n)), None
        )

        anchors = {
            "arquivamento": arq_idx,
            "transito": transito_idx,
            "sentenca": sentenca_idx,
            "remessa": remessa_idx,
            "suspenso": suspenso_idx,
        }

        def _decisive(idx):
            """Retorna (tipo_local original, ISO date) do movimento na posição idx."""
            if idx is None:
                return None, None
            return ordered[idx].tipo_local, ordered[idx].data.isoformat()

        total = len(movimentos)

        # P1: Arquivamento
        if arq_idx is not None:
            nome, data = _decisive(arq_idx)
            return ClassificationResult(
                "15", "conhecimento", classe_norm, total,
                "P1_arquivamento", nome, data, anchors,
            )

        # P2: Trânsito em Julgado (explícito)
        if transito_idx is not None:
            nome, data = _decisive(transito_idx)
            return ClassificationResult(
                "03", "conhecimento", classe_norm, total,
                "P2_transito_em_julgado", nome, data, anchors,
            )

        # P3: Sentença
        if sentenca_idx is not None:
            # Se há remessa mais recente que a sentença (índice menor = mais recente),
            # o processo foi remetido à instância superior após a sentença → fase 04
            if remessa_idx is not None and remessa_idx < sentenca_idx:
                nome, data = _decisive(remessa_idx)
                return ClassificationResult(
                    "04", "conhecimento", classe_norm, total,
                    "P3_sentenca_com_remessa_posterior", nome, data, anchors,
                )
            # Sentença sem remessa posterior nem trânsito → fase 02
            nome, data = _decisive(sentenca_idx)
            return ClassificationResult(
                "02", "conhecimento", classe_norm, total,
                "P3_sentenca_sem_transito", nome, data, anchors,
            )

        # P4: Remessa sem sentença prévia
        if remessa_idx is not None:
            nome, data = _decisive(remessa_idx)
            return ClassificationResult(
                "04", "conhecimento", classe_norm, total,
                "P4_remessa_sem_sentenca", nome, data, anchors,
            )

        # P5: Suspensão
        if suspenso_idx is not None:
            nome, data = _decisive(suspenso_idx)
            return ClassificationResult(
                "13", "conhecimento", classe_norm, total,
                "P5_suspensao", nome, data, anchors,
            )

        # Fallback conservador: antes da sentença
        return ClassificationResult(
            "01", "conhecimento", classe_norm, total,
            "P6_fallback_antes_sentenca", None, None, anchors,
        )

    # ------------------------------------------------------------------
    # Branch: execução (fases 10–12, 14, 15)
    # ------------------------------------------------------------------

    @classmethod
    def _classify_execucao_traced(
        cls, movimentos: List[FusionMovimento], classe_norm: str
    ) -> ClassificationResult:
        if not movimentos:
            return ClassificationResult(
                phase="10", branch="execucao", classe_normalizada=classe_norm,
                total_movimentos=0, rule_applied="empty_list_fallback",
                anchor_matches={},
            )

        ordered = sorted(movimentos, key=lambda m: m.data, reverse=True)
        nomes = [cls._normalize(m.tipo_local) for m in ordered]

        arq_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_ARQUIVAMENTO.search(n)), None
        )
        suspenso_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_SUSPENSO.search(n)), None
        )

        anchors = {
            "arquivamento": arq_idx,
            "suspenso": suspenso_idx,
        }

        def _decisive(idx):
            if idx is None:
                return None, None
            return ordered[idx].tipo_local, ordered[idx].data.isoformat()

        total = len(movimentos)

        # E1: Arquivamento também termina execução
        if arq_idx is not None:
            nome, data = _decisive(arq_idx)
            return ClassificationResult(
                "15", "execucao", classe_norm, total,
                "E1_arquivamento", nome, data, anchors,
            )

        # E2: Suspensão de execução
        if suspenso_idx is not None:
            nome, data = _decisive(suspenso_idx)
            return ClassificationResult(
                "11", "execucao", classe_norm, total,
                "E2_suspensao", nome, data, anchors,
            )

        # Fallback: execução em andamento
        return ClassificationResult(
            "10", "execucao", classe_norm, total,
            "E3_fallback", None, None, anchors,
        )

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
