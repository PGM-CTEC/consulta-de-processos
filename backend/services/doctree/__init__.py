"""
Classificação de Fase Processual por Árvore de Documentos
==========================================================

Implementação Python da skill `fase-processual-doctree`. A árvore de peças é a
única fonte de sinal. Não consulta DataJud, movimentos CNJ, situação cadastral
ou qualquer fonte externa. Quando a árvore é insuficiente, o resultado correto
é a abstenção (código 16), nunca a inferência forçada.

Pipeline: normalizer (R0) → rules R1-R7 + RE-01..RE-12 + fronteiras F-01..F-13
→ audit. Contrato público: ``DocTreeClassifier.classify(documents, numero) -> dict``.

Fonte normativa: backend/../fase-processual-doctree/references/{regras,
taxonomia-pecas, vocabulario-pav, casos-fronteira, output-schema}.md
"""

from .classifier import DocTreeClassifier
from .normalizer import normalize_tree, DocumentPiece
from .rules import (
    FASE_NOMES,
    classify_domain,
    classify_execution,
    classify_knowledge,
    aplicar_fallback_teor,
)

__all__ = [
    "DocTreeClassifier",
    "normalize_tree",
    "DocumentPiece",
    "FASE_NOMES",
    "classify_domain",
    "classify_execution",
    "classify_knowledge",
    "aplicar_fallback_teor",
]
