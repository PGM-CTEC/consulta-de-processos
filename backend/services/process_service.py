from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import models
import schemas
from .datajud import DataJudClient
from database import transaction_scope
from exceptions import DataJudAPIException, ProcessNotFoundException
import logging

logger = logging.getLogger(__name__)

class ProcessService:
    def __init__(self, db: Session):
        self.db = db
        self.client = DataJudClient()

    async def get_or_update_process(self, process_number: str) -> Optional[models.Process]:
        """
        Orchestrates the fetching and storage of process data.
        1. Calls DataJud API
        2. Parses and saves to DB with proper transaction management
        3. Returns the updated object
        """
        # Fetch fresh data from API
        try:
            api_data = await self.client.get_process(process_number)
        except DataJudAPIException as e:
            # DataJud API specific errors - try to return local copy if exists
            logger.warning(f"DataJud API error for {process_number}: {e.message}")
            local_process = self.get_from_db(process_number)
            if local_process:
                logger.info(f"Returning cached data for {process_number}")
                return local_process
            raise
        except Exception as e:
            # Unexpected errors - try local copy as fallback
            logger.error(f"Unexpected error fetching {process_number}: {str(e)}")
            local_process = self.get_from_db(process_number)
            if local_process:
                logger.info(f"Returning cached data for {process_number} after error")
                return local_process
            raise DataJudAPIException("Erro ao buscar processo") from e

        if not api_data:
            # Process not found in DataJud
            return None

        # Transform and Save with transaction management
        return self._save_process_data(process_number, api_data)

    def get_from_db(self, process_number: str) -> Optional[models.Process]:
        """Fetch process from database without locking."""
        return self.db.query(models.Process).filter(
            models.Process.number == process_number
        ).first()

    def _save_process_data(self, process_number: str, data: dict) -> models.Process:
        """
        Save or update process data with proper transaction management.
        Uses SELECT FOR UPDATE to prevent race conditions.
        """
        logger.debug(f"Saving process data for {process_number}")

        with transaction_scope(self.db):
            # CRITICAL: Use SELECT FOR UPDATE to lock row during update
            # This prevents race conditions when multiple requests arrive simultaneously
            process = (
                self.db.query(models.Process)
                .filter(models.Process.number == process_number)
                .with_for_update()  # Row-level lock
                .first()
            )

            # Extract and parse fields from DataJud response
            parsed_data = self._parse_datajud_response(data)

            if not process:
                # Create new process
                process = models.Process(number=process_number, **parsed_data)
                self.db.add(process)
                self.db.flush()  # Get ID without committing
                logger.info(f"Created new process: {process_number}")
            else:
                # Update existing process
                for key, value in parsed_data.items():
                    setattr(process, key, value)
                process.last_update = datetime.now()
                self.db.flush()
                logger.info(f"Updated existing process: {process_number}")

            # Delete old movements and add new ones (within same transaction)
            self.db.query(models.Movement).filter(
                models.Movement.process_id == process.id
            ).delete()

            # Parse and add movements
            movements_data = data.get("movimentos", [])
            self._add_movements(process.id, movements_data)

            # Transaction commits automatically via context manager

        # Refresh outside transaction (read-only operation)
        self.db.refresh(process)
        return process

    def _parse_datajud_response(self, data: dict) -> dict:
        """
        Parse DataJud API response into database fields.
        Handles all field extraction with proper error handling.
        """
        # Class information
        class_node = data.get("classe", {})
        class_name = class_node.get("nome", "N/A")

        # Tribunal
        tribunal = data.get("tribunal", "N/A")

        # Court/Vara information
        root_orgao = data.get("orgaoJulgador", {})
        vara_name = root_orgao.get("nome", "")
        court_display = f"{tribunal} - {vara_name}" if vara_name else tribunal

        # Subject (first from assuntos list)
        assuntos = data.get("assuntos", [])
        subject_name = assuntos[0].get("nome", "") if assuntos else "N/A"

        # Distribution Date with proper error handling
        dist_date = self._parse_datajud_date(
            data.get("dataAjuizamento", ""),
            "distribution date"
        )

        # Phase Analysis
        movements_data = data.get("movimentos", [])
        class_code = class_node.get("codigo")
        
        from .phase_analyzer import PhaseAnalyzer
        phase = PhaseAnalyzer.analyze(
            class_code,
            movements_data,
            tribunal,
            data.get("grau", "G1")
        )

        return {
            "class_nature": class_name,
            "subject": subject_name,
            "court": court_display,
            "tribunal_name": tribunal,
            "court_unit": vara_name,
            "district": str(root_orgao.get("codigoMunicipioIBGE", "")),
            "distribution_date": dist_date,
            "phase": phase,
            "raw_data": data
        }

    def _parse_datajud_date(self, date_str: str, field_name: str) -> Optional[datetime]:
        """
        Parse DataJud date format (YYYYMMDDHHMMSS) with proper error handling.
        """
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")
        except ValueError as e:
            logger.warning(f"Failed to parse {field_name}: '{date_str}' - {str(e)}")
            return None

    def _add_movements(self, process_id: int, movements_data: list) -> None:
        """
        Parse and add movements to the database.
        Handles date parsing and description formatting.
        """
        # Sort movements desc (Newest first)
        sorted_movements = sorted(
            movements_data,
            key=lambda x: x.get("dataHora", ""),
            reverse=True
        )

        for mov in sorted_movements:
            # Parse movement date
            mov_date = None
            if "dataHora" in mov:
                try:
                    t_str = mov["dataHora"].replace("Z", "+00:00")
                    mov_date = datetime.fromisoformat(t_str)
                except (ValueError, AttributeError) as e:
                    logger.warning(
                        f"Failed to parse movement date '{mov.get('dataHora')}': {str(e)}"
                    )

            # Build description from movement name and complements
            main_name = mov.get("nome", "Movimentação")

            # Add complements if available
            comps = mov.get("complementosTabelados", [])
            comp_details = [c.get("nome", "") for c in comps if c.get("nome")]

            full_description = main_name
            if comp_details:
                full_description += f" ({' | '.join(comp_details)})"

            # Create movement record
            new_mov = models.Movement(
                process_id=process_id,
                description=full_description,
                code=str(mov.get("codigo", "")),
                date=mov_date or datetime.now()
            )
            self.db.add(new_mov)

    async def get_bulk_processes(self, numbers: list) -> dict:
        """
        Executes multiple lookups.
        """
        results = []
        failures = []
        
        # Simple async loop (can be optimized with semaphore if needed)
        for number in numbers:
            try:
                # Reuse existing logic
                process = await self.get_or_update_process(number)
                if process:
                    results.append(process)
                else:
                    failures.append(number)
            except Exception as e:
                logger.error(f"Error in bulk processing for {number}: {e}")
                failures.append(number)
        
        return {"results": results, "failures": failures}
