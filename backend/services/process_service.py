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
from .document_phase_classifier import DocumentPhaseClassifier, ClassificationResult
from .pav_data_transformer import PAVDataTransformer
import json as _json
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

        # [FUSION-ONLY] Classifica fase exclusivamente via Fusion PAV.
        # DataJud fornece dados cadastrais; a fase vem do DocumentPhaseClassifier.
        api_data = copy.deepcopy(api_data)
        _meta_fo = api_data.setdefault("__meta__", {})

        if self.fusion_service:
            try:
                fusion_result = await self.fusion_service.get_document_tree(process_number)
                if fusion_result and fusion_result.movimentos:
                    classification = DocumentPhaseClassifier.classify_with_trace(
                        fusion_result.movimentos,
                        fusion_result.classe_processual
                        or (api_data.get("classe") or {}).get("nome", ""),
                    )
                    fusion_phase = classification.phase
                    _meta_fo["fusion_phase_override"] = fusion_phase
                    _meta_fo["fusion_phase_source"] = fusion_result.fonte
                    _meta_fo["fusion_movements"] = [
                        {"date": m.data.isoformat(), "description": m.tipo_local, "code": m.tipo_cnj}
                        for m in fusion_result.movimentos
                    ]
                    _meta_fo["fusion_fonte"] = fusion_result.fonte
                    _meta_fo["fusion_classe_processual"] = fusion_result.classe_processual
                    _meta_fo["fusion_classification_log"] = classification.to_dict()
                    logger.info(
                        f"[Fusion-only] {process_number}: fase={fusion_phase}, "
                        f"fonte={fusion_result.fonte}, regra={classification.rule_applied}"
                    )
                else:
                    _meta_fo["fusion_phase_override"] = "Indefinido"
                    _meta_fo["fusion_phase_source"] = "fusion_api"
                    _meta_fo["fusion_phase_warning"] = (
                        "Processo não encontrado no Fusion/PAV. "
                        "Fase indisponível neste modo de classificação."
                    )
                    _meta_fo["fusion_classification_log"] = {
                        "phase": "Indefinido", "branch": None, "classe_normalizada": None,
                        "total_movimentos": 0, "rule_applied": "fusion_not_found",
                        "decisive_movement": None, "decisive_movement_date": None,
                        "anchor_matches": {},
                    }
                    logger.warning(
                        f"[Fusion-only] {process_number}: não encontrado no Fusion/PAV"
                    )
            except Exception as e:
                _meta_fo["fusion_phase_override"] = "Indefinido"
                _meta_fo["fusion_phase_source"] = "fusion_api"
                _meta_fo["fusion_phase_warning"] = (
                    f"Erro ao consultar Fusion/PAV: {e}. "
                    "Fase indisponível neste modo de classificação."
                )
                _meta_fo["fusion_classification_log"] = {
                    "phase": "Indefinido", "branch": None, "classe_normalizada": None,
                    "total_movimentos": 0, "rule_applied": "fusion_error",
                    "decisive_movement": None, "decisive_movement_date": None,
                    "anchor_matches": {},
                }
                logger.warning(f"[Fusion-only] {process_number}: erro Fusion: {e}")
        else:
            _meta_fo["fusion_phase_override"] = "Indefinido"
            _meta_fo["fusion_phase_source"] = "datajud"
            _meta_fo["fusion_phase_warning"] = (
                "Serviço Fusion/PAV não configurado. "
                "Fase indisponível neste modo de classificação."
            )
            _meta_fo["fusion_classification_log"] = {
                "phase": "Indefinido", "branch": None, "classe_normalizada": None,
                "total_movimentos": 0, "rule_applied": "fusion_unavailable",
                "decisive_movement": None, "decisive_movement_date": None,
                "anchor_matches": {},
            }

        # Transform and Save with transaction management
        process = self._save_process_data(process_number, api_data)

        # Record search in history
        if process:
            self._record_history(
                process,
                classification_log=_meta_fo.get("fusion_classification_log"),
            )

        return process

    async def get_or_update_process_pav_only(self, process_number: str) -> Optional[models.Process]:
        """
        [PAV-ONLY] Busca processo exclusivamente via PAV.
        Elimina dependência em DataJud completamente.

        Fluxo:
        1. Chama PAV via fusion_service.get_process_complete()
        2. Normaliza dados com PAVDataTransformer
        3. Classifica fase com DocumentPhaseClassifier
        4. Salva em DB
        5. Retorna processo ou None

        Args:
            process_number: número CNJ (com ou sem formatação)

        Returns:
            Process objeto ou None se não encontrado

        Raises:
            ProcessNotFoundException: Se processo não encontrado
        """
        logger.info(f"[PAV-ONLY] Iniciando busca para: {process_number}")
        if not self.fusion_service:
            logger.error("FusionService não configurado - PAV-only não disponível")
            raise ProcessNotFoundException(process_number)

        # Buscar dados COMPLETOS do PAV
        try:
            pav_response = await self.fusion_service.get_process_complete(process_number)
        except Exception as e:
            logger.error(f"[PAV-only] Erro ao buscar processo {process_number}: {e}")
            self._record_history_not_found(process_number, error_type="pav_error", error_message=str(e))
            raise ProcessNotFoundException(process_number) from e

        if not pav_response:
            # Não encontrado no PAV
            logger.info(f"[PAV-only] Processo {process_number} não encontrado")
            self._record_history_not_found(process_number, error_type="not_found")
            return None

        # Normalizar dados do PAV
        try:
            normalized_data = PAVDataTransformer.transform(pav_response)
        except ValueError as e:
            logger.error(f"[PAV-only] Erro ao normalizar dados: {e}")
            self._record_history_not_found(process_number, error_type="transform_error", error_message=str(e))
            raise ProcessNotFoundException(process_number) from e

        # Classificar fase usando movimentos do PAV
        try:
            movimentos_fusion = PAVDataTransformer.extract_movimentos_for_classification(pav_response)
            classe_processual = PAVDataTransformer.extract_classe_processual(pav_response)

            classification = DocumentPhaseClassifier.classify_with_trace(
                movimentos_fusion,
                classe_processual
            )
            fusion_phase = classification.phase
        except Exception as e:
            logger.warning(f"[PAV-only] Erro ao classificar fase: {e}")
            classification = None
            fusion_phase = "Indefinido"

        # Preparar dados para salvar no DB
        api_data = normalized_data
        api_data = copy.deepcopy(api_data)
        # IMPORTANTE: __meta__ deve estar no top-level, não em raw_data, para ser lido por _parse_datajud_response()
        _meta_fo = api_data.setdefault("__meta__", {})

        # Adicionar metadados de fase
        _meta_fo["fusion_phase_override"] = fusion_phase
        _meta_fo["fusion_phase_source"] = "pav_completo"
        _meta_fo["fusion_fonte"] = "pav_api"

        if classification:
            _meta_fo["fusion_classification_log"] = classification.to_dict()
            logger.info(
                f"[PAV-only] {process_number}: fase={fusion_phase}, "
                f"regra={classification.rule_applied}"
            )
        else:
            _meta_fo["fusion_classification_log"] = {
                "phase": fusion_phase, "branch": None, "classe_normalizada": classe_processual,
                "total_movimentos": len(movimentos_fusion) if movimentos_fusion else 0,
                "rule_applied": "classificacao_erro",
                "decisive_movement": None, "decisive_movement_date": None,
                "anchor_matches": {},
            }

        # Converter FusionMovimento objects para dicts para compatibilidade
        if "movimentos" in api_data and api_data["movimentos"]:
            movimentos_converted = []
            for mov in api_data["movimentos"]:
                if hasattr(mov, 'data'):  # É um FusionMovimento
                    movimentos_converted.append({
                        "dataHora": mov.data.isoformat(),
                        "tipo_local": mov.tipo_local,
                        "tipo_cnj": mov.tipo_cnj,
                    })
                else:  # Já é um dict
                    movimentos_converted.append(mov)
            api_data["movimentos"] = movimentos_converted

        # Salvar no DB
        process = self._save_process_data(process_number, api_data)

        # Registrar no histórico
        if process:
            self._record_history(
                process,
                classification_log=_meta_fo.get("fusion_classification_log"),
            )

        return process

    def _record_history(self, process: models.Process, classification_log: dict = None):
        """
        Record a found process in history, avoiding duplicates.
        If already exists, update timestamp, court info, phase and classification log.
        """
        log_json = (
            _json.dumps(classification_log, ensure_ascii=False)
            if classification_log else None
        )
        try:
            existing = self.db.query(models.SearchHistory).filter(
                models.SearchHistory.number == process.number
            ).first()

            if existing:
                existing.created_at = func.now()
                existing.status = "found"
                existing.court = process.court
                existing.phase_source = process.phase_source
                existing.phase = process.phase
                existing.classification_log = log_json
                existing.error_type = None
                existing.error_message = None
            else:
                history_entry = models.SearchHistory(
                    number=process.number,
                    status="found",
                    court=process.court,
                    tribunal_expected=process.tribunal_name,
                    phase_source=process.phase_source,
                    phase=process.phase,
                    classification_log=log_json,
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

        # [FUSION-ONLY] Phase Analysis — usa exclusivamente a fase calculada
        # pelo DocumentPhaseClassifier via Fusion PAV.
        raw_payload = dict(data)
        meta = raw_payload.get("__meta__") or {}

        phase_source = meta.get("fusion_phase_source", "datajud")

        if meta.get("fusion_phase_override"):
            phase = meta["fusion_phase_override"]
            meta["phase_analysis_mode"] = "fusion_only"
        elif meta.get("phase_override"):
            phase = meta["phase_override"]
            meta["phase_analysis_mode"] = "override"
        else:
            # Segurança: sem dados Fusion nem override → Indefinido
            phase = "Indefinido"
            meta["phase_analysis_mode"] = "fusion_only_fallback"

        meta["unified_phase"] = phase

        # Warning: usa aviso injetado pelo get_or_update_process()
        phase_warning = meta.get("fusion_phase_warning")

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
            "phase_source": phase_source,
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
        classification = DocumentPhaseClassifier.classify_with_trace(
            fusion_result.movimentos,
            fusion_result.classe_processual,
        )
        phase = classification.phase

        with transaction_scope(self.db):
            process = (
                self.db.query(models.Process)
                .filter(models.Process.number == process_number)
                .with_for_update()
                .first()
            )

            # Serializa movimentos Fusion para persistência em raw_data
            fusion_movs_json = [
                {"date": m.data.isoformat(), "description": m.tipo_local, "code": m.tipo_cnj}
                for m in fusion_result.movimentos
            ]
            fusion_raw = {"__meta__": {"fusion_movements": fusion_movs_json, "fusion_fonte": fusion_result.fonte}}

            if not process:
                process = models.Process(
                    number=process_number,
                    class_nature=fusion_result.classe_processual,
                    tribunal_name=fusion_result.sistema,
                    phase=phase,
                    phase_source=fusion_result.fonte,
                    raw_data=fusion_raw,
                )
                self.db.add(process)
            else:
                process.phase = phase
                process.phase_source = fusion_result.fonte
                process.raw_data = fusion_raw
                if fusion_result.classe_processual:
                    process.class_nature = fusion_result.classe_processual

            self.db.flush()

        # Registrar no histórico com phase_source e classification_log
        log_json = _json.dumps(classification.to_dict(), ensure_ascii=False)
        try:
            existing = self.db.query(models.SearchHistory).filter(
                models.SearchHistory.number == process_number
            ).first()

            if existing:
                existing.created_at = func.now()
                existing.status = "found"
                existing.phase_source = fusion_result.fonte
                existing.court = fusion_result.sistema
                existing.phase = phase
                existing.classification_log = log_json
                existing.error_type = None
                existing.error_message = None
            else:
                history_entry = models.SearchHistory(
                    number=process_number,
                    status="found",
                    court=fusion_result.sistema,
                    tribunal_expected=fusion_result.sistema,
                    phase_source=fusion_result.fonte,
                    phase=phase,
                    classification_log=log_json,
                )
                self.db.add(history_entry)

            self.db.commit()
        except Exception as e:
            logger.error(f"Error recording history for {process_number}: {e}")
            self.db.rollback()

        logger.info(
            f"Processo {process_number} classificado via Fusion: "
            f"fase={phase}, fonte={fusion_result.fonte}, regra={classification.rule_applied}"
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
        meta["fusion_movements"] = [
            {"date": m.data.isoformat(), "description": m.tipo_local, "code": m.tipo_cnj}
            for m in fusion_result.movimentos
        ]

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
