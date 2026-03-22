"""
Classificação Hierárquica de Fases Processuais
===============================================
Módulo compartilhado que define os tipos e utilidades para a classificação
hierárquica em 3 campos: Stage, Substage, Transit.

Usado por: classification_rules.py, document_phase_classifier.py, phase_analyzer.py
"""

from dataclasses import dataclass
from typing import Optional, Dict, List


# ============================================================
# Constantes: Stages e Substages
# ============================================================

class Stage:
    CONHECIMENTO = 1
    EXECUCAO = 2
    SUSPENSAO = 3
    ARQUIVAMENTO = 4
    CONVERSAO = 5

    LABELS = {
        1: "Conhecimento",
        2: "Execução",
        3: "Suspensão / Sobrestamento",
        4: "Arquivamento",
        5: "Conversão em Renda",
    }


class Substage:
    # Conhecimento
    ANTES_SENTENCA = "1.1"
    SENTENCA_PROFERIDA = "1.2"
    PENDENTE_TRIBUNAL_LOCAL = "1.3"
    JULGAMENTO_TRIBUNAL_LOCAL = "1.4"
    PENDENTE_TRIBUNAL_SUPERIOR = "1.5"
    JULGAMENTO_TRIBUNAL_SUPERIOR = "1.6"

    # Execução
    EXECUCAO_NORMAL = "2.1"
    EXECUCAO_SUSPENSA_PARCIAL = "2.2"
    EXECUCAO_SUSPENSA_TOTAL = "2.3"

    LABELS = {
        "1.1": "Antes da Sentença",
        "1.2": "Sentença Proferida",
        "1.3": "Pendente Julgamento Tribunal Local",
        "1.4": "Julgamento no Tribunal (Monocrático ou Acórdão)",
        "1.5": "Pendente Julgamento Tribunal Superior",
        "1.6": "Julgamento no Tribunal Superior (Monocrático ou Acórdão)",
        "2.1": "Execução Normal",
        "2.2": "Execução Suspensa Parcialmente",
        "2.3": "Execução Suspensa",
    }


class Transit:
    SIM = "sim"
    NAO = "nao"
    NA = "na"  # Não se aplica (ex: execução fiscal)


# ============================================================
# Dataclass: resultado hierárquico
# ============================================================

@dataclass
class HierarchicalResult:
    """Resultado da classificação hierárquica em 3 campos."""
    stage: int
    substage: Optional[str]
    transit_julgado: str
    phase_legacy: str  # "01"-"15" derivado para compatibilidade

    rules_applied: List[str] = None
    confidence: float = 0.0

    def __post_init__(self):
        if self.rules_applied is None:
            self.rules_applied = []

    def to_dict(self) -> Dict:
        return {
            "stage": self.stage,
            "stage_label": Stage.LABELS.get(self.stage),
            "substage": self.substage,
            "substage_label": Substage.LABELS.get(self.substage),
            "transit_julgado": self.transit_julgado,
            "phase_legacy": self.phase_legacy,
            "confidence": self.confidence,
            "rules_applied": self.rules_applied,
        }


# ============================================================
# Derivação: (stage, substage, transit) → phase legacy "01"-"15"
# ============================================================

_LEGACY_MAP = {
    # (stage, substage, transit) → phase code
    # Conhecimento
    (1, "1.1", "nao"): "01",
    (1, "1.1", "sim"): "03",  # Antes da sentença mas com trânsito → trânsito prevalece
    (1, "1.1", "na"):  "01",
    (1, "1.2", "nao"): "02",
    (1, "1.2", "sim"): "03",
    (1, "1.2", "na"):  "02",
    (1, "1.3", "nao"): "04",
    (1, "1.3", "sim"): "06",  # Pendente tribunal local + trânsito → transitado 2ª inst
    (1, "1.3", "na"):  "04",
    (1, "1.4", "nao"): "05",
    (1, "1.4", "sim"): "06",
    (1, "1.4", "na"):  "05",
    (1, "1.5", "nao"): "07",
    (1, "1.5", "sim"): "09",  # Pendente tribunal superior + trânsito
    (1, "1.5", "na"):  "07",
    (1, "1.6", "nao"): "08",
    (1, "1.6", "sim"): "09",
    (1, "1.6", "na"):  "08",
    # Execução
    (2, "2.1", "sim"): "10",
    (2, "2.1", "nao"): "10",
    (2, "2.1", "na"):  "10",
    (2, "2.2", "sim"): "12",
    (2, "2.2", "nao"): "12",
    (2, "2.2", "na"):  "12",
    (2, "2.3", "sim"): "11",
    (2, "2.3", "nao"): "11",
    (2, "2.3", "na"):  "11",
    # Suspensão (substage=None → use None as key)
    (3, None, "sim"):  "13",
    (3, None, "nao"):  "13",
    (3, None, "na"):   "13",
    # Arquivamento
    (4, None, "sim"):  "15",
    (4, None, "nao"):  "15",
    (4, None, "na"):   "15",
    # Conversão
    (5, None, "sim"):  "14",
    (5, None, "nao"):  "14",
    (5, None, "na"):   "14",
}


def derive_legacy_phase(stage: int, substage: Optional[str], transit: str) -> str:
    """Converte (stage, substage, transit) → código de fase legacy "01"-"15"."""
    key = (stage, substage, transit)
    result = _LEGACY_MAP.get(key)
    if result:
        return result

    # Fallback: tentar sem transit específico
    for t in ("nao", "sim", "na"):
        fallback_key = (stage, substage, t)
        result = _LEGACY_MAP.get(fallback_key)
        if result:
            return result

    return "01"  # Fallback absoluto


# ============================================================
# Classes processuais: detecção de tipo para Campo 3 (Transit)
# ============================================================

# Códigos CNJ de classes que são execução originária (sem fase de conhecimento)
CLASSES_EXECUCAO_ORIGINARIA = {
    1116,   # Execução Fiscal
    159,    # Execução de Título Extrajudicial
}

# Códigos CNJ de classes de cumprimento de sentença (indica trânsito)
CLASSES_CUMPRIMENTO_SENTENCA = {
    156,    # Cumprimento de Sentença
    12078,  # Cumprimento de Sentença contra Fazenda Pública
    1727,   # Cumprimento de Sentença (Juizado)
}

# Termos para detecção textual de cumprimento provisório
TERMOS_CUMPRIMENTO_PROVISORIO = [
    "cumprimento provisorio",
    "cumprimento provisório",
]


def detect_transit_from_class(classe_codigo: int, classe_descricao: str) -> Optional[str]:
    """
    Detecta trânsito em julgado a partir da classe processual.

    Retorna:
    - "na" se execução originária (fiscal/título extrajudicial)
    - "sim" se cumprimento de sentença (não provisório)
    - None se não determinável pela classe (requer análise de movimentos)
    """
    # Execução originária → não há fase de conhecimento
    if classe_codigo in CLASSES_EXECUCAO_ORIGINARIA:
        return Transit.NA

    # Cumprimento de sentença → trânsito (exceto provisório)
    if classe_codigo in CLASSES_CUMPRIMENTO_SENTENCA:
        desc_norm = classe_descricao.lower() if classe_descricao else ""
        for termo in TERMOS_CUMPRIMENTO_PROVISORIO:
            if termo in desc_norm:
                return None  # Provisório: não implica trânsito
        return Transit.SIM

    return None  # Não determinável pela classe


# ============================================================
# Mapeamento: phase legacy → (stage, substage)
# ============================================================

PHASE_TO_STAGE_SUBSTAGE = {
    "01": (Stage.CONHECIMENTO, Substage.ANTES_SENTENCA),
    "02": (Stage.CONHECIMENTO, Substage.SENTENCA_PROFERIDA),
    "03": (Stage.CONHECIMENTO, Substage.SENTENCA_PROFERIDA),       # transit=sim
    "04": (Stage.CONHECIMENTO, Substage.PENDENTE_TRIBUNAL_LOCAL),
    "05": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_LOCAL),
    "06": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_LOCAL), # transit=sim
    "07": (Stage.CONHECIMENTO, Substage.PENDENTE_TRIBUNAL_SUPERIOR),
    "08": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_SUPERIOR),
    "09": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_SUPERIOR), # transit=sim
    "10": (Stage.EXECUCAO, Substage.EXECUCAO_NORMAL),
    "11": (Stage.EXECUCAO, Substage.EXECUCAO_SUSPENSA_TOTAL),
    "12": (Stage.EXECUCAO, Substage.EXECUCAO_SUSPENSA_PARCIAL),
    "13": (Stage.SUSPENSAO, None),
    "14": (Stage.CONVERSAO, None),
    "15": (Stage.ARQUIVAMENTO, None),
}


# Fases que implicam trânsito em julgado pelo próprio código
_PHASES_WITH_IMPLICIT_TRANSIT = {"03", "06", "09"}


def detect_transit_from_class_text(classe_norm: str) -> Optional[str]:
    """
    Detecta trânsito a partir da descrição textual normalizada da classe processual.
    Usado pelo DocumentPhaseClassifier que não tem código numérico da classe.

    Retorna:
    - "na" se execução originária
    - "sim" se cumprimento de sentença (não provisório)
    - None se não determinável
    """
    if classe_norm.startswith("execucao fiscal") or classe_norm.startswith("execucao de titulo extrajudicial"):
        return Transit.NA
    if classe_norm.startswith("cumprimento provisorio"):
        return None  # Provisório: não implica trânsito
    if classe_norm.startswith("cumprimento"):
        return Transit.SIM
    return None
