"""
Script de reclassificação hierárquica.

Re-executa a classificação de todos os processos existentes no banco
e popula os 3 novos campos: stage, substage, transit_julgado.

Uso:
    python -m backend.scripts.reclassify_hierarchical [--dry-run] [--limit N]
"""
import argparse
import logging
import sys
from pathlib import Path

# Garantir que o diretório raiz esteja no sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database import SessionLocal
from backend.models import Process, SearchHistory
from backend.services.document_phase_classifier import DocumentPhaseClassifier
from backend.services.phase_analyzer import PhaseAnalyzer
from backend.services.fusion_api_client import FusionMovimento
from backend.services.process_service import (
    _consolidar_tres_fontes, _extrair_hierarquia_da_fonte,
)
from backend.services.hierarchical_classification import (
    PHASE_TO_STAGE_SUBSTAGE, derive_legacy_phase,
    _PHASES_WITH_IMPLICIT_TRANSIT,
)
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _reclassify_from_meta(meta: dict) -> tuple:
    """
    Tenta re-derivar (stage, substage, transit) a partir dos dados já no __meta__.

    Retorna (stage, substage, transit, source) ou (None, None, None, None) se
    não foi possível.
    """
    if not meta:
        return None, None, None, None

    # Tentar reclassificar via fontes disponíveis no meta
    # 1. Fusion classification_log (mais completo)
    fusion_log = meta.get("fusion_classification_log") or {}
    pav_log = meta.get("pav_tree_classification_log") or {}

    # Reclassificar PAV Tree se disponível
    pav_phase = meta.get("pav_tree_phase", "")
    pav_stage, pav_substage, pav_transit = None, None, None
    if pav_phase and pav_phase != "Indefinido" and pav_log.get("rule_applied"):
        pav_stage = pav_log.get("stage")
        pav_substage = pav_log.get("substage")
        pav_transit = pav_log.get("transit_julgado")

    # Reclassificar Fusion se disponível
    fusion_phase = meta.get("fusion_phase_override", "")
    fusion_stage, fusion_substage, fusion_transit = None, None, None
    if fusion_phase and fusion_phase != "Indefinido" and fusion_log.get("rule_applied"):
        fusion_stage = fusion_log.get("stage")
        fusion_substage = fusion_log.get("substage")
        fusion_transit = fusion_log.get("transit_julgado")

    # Reclassificar DataJud se disponível
    datajud_phase = meta.get("datajud_phase", "")
    datajud_stage, datajud_substage, datajud_transit = None, None, None

    # Se os logs salvos não têm campos hierárquicos (dados pré-migração),
    # derivar a partir do código de fase legacy
    if pav_phase and pav_phase != "Indefinido" and pav_stage is None:
        cod = pav_phase.split()[0] if pav_phase.split() else ""
        if cod in PHASE_TO_STAGE_SUBSTAGE:
            pav_stage, pav_substage = PHASE_TO_STAGE_SUBSTAGE[cod]
            pav_transit = _transit_from_legacy_code(cod)

    if fusion_phase and fusion_phase != "Indefinido" and fusion_stage is None:
        cod = fusion_phase.split()[0] if fusion_phase.split() else ""
        if cod in PHASE_TO_STAGE_SUBSTAGE:
            fusion_stage, fusion_substage = PHASE_TO_STAGE_SUBSTAGE[cod]
            fusion_transit = _transit_from_legacy_code(cod)

    if datajud_phase and datajud_phase != "Indefinido" and datajud_stage is None:
        cod = datajud_phase.split()[0] if datajud_phase.split() else ""
        if cod in PHASE_TO_STAGE_SUBSTAGE:
            datajud_stage, datajud_substage = PHASE_TO_STAGE_SUBSTAGE[cod]
            datajud_transit = _transit_from_legacy_code(cod)

    # Montar meta simulado para _extrair_hierarquia_da_fonte
    sim_meta = {
        "pav_tree_stage": pav_stage, "pav_tree_substage": pav_substage, "pav_tree_transit": pav_transit,
        "fusion_stage": fusion_stage, "fusion_substage": fusion_substage, "fusion_transit": fusion_transit,
        "datajud_stage": datajud_stage, "datajud_substage": datajud_substage, "datajud_transit": datajud_transit,
    }

    # Consolidar usando mesma lógica do process_service
    _, modo = _consolidar_tres_fontes(datajud_phase, fusion_phase, pav_phase)
    stage, substage, transit = _extrair_hierarquia_da_fonte(modo, sim_meta)

    if stage is not None:
        return stage, substage, transit, modo

    return None, None, None, None


def _transit_from_legacy_code(cod: str) -> str:
    """Deriva transit a partir do código de fase legacy.
    Fases 03, 06, 09 implicam trânsito em julgado."""
    if cod in _PHASES_WITH_IMPLICIT_TRANSIT:
        return "sim"
    return "nao"


def _reclassify_from_phase(phase: str) -> tuple:
    """
    Fallback: deriva (stage, substage, transit) a partir do código de fase legacy.
    Fases 03/06/09 → transit=sim; demais → transit=nao.
    """
    if not phase:
        return None, None, None

    cod = phase.split()[0] if phase.split() else ""
    if cod in PHASE_TO_STAGE_SUBSTAGE:
        stage, substage = PHASE_TO_STAGE_SUBSTAGE[cod]
        transit = _transit_from_legacy_code(cod)
        return stage, substage, transit

    return None, None, None


def reclassify_all(dry_run: bool = False, limit: int = 0):
    """Re-classifica todos os processos no banco."""
    db = SessionLocal()
    try:
        query = db.query(Process)
        if limit > 0:
            query = query.limit(limit)

        processes = query.all()
        total = len(processes)
        updated = 0
        skipped = 0
        divergences = []

        logger.info(f"Reclassificando {total} processos (dry_run={dry_run})")

        for i, process in enumerate(processes):
            raw_data = process.raw_data or {}
            meta = raw_data.get("__meta__", {})

            # Tentar via meta completo primeiro
            stage, substage, transit, source = _reclassify_from_meta(meta)

            if stage is None:
                # Fallback: derivar do código de fase legacy
                stage, substage, transit = _reclassify_from_phase(process.phase)
                source = "legacy_fallback"

            if stage is None:
                skipped += 1
                continue

            # Verificar divergência com phase legacy
            derived_legacy = derive_legacy_phase(stage, substage, transit)
            old_cod = (process.phase or "").split()[0] if process.phase else ""
            if derived_legacy != old_cod and old_cod:
                divergences.append({
                    "number": process.number,
                    "old_phase": old_cod,
                    "new_legacy": derived_legacy,
                    "stage": stage,
                    "substage": substage,
                    "transit": transit,
                    "source": source,
                })

            if not dry_run:
                process.stage = stage
                process.substage = substage
                process.transit_julgado = transit

                # Atualizar SearchHistory correspondente
                history = db.query(SearchHistory).filter(
                    SearchHistory.number == process.number
                ).first()
                if history:
                    history.stage = stage
                    history.substage = substage
                    history.transit_julgado = transit

            updated += 1

            if (i + 1) % 100 == 0:
                if not dry_run:
                    db.commit()
                logger.info(f"  Progresso: {i+1}/{total} ({updated} atualizados)")

        if not dry_run:
            db.commit()

        logger.info(f"Reclassificação completa: {updated} atualizados, {skipped} ignorados")

        if divergences:
            logger.warning(f"Divergências encontradas: {len(divergences)}")
            for d in divergences[:20]:
                logger.warning(
                    f"  {d['number']}: old={d['old_phase']} → derived={d['new_legacy']} "
                    f"(stage={d['stage']}, substage={d['substage']}, transit={d['transit']}, source={d['source']})"
                )
            if len(divergences) > 20:
                logger.warning(f"  ... e mais {len(divergences) - 20} divergências")
        else:
            logger.info("Nenhuma divergência encontrada")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reclassificação hierárquica de processos")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simula, sem gravar")
    parser.add_argument("--limit", type=int, default=0, help="Limitar a N processos (0=todos)")
    args = parser.parse_args()

    reclassify_all(dry_run=args.dry_run, limit=args.limit)
