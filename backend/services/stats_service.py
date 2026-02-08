import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from .. import models, schemas

logger = logging.getLogger(__name__)

class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def get_database_stats(self) -> schemas.DatabaseStats:
        """
        Generate statistics from the local database.
        Returns aggregated data about stored processes.
        """
        try:
            # Total processes
            total_processes = self.db.query(func.count(models.Process.id)).scalar() or 0

            # Total movements
            total_movements = self.db.query(func.count(models.Movement.id)).scalar() or 0

            # Group by tribunal
            tribunal_stats = (
                self.db.query(
                    models.Process.tribunal_name,
                    func.count(models.Process.id).label('count')
                )
                .filter(models.Process.tribunal_name.isnot(None))
                .group_by(models.Process.tribunal_name)
                .order_by(func.count(models.Process.id).desc())
                .limit(10)
                .all()
            )

            tribunals = [
                schemas.TribunalStats(
                    tribunal_name=name or "Não especificado",
                    count=count
                )
                for name, count in tribunal_stats
            ]

            # Group by phase
            phase_stats = (
                self.db.query(
                    models.Process.phase,
                    func.count(models.Process.id).label('count')
                )
                .filter(models.Process.phase.isnot(None))
                .group_by(models.Process.phase)
                .order_by(func.count(models.Process.id).desc())
                .all()
            )

            phases = [
                schemas.PhaseStats(
                    phase=phase or "Conhecimento",
                    count=count
                )
                for phase, count in phase_stats
            ]

            # Timeline - processes by distribution month
            timeline_stats = (
                self.db.query(
                    func.strftime('%Y-%m', models.Process.distribution_date).label('month'),
                    func.count(models.Process.id).label('count')
                )
                .filter(models.Process.distribution_date.isnot(None))
                .group_by(func.strftime('%Y-%m', models.Process.distribution_date))
                .order_by(func.strftime('%Y-%m', models.Process.distribution_date).desc())
                .limit(12)
                .all()
            )

            timeline = [
                schemas.TimelineStats(
                    month=month or "Desconhecido",
                    count=count
                )
                for month, count in timeline_stats
            ]
            timeline.reverse()  # Oldest to newest

            # Most recent update
            last_updated = (
                self.db.query(func.max(models.Process.last_update))
                .scalar()
            )

            return schemas.DatabaseStats(
                total_processes=total_processes,
                total_movements=total_movements,
                tribunals=tribunals,
                phases=phases,
                timeline=timeline,
                last_updated=last_updated
            )

        except Exception as e:
            logger.error(f"Error generating database stats: {str(e)}")
            raise
