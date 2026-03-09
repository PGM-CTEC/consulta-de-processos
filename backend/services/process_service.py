import asyncio
import copy
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from .datajud import DataJudClient
from .phase_analyzer import PhaseAnalyzer, DCP_WARNING_MESSAGE
from .fusion_service import FusionService
from .fusion_api_client import FusionResult
from .document_phase_classifier import DocumentPhaseClassifier
from .. import models, schemas
from ..database import transaction_scope
from ..exceptions import DataJudAPIException, ProcessNotFoundException
from ..utils.string_cleaner import clean_orgao_name

logger = logging.getLogger(__name__)

class ProcessService:
    def __init__(
        self,
        db: Session,
        client: Optional[DataJudClient] = None,
        phase_analyzer: Optional[PhaseAnalyzer] = None,
        fusion_service: Optional[FusionService] = None
    ):
        """
        Initialize ProcessService with dependency injection.

        Args:
            db: SQLAlchemy database session
            client: DataJudClient instance (optional, defaults to DataJudClient())
            phase_analyzer: PhaseAnalyzer instance (optional, defaults to PhaseAnalyzer)
            fusion_service: FusionService instance for fallback to Fusion/PAV

        This enables:
        - Testing with mock clients
        - Swapping implementations
        - Reduced coupling to external services
        - Fallback to Fusion/PAV when DataJud returns not_found
        """
        self.db = db
        self.client = client or DataJudClient()
        self.phase_analyzer = phase_analyzer or PhaseAnalyzer
        self.fusion_service = fusion_service

    async def get_or_update_process(self, process_number: str) -> Optional[models.Process]:
        """
        Orchestrates the fetching and storage of process data.
        1. Calls DataJud API
        2. Parses and saves to DB with proper transaction management
        3. Returns the updated object
        """
        # Fetch fresh data from API — sem fallback de cache: toda consulta deve
        # refletir o estado atual das fontes (DataJud / Fusion).
        try:
            api_data = await self.client.get_process(process_number)
        except DataJudAPIException as e:
            logger.warning(f"DataJud API error for {process_number}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching {process_number}: {str(e)}")
            raise DataJudAPIException("Erro ao buscar processo") from e

        if not api_data:
            # Process not found in DataJud — try Fusion as fallback
            if self.fusion_service:
                fusion_result = await self.fusion_service.get_document_tree(process_number)
                if fusion_result and fusion_result.movimentos:
                    return await self._save_fusion_result(process_number, fusion_result)
            # não encontrado em nenhuma fonte
            self._record_history_not_found(process_number, error_type="not_found")
            return None

        # Enriquece com Fusion quando DataJud retornou dados mas sem a 1ª instância,
        # e o número do processo tem OOOO != "0000" (tramitou em 1ª instância)
        _meta_check = (api_data.get("__meta__") or {})
        _missing_check = _meta_check.get("missing_expected_instances") or []
        logger.info(
            f"[Fusion-check] {process_number} | "
            f"fusion_service={'sim' if self.fusion_service else 'NÃO CONFIGURADO'} | "
            f"missing_instances={_missing_check}"
        )
        if self._should_enrich_with_fusion(process_number, api_data):
            _fusion_unavailable = False
            if self.fusion_service:
                try:
                    fusion_result = await self.fusion_service.get_document_tree(process_number)
                    if fusion_result:
                        api_data = self._enrich_api_data_with_fusion(api_data, fusion_result)
                        logger.info(
                            f"Processo {process_number} enriquecido com Fusion "
                            f"(1ª instância ausente no DataJud)"
                        )
                    else:
                        _fusion_unavailable = True
                        logger.warning(
                            f"Processo {process_number}: Fusion ativado mas processo "
                            f"NÃO encontrado no Fusion/PAV — fase marcada como Indefinido"
                        )
                except Exception as e:
                    _fusion_unavailable = True
                    logger.warning(f"Falha ao enriquecer {process_number} com Fusion: {e}")
            else:
                _fusion_unavailable = True
                logger.warning(
                    f"Processo {process_number}: 1ª instância ausente no DataJud e "
                    f"Fusion não configurado — fase marcada como Indefinido"
                )
            if _fusion_unavailable:
                api_data = copy.deepcopy(api_data)
                _meta_ov = api_data.setdefault("__meta__", {})
                _meta_ov["phase_override"] = "Indefinido"
                _meta_ov["phase_override_reason"] = "first_instance_unavailable"

        # Transform and Save with transaction management
        process = self._save_process_data(process_number, api_data)

        # Record search in history
        if process:
            self._record_history(process)

        return process

    def _record_history(self, process: models.Process):
        """
        Record a found process in history, avoiding duplicates.
        If already exists, update timestamp and court info.
        """
        try:
            existing = self.db.query(models.SearchHistory).filter(
                models.SearchHistory.number == process.number
            ).first()

            if existing:
                existing.created_at = func.now()
                existing.status = "found"
                existing.court = process.court
                existing.error_type = None
                existing.error_message = None
            else:
                history_entry = models.SearchHistory(
                    number=process.number,
                    status="found",
                    court=process.court,
                    tribunal_expected=process.tribunal_name,
                )
                self.db.add(history_entry)

            self.db.commit()
        except Exception as e:
            logger.error(f"Error recording history for {process.number}: {e}")
            self.db.rollback()

    def _record_history_not_found(self, process_number: str, error_type: str = "not_found", error_message: str = None):
        """
        Record a failed search (not found or API error) in history.
        Attempts to infer expected tribunal from CNJ number.
        """
        try:
            tribunal_expected = None
            try:
                alias = self.client._get_tribunal_alias(process_number)
                tribunal_expected = alias.replace("api_publica_", "").upper()
            except Exception:
                pass

            existing = self.db.query(models.SearchHistory).filter(
                models.SearchHistory.number == process_number
            ).first()

            if existing:
                existing.created_at = func.now()
                existing.status = error_type
                existing.error_type = error_type
                existing.error_message = error_message
                if tribunal_expected:
                    existing.tribunal_expected = tribunal_expected
            else:
                history_entry = models.SearchHistory(
                    number=process_number,
                    status=error_type,
                    error_type=error_type,
                    error_message=error_message,
                    tribunal_expected=tribunal_expected,
                )
                self.db.add(history_entry)

            self.db.commit()
        except Exception as e:
            logger.error(f"Error recording failure history for {process_number}: {e}")
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
            parsed_data = self._parse_datajud_response(data, process_number)

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

    def _parse_datajud_response(self, data: dict, process_number: str = "") -> dict:
        """
        Parse DataJud API response into database fields.
        Handles all field extraction with proper error handling.

        When multiple instances are available, performs unified phase analysis
        considering all instances together. Otherwise falls back to single-instance analysis.
        """
        # Class information
        class_node = data.get("classe", {})
        class_name = class_node.get("nome", "N/A")

        # Tribunal
        tribunal = clean_orgao_name(data.get("tribunal", "N/A"))

        # Court/Vara information
        root_orgao = data.get("orgaoJulgador", {}) or {}
        movements_data = data.get("movimentos", [])
        latest_orgao = self._get_latest_movement_orgao(movements_data) or root_orgao
        vara_name = latest_orgao.get("nome", "") if isinstance(latest_orgao, dict) else ""
        vara_name = clean_orgao_name(vara_name)
        court_display = f"{tribunal} - {vara_name}" if vara_name else tribunal

        # Subject (first from assuntos list)
        assuntos = data.get("assuntos", [])
        subject_name = assuntos[0].get("nome", "") if assuntos else "N/A"

        # Distribution Date with proper error handling
        dist_date = self._parse_datajud_date(
            data.get("dataAjuizamento", ""),
            "distribution date"
        )

        # Phase Analysis - with support for unified multi-instance analysis
        class_code = class_node.get("codigo")
        raw_payload = dict(data)
        meta = raw_payload.get("__meta__") or {}
        all_hits = meta.get("all_hits") or []

        # Phase override — 1ª instância esperada mas indisponível (Fusion falhou/ausente)
        if meta.get("phase_override"):
            phase = meta["phase_override"]
            meta["phase_analysis_mode"] = "override"
            meta["phase_instances_analyzed"] = 0
            logger.info(
                f"Phase override '{phase}' para {process_number}: "
                f"{meta.get('phase_override_reason')}"
            )
        # If multiple instances available, use unified analysis
        elif all_hits and len(all_hits) > 1:
            phase = self.phase_analyzer.analyze_unified(
                all_instances=all_hits,
                process_number=process_number,
                tribunal=tribunal
            )
            meta["phase_analysis_mode"] = "unified"
            meta["phase_instances_analyzed"] = len(all_hits)
            logger.info(f"Unified phase analysis for {process_number}: {len(all_hits)} instances")
        else:
            # Single instance or no meta - fallback to original analysis
            phase = self.phase_analyzer.analyze(
                class_code,
                movements_data,
                tribunal,
                data.get("grau", "G1"),
                process_number=process_number,
                raw_data=data
            )
            meta["phase_analysis_mode"] = "single_instance"
            meta["phase_instances_analyzed"] = 1

        # Store unified phase in meta for reuse in get_process_instance()
        meta["unified_phase"] = phase

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

        if meta.get("fusion_g1_enriched") and not phase_warning:
            phase_warning = (
                "Informação: dados da 1ª instância complementados via Fusion/PAV "
                "por ausência na base pública do DataJud/CNJ."
            )
            meta["phase_warning"] = phase_warning

        if meta.get("phase_override_reason") == "first_instance_unavailable" and not phase_warning:
            phase_warning = (
                "Não foi possível obter dados da 1ª instância. "
                "Tente consultar novamente."
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

        IMPORTANT: The phase returned is ALWAYS the unified phase (analyzed across all instances),
        not the per-instance phase. This ensures the phase displayed is consistent regardless
        of which instance the user is viewing.
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

        # Parse this specific instance (but don't recalculate phase)
        parsed_data = self._parse_datajud_response(target_instance, process_number)

        # Override phase with unified phase (cached in meta) for consistency
        # The phase reflects the process as a whole, not this individual instance
        unified_phase = meta.get("unified_phase")
        if unified_phase:
            parsed_data["phase"] = unified_phase

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
            "tribunal": clean_orgao_name(instance_data.get("tribunal", "N/A")),
            "orgao_julgador": clean_orgao_name(instance_data.get("orgao_julgador", "N/A")),
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
            "tribunal": clean_orgao_name(summarized.get("tribunal", "N/A")),
            "orgao_julgador": clean_orgao_name(summarized.get("orgao_julgador", "N/A")),
            "latest_movement_at": summarized.get("latest_movement_at"),
            "updated_at": summarized.get("updated_at"),
        }

    async def _save_fusion_result(
        self, process_number: str, fusion_result: FusionResult
    ) -> models.Process:
        """Salva resultado do Fusion no banco e retorna o processo."""
        phase = DocumentPhaseClassifier.classify(
            fusion_result.movimentos,
            fusion_result.classe_processual,
        )

        with transaction_scope(self.db):
            process = (
                self.db.query(models.Process)
                .filter(models.Process.number == process_number)
                .with_for_update()
                .first()
            )

            if not process:
                process = models.Process(
                    number=process_number,
                    class_nature=fusion_result.classe_processual,
                    tribunal_name=fusion_result.sistema,
                    phase=phase,
                    phase_source=fusion_result.fonte,
                )
                self.db.add(process)
            else:
                process.phase = phase
                process.phase_source = fusion_result.fonte
                if fusion_result.classe_processual:
                    process.class_nature = fusion_result.classe_processual

            self.db.flush()

        # Registrar no histórico com phase_source
        try:
            existing = self.db.query(models.SearchHistory).filter(
                models.SearchHistory.number == process_number
            ).first()

            if existing:
                existing.created_at = func.now()
                existing.status = "found"
                existing.phase_source = fusion_result.fonte
                existing.court = fusion_result.sistema
                existing.error_type = None
                existing.error_message = None
            else:
                history_entry = models.SearchHistory(
                    number=process_number,
                    status="found",
                    court=fusion_result.sistema,
                    tribunal_expected=fusion_result.sistema,
                    phase_source=fusion_result.fonte,
                )
                self.db.add(history_entry)

            self.db.commit()
        except Exception as e:
            logger.error(f"Error recording history for {process_number}: {e}")
            self.db.rollback()

        logger.info(
            f"Processo {process_number} classificado via Fusion: "
            f"fase={phase}, fonte={fusion_result.fonte}"
        )
        return process

    @staticmethod
    def _should_enrich_with_fusion(process_number: str, api_data: dict) -> bool:
        """
        Retorna True quando o DataJud retornou dados mas sem a 1ª instância,
        e o processo é elegível para enriquecimento via Fusion.

        Condições (ambas necessárias):
        1. Últimos 4 dígitos do número CNJ (OOOO) != "0000"
        2. DataJud não retornou G1 ou JE (missing_expected_instances contém "G1" ou "JE")
        """
        clean = "".join(filter(str.isdigit, process_number))
        if len(clean) != 20 or clean[16:20] == "0000":
            return False
        meta = api_data.get("__meta__") or {}
        missing = meta.get("missing_expected_instances") or []
        return "G1" in missing or "JE" in missing

    @staticmethod
    def _build_synthetic_g1_hit(fusion_result) -> dict:
        """
        Constrói um hit sintético no formato DataJud a partir de dados do Fusion.
        Representa a 1ª instância ausente no DataJud para análise unificada de fase.
        """
        movimentos = []
        for m in (fusion_result.movimentos or []):
            data_hora = None
            m_data = getattr(m, "data", None)
            if m_data and m_data != datetime.min:
                try:
                    data_hora = m_data.isoformat()
                except Exception:
                    pass
            movimentos.append({
                "nome": getattr(m, "tipo_cnj", None) or getattr(m, "tipo_local", None) or "",
                "codigo": 0,
                "dataHora": data_hora,
            })
        return {
            "grau": "G1",
            "tribunal": fusion_result.sistema or "",
            "orgaoJulgador": {"nome": fusion_result.sistema or "Fusion/PAV"},
            "classe": {
                "nome": fusion_result.classe_processual or "",
                "codigo": None,
            },
            "movimentos": movimentos,
            "__source__": "fusion",
        }

    def _enrich_api_data_with_fusion(self, api_data: dict, fusion_result) -> dict:
        """
        Enriquece dados do DataJud com informações do Fusion para a 1ª instância ausente.

        - Adiciona hit sintético G1 ao all_hits para análise unificada de fase.
        - Atualiza a classe processual com o dado da 1ª instância (Fusion).
        - Remove G1/JE de missing_expected_instances (agora cobertos via Fusion).
        """
        enriched = copy.deepcopy(api_data)
        meta = enriched.setdefault("__meta__", {})

        synthetic_g1 = self._build_synthetic_g1_hit(fusion_result)
        all_hits = list(meta.get("all_hits") or [])
        all_hits.append(synthetic_g1)
        meta["all_hits"] = all_hits
        meta["instances_count"] = len(all_hits)
        meta["fusion_g1_enriched"] = True
        meta["fusion_fonte"] = fusion_result.fonte
        meta["fusion_classe_processual"] = fusion_result.classe_processual

        # Usa classe processual da 1ª instância (Fusion) como classe principal
        if fusion_result.classe_processual:
            meta["datajud_classe_original"] = (enriched.get("classe") or {}).get("nome", "")
            enriched["classe"] = {
                "nome": fusion_result.classe_processual,
                "codigo": None,
            }

        # Remove G1/JE do missing (cobertos agora via Fusion)
        missing = [m for m in (meta.get("missing_expected_instances") or []) if m not in ("G1", "JE")]
        meta["missing_expected_instances"] = missing
        meta["source_limited"] = bool(missing)

        return enriched
