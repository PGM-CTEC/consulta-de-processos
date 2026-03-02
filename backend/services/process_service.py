import asyncio
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from .datajud import DataJudClient
from .phase_analyzer import PhaseAnalyzer, DCP_WARNING_MESSAGE
from .. import models, schemas
from ..database import transaction_scope
from ..exceptions import DataJudAPIException, ProcessNotFoundException

logger = logging.getLogger(__name__)

class ProcessService:
    def __init__(
        self,
        db: Session,
        client: Optional[DataJudClient] = None,
        phase_analyzer: Optional[PhaseAnalyzer] = None
    ):
        """
        Initialize ProcessService with dependency injection.

        Args:
            db: SQLAlchemy database session
            client: DataJudClient instance (optional, defaults to DataJudClient())
            phase_analyzer: PhaseAnalyzer instance (optional, defaults to PhaseAnalyzer)

        This enables:
        - Testing with mock clients
        - Swapping implementations
        - Reduced coupling to external services
        """
        self.db = db
        self.client = client or DataJudClient()
        self.phase_analyzer = phase_analyzer or PhaseAnalyzer

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
        process = self._save_process_data(process_number, api_data)

        # Record search in history
        if process:
            self._record_history(process)

        return process

    def _record_history(self, process: models.Process):
        """Record the search in history."""
        try:
            history_entry = models.SearchHistory(
                number=process.number,
                court=process.court
            )
            self.db.add(history_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error recording history for {process.number}: {e}")
            self.db.rollback()

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
        root_orgao = data.get("orgaoJulgador", {}) or {}
        movements_data = data.get("movimentos", [])
        latest_orgao = self._get_latest_movement_orgao(movements_data) or root_orgao
        vara_name = latest_orgao.get("nome", "") if isinstance(latest_orgao, dict) else ""
        court_display = f"{tribunal} - {vara_name}" if vara_name else tribunal

        # Subject (first from assuntos list)
        assuntos = data.get("assuntos", [])
        subject_name = assuntos[0].get("nome", "") if assuntos else "N/A"

        # Distribution Date with proper error handling
        dist_date = self._parse_datajud_date(
            data.get("dataAjuizamento", ""),
            "distribution date"
        )

        # Phase Analysis - using injected dependency
        class_code = class_node.get("codigo")
        phase = self.phase_analyzer.analyze(
            class_code,
            movements_data,
            tribunal,
            data.get("grau", "G1"),
            raw_data=data
        )

        raw_payload = dict(data)
        meta = raw_payload.get("__meta__") or {}
        selected_index = meta.get("selected_index", 0)
        source_grau = None
        instances = meta.get("instances") or []
        if isinstance(selected_index, int) and 0 <= selected_index < len(instances):
            source_grau = (instances[selected_index] or {}).get("grau")
        if not source_grau:
            source_grau = raw_payload.get("grau")
        meta["phase_source_instance_index"] = selected_index
        meta["phase_source_grau"] = source_grau

        # Injeta mensagem de aviso quando processo é DCP TJRJ antigo
        phase_warning = None
        if isinstance(phase, str) and phase.endswith(" *"):
            phase_warning = DCP_WARNING_MESSAGE
            meta["phase_warning"] = phase_warning

        # Aviso quando apenas a Turma Recursal (TR = 2ª instância) foi localizada no
        # DataJud sem a 1ª instância do Juizado Especial (JE).  O DataJud indexa o TR
        # separado da tramitação no JE, e processos anteriores a ~2018 frequentemente
        # não têm a 1ª instância exposta na base pública.
        missing = meta.get("missing_expected_instances", [])
        if "JE" in missing and not phase_warning:
            phase_warning = (
                "Atenção: o DataJud localizou apenas a 2ª instância (Turma Recursal). "
                "A 1ª instância (Juizado Especial) pode estar tramitando ativamente "
                "no sistema do tribunal e não foi localizada na base pública do DataJud/CNJ."
            )
            meta["phase_warning"] = phase_warning

        raw_payload["__meta__"] = meta

        return {
            "class_nature": class_name,
            "subject": subject_name,
            "court": court_display,
            "tribunal_name": tribunal,
            "court_unit": vara_name,
            "district": str((root_orgao or {}).get("codigoMunicipioIBGE", "")),
            "distribution_date": dist_date,
            "phase": phase,
            "phase_warning": phase_warning,
            "raw_data": raw_payload
        }

    def _get_latest_movement_orgao(self, movements_data: list) -> Optional[dict]:
        """
        Get the orgaoJulgador from the most recent movement.
        This indicates where the process is currently tramiting.
        """
        latest_mov = None
        latest_date = None

        for mov in movements_data or []:
            mov_date = None
            if "dataHora" in mov:
                try:
                    t_str = mov["dataHora"].replace("Z", "+00:00")
                    mov_date = datetime.fromisoformat(t_str)
                except (ValueError, AttributeError):
                    mov_date = None

            if mov_date and (latest_date is None or mov_date > latest_date):
                latest_date = mov_date
                latest_mov = mov

        if latest_mov and isinstance(latest_mov, dict):
            return latest_mov.get("orgaoJulgador") or None
        return None

    def _parse_datajud_date(self, date_str: str, field_name: str) -> Optional[datetime]:
        """
        Parse DataJud date format (YYYYMMDDHHMMSS or ISO 8601) with proper error handling.
        """
        if not date_str:
            return None

        try:
            # Try DataJud specific format first: YYYYMMDDHHMMSS
            if len(date_str) >= 14 and date_str[:14].isdigit():
                 return datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")
            
            # Try ISO 8601 (e.g., 2014-09-11T10:02:00.000Z)
            # Replace Z with +00:00 for fromisoformat compatibility in older python versions if needed,
            # though Python 3.11+ handles Z correctly.
            clean_str = date_str.replace("Z", "+00:00")
            return datetime.fromisoformat(clean_str)

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

    def _parse_movements_list(self, movements_data: list) -> list:
        """
        Parse movements data into a list of dictionaries (for in-memory use).
        """
        # Sort movements desc (Newest first)
        sorted_movements = sorted(
            movements_data,
            key=lambda x: x.get("dataHora", ""),
            reverse=True
        )

        parsed_movements = []
        for mov in sorted_movements:
            # Parse movement date
            mov_date = None
            if "dataHora" in mov:
                try:
                    t_str = mov["dataHora"].replace("Z", "+00:00")
                    mov_date = datetime.fromisoformat(t_str)
                except (ValueError, AttributeError):
                    pass

            # Build description
            main_name = mov.get("nome", "Movimentação")
            comps = mov.get("complementosTabelados", [])
            comp_details = [c.get("nome", "") for c in comps if c.get("nome")]

            full_description = main_name
            if comp_details:
                full_description += f" ({' | '.join(comp_details)})"

            parsed_movements.append({
                "id": 0, # Temporary ID for non-persisted movements
                "description": full_description,
                "code": str(mov.get("codigo", "")),
                "date": mov_date or datetime.now()
            })
            
        return parsed_movements

    async def get_process_instance(self, process_number: str, instance_index: int) -> dict:
        """
        Retrieve a specific instance of the process from the stored raw_data.
        Does NOT update the main database record, just returns the parsed view.
        """
        process = self.get_from_db(process_number)
        if not process or not process.raw_data:
            raise ProcessNotFoundException(process_number)

        raw_data = process.raw_data
        meta = raw_data.get("__meta__", {})
        all_hits = meta.get("all_hits") or meta.get("hits") or [raw_data] # Fallback to self if no meta

        # If the DB cache does not contain the requested instance, refresh from DataJud.
        if instance_index >= len(all_hits):
            selected, fresh_meta = await self.client.get_process_instances(process_number)
            if selected and fresh_meta:
                selected["__meta__"] = fresh_meta
                process = self._save_process_data(process_number, selected)
                raw_data = process.raw_data or {}
                meta = raw_data.get("__meta__", {})
                all_hits = meta.get("all_hits") or meta.get("hits") or [raw_data]

        if instance_index < 0 or instance_index >= len(all_hits):
            raise ProcessNotFoundException(f"{process_number} (Instância {instance_index} não encontrada)")

        target_instance = all_hits[instance_index]
        
        # Parse this specific instance
        parsed_data = self._parse_datajud_response(target_instance)
        
        # Parse movements for this instance
        movements_list = self._parse_movements_list(target_instance.get("movimentos", []))
        
        # Construct response compatible with ProcessResponse
        # We use the main process ID for compatibility, but this is a transient view
        return {
            "id": process.id,
            "number": process.number,
            "last_update": process.last_update,
            "raw_data": process.raw_data, # Return full raw data so UI keeps context
            "movements": movements_list,
            **parsed_data
        }

    async def get_bulk_processes(self, numbers: list, max_concurrent: int = 10) -> dict:
        """
        Executes multiple process lookups in parallel using asyncio.gather().

        Args:
            numbers: List of CNJ process numbers to fetch
            max_concurrent: Maximum concurrent requests (default: 10)

        Returns:
            dict with 'results' (successful processes) and 'failures' (error numbers)

        Story: PERF-ARCH-001 - Async Bulk Processing
        Target: 50 items in <30s (vs 2-5 min sequential)
        """
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(number: str):
            """Fetch process with semaphore to limit concurrency."""
            async with semaphore:
                try:
                    process = await self.get_or_update_process(number)
                    return ("success", number, process)
                except Exception as e:
                    logger.error(f"Error fetching process {number}: {e}")
                    return ("failure", number, None)

        # Create tasks for all numbers
        tasks = [fetch_with_semaphore(number) for number in numbers]

        # Execute all tasks concurrently (respecting semaphore limit)
        results_list = await asyncio.gather(*tasks, return_exceptions=False)

        # Separate results and failures
        results = []
        failures = []

        for status, number, process in results_list:
            if status == "success" and process:
                results.append(process)
            else:
                failures.append(number)

        logger.info(
            f"Bulk processing completed: {len(results)} successful, {len(failures)} failed out of {len(numbers)} total"
        )

        return {"results": results, "failures": failures}

    async def get_all_instances(self, process_number: str) -> dict:
        """
        Busca todas as instâncias de um processo no DataJud.
        Retorna lista com todas as instâncias encontradas.
        """
        try:
            api_data, meta = await self.client.get_process_instances(process_number)

            if not api_data:
                raise ProcessNotFoundException(process_number)

            meta = meta or {}
            diagnostic = {
                "aliases_queried": meta.get("aliases_queried"),
                "missing_expected_instances": meta.get("missing_expected_instances"),
                "source_limited": meta.get("source_limited"),
                "diagnostic_note": meta.get("diagnostic_note"),
            }

            if not meta or meta.get("instances_count", 1) <= 1:
                # Apenas uma instância, retornar dados atuais
                return {
                    "process_number": process_number,
                    "instances_count": 1,
                    "instances": [self._parse_single_instance_summary(api_data, 0)],
                    **diagnostic,
                }

            # Múltiplas instâncias - retornar metadados
            return {
                "process_number": process_number,
                "instances_count": meta["instances_count"],
                "selected_index": meta.get("selected_index", 0),
                "instances": [
                    self._parse_instance_summary(inst, idx)
                    for idx, inst in enumerate(meta.get("instances", []))
                ],
                **diagnostic,
            }

        except DataJudAPIException as e:
            logger.error(f"Error fetching instances for {process_number}: {e}")
            raise

    # Mapeamento canônico de grau DataJud → rótulo de instância exibido ao usuário.
    # TR = Turma Recursal = 2ª instância dos Juizados Especiais.
    # JE = Juizado Especial = 1ª instância dos Juizados Especiais.
    _GRAU_LABEL: dict = {
        "G1":  "1ª Instância",
        "JE":  "1ª Instância (Juizado Especial)",
        "G2":  "2ª Instância",
        "TR":  "2ª Instância (Turma Recursal)",
        "SUP": "Instância Superior",
    }

    @classmethod
    def _grau_label(cls, grau: str | None) -> str:
        return cls._GRAU_LABEL.get(grau or "", grau or "N/A")

    def _parse_instance_summary(self, instance_data: dict, index: int) -> dict:
        """
        Cria um resumo de uma instância do processo.
        """
        grau = instance_data.get("grau", "N/A")
        return {
            "index": index,
            "grau": grau,
            "grau_label": self._grau_label(grau),
            "tribunal": instance_data.get("tribunal", "N/A"),
            "orgao_julgador": instance_data.get("orgao_julgador", "N/A"),
            "latest_movement_at": instance_data.get("latest_movement_at"),
            "updated_at": instance_data.get("updated_at")
        }

    def _parse_single_instance_summary(self, instance_data: dict, index: int) -> dict:
        """
        Build instance summary when the payload is raw DataJud hit (_source shape),
        not the pre-summarized metadata shape.
        """
        summarized = self.client._summarize_instance(instance_data)
        grau = summarized.get("grau", "N/A")
        return {
            "index": index,
            "grau": grau,
            "grau_label": self._grau_label(grau),
            "tribunal": summarized.get("tribunal", "N/A"),
            "orgao_julgador": summarized.get("orgao_julgador", "N/A"),
            "latest_movement_at": summarized.get("latest_movement_at"),
            "updated_at": summarized.get("updated_at"),
        }
