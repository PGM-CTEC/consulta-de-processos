"""
audit.py — Log estruturado por decisão.

Cada classificação produz um registro de auditoria imutável contendo: número,
regras aplicadas, peças determinantes, índices de confiança por etapa, flags e
raciocínio. Toda decisão fica rastreável para revisão humana e para
retroalimentação do loop de correção (phase_corrections).
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AuditRecord:
    numero: str
    timestamp: str
    fase_codigo: str
    confianca: float
    regra_determinante: str
    documentos_determinantes: List[int]
    flags: Dict[str, Any]
    raciocinio: str
    modo_evidencia: str
    perspectiva_classificacao: str
    classe_processual: Optional[str]
    qualidade_arvore: str
    fase_provavel: Optional[str] = None
    motivo_abstencao: Optional[str] = None
    marcadores: Dict[str, Any] = field(default_factory=dict)
    documentos_lidos_fallback: List[int] = field(default_factory=list)
    campos_inferidos: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)


def build_audit_record(
    numero: str,
    output: Dict[str, Any],
    campos_inferidos: Optional[List[Dict[str, Any]]] = None,
) -> AuditRecord:
    flags = output.get("flags", {}) or {}
    return AuditRecord(
        numero=numero,
        timestamp=datetime.now(timezone.utc).isoformat(),
        fase_codigo=output.get("fase_codigo", "ERR"),
        confianca=float(output.get("confianca", 0.0) or 0.0),
        regra_determinante=output.get("regra_determinante", ""),
        documentos_determinantes=list(output.get("documentos_determinantes", []) or []),
        flags=flags,
        raciocinio=output.get("raciocinio", ""),
        modo_evidencia=output.get("modo_evidencia", "metadados_apenas"),
        perspectiva_classificacao=output.get("perspectiva_classificacao", "processual_arrecadatoria"),
        classe_processual=output.get("classe_processual"),
        qualidade_arvore=output.get("qualidade_arvore", "suficiente"),
        fase_provavel=output.get("fase_provavel"),
        motivo_abstencao=output.get("motivo_abstencao"),
        marcadores=output.get("marcadores", {}) or {},
        documentos_lidos_fallback=list(flags.get("documentos_lidos_fallback", []) or []),
        campos_inferidos=campos_inferidos or [],
    )


def log_audit(record: AuditRecord) -> None:
    """Em produção: registra em logger INFO estruturado."""
    try:
        logger.info(
            "doctree.audit numero=%s fase=%s confianca=%.2f regra=%s docs=%s",
            record.numero,
            record.fase_codigo,
            record.confianca,
            record.regra_determinante,
            record.documentos_determinantes,
        )
    except Exception:
        logger.exception("Falha ao registrar auditoria doctree para %s", record.numero)
