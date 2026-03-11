import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .. import models, schemas

logger = logging.getLogger(__name__)


class PhaseCorrectionService:
    """Gerencia correções de fase processual."""

    @staticmethod
    def record_correction(
        db: Session,
        process_number: str,
        original_phase: str,
        corrected_phase: str,
        reason: str = None
    ) -> models.PhaseCorrection:
        """Registra uma correção de fase."""
        correction = models.PhaseCorrection(
            process_number=process_number,
            original_phase=original_phase,
            corrected_phase=corrected_phase,
            reason=reason
        )
        db.add(correction)
        db.commit()
        db.refresh(correction)
        logger.info(
            f"Phase correction recorded: {process_number} "
            f"{original_phase}→{corrected_phase} (reason: {reason})"
        )
        return correction

    @staticmethod
    def get_last_correction(db: Session, process_number: str) -> Optional[models.PhaseCorrection]:
        """Retorna a última correção de fase para um processo."""
        return db.query(models.PhaseCorrection).filter(
            models.PhaseCorrection.process_number == process_number
        ).order_by(desc(models.PhaseCorrection.corrected_at)).first()

    @staticmethod
    def get_all_corrections(db: Session, process_number: str):
        """Retorna todas as correções para um processo."""
        return db.query(models.PhaseCorrection).filter(
            models.PhaseCorrection.process_number == process_number
        ).order_by(desc(models.PhaseCorrection.corrected_at)).all()
