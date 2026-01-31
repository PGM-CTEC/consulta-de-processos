from sqlalchemy.orm import Session
from datetime import datetime
import models
import schemas
from .datajud import DataJudClient
import json
import logging

logger = logging.getLogger(__name__)

class ProcessService:
    def __init__(self, db: Session):
        self.db = db
        self.client = DataJudClient()

    async def get_or_update_process(self, process_number: str) -> models.Process:
        """
        Orchestrates the fetching and storage of process data.
        1. Checks DB for recent version? (Optional caching strategy)
        2. Calls DataJud API
        3. Parsed and saves to DB
        4. Returns the updated object
        """
        # Always fetch fresh for now (can add cache logic later)
        try:
            api_data = await self.client.get_process(process_number)
        except Exception as e:
            logger.error(f"Failed to fetch from API: {e}")
            # If API fails, try to return local copy if exists
            local_process = self.get_from_db(process_number)
            if local_process:
                return local_process
            raise e

        if not api_data:
            return None

        # Transform and Save
        return self._save_process_data(process_number, api_data)

    def get_from_db(self, process_number: str) -> models.Process:
        return self.db.query(models.Process).filter(models.Process.number == process_number).first()

    def _save_process_data(self, process_number: str, data: dict) -> models.Process:
        logger.info(f"KEYS IN DATA: {list(data.keys())}")
        
        # 1. Upsert Process
        process = self.get_from_db(process_number)
        
        # Extract fields (Final Mappings based on raw JSON)
        class_node = data.get("classe", {})
        class_name = class_node.get("nome", "N/A")
        
        tribunal = data.get("tribunal", "N/A")
        
        # Court/Vara from root orgaoJulgador
        root_orgao = data.get("orgaoJulgador", {})
        vara_name = root_orgao.get("nome", "")
        
        court_display = f"{tribunal} - {vara_name}" if vara_name else tribunal
        
        logger.info(f"EXTRACTED: Class={class_name}, Tribunal={tribunal}, Vara={vara_name}, CourtDisplay={court_display}")
        
        # Assunto (from 'assuntos' list)
        assuntos = data.get("assuntos", [])
        subject_name = assuntos[0].get("nome", "") if assuntos else "N/A"
        
        # Distribution Date (dataAjuizamento: YYYYMMDDHHMMSS)
        dist_raw = data.get("dataAjuizamento", "")
        dist_date = None
        if dist_raw:
             try:
                 dist_date = datetime.strptime(dist_raw[:14], "%Y%m%d%H%M%S")
             except:
                 pass
        
        # Phase Analysis
        movements_data = data.get("movimentos", [])
        from .phase_analyzer import PhaseAnalyzer
        phase = PhaseAnalyzer.analyze(class_name, movements_data, tribunal, data.get("grau", "G1"))

        mapped_data = {
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

        if not process:
            process = models.Process(number=process_number, **mapped_data)
            self.db.add(process)
        else:
            for key, value in mapped_data.items():
                setattr(process, key, value)
            process.last_update = datetime.now()
        
        self.db.flush() # Get ID

        # 2. Update Movements
        self.db.query(models.Movement).filter(models.Movement.process_id == process.id).delete()
        
        # Sort movements desc (Newest first)
        sorted_movements = sorted(movements_data, key=lambda x: x.get("dataHora", ""), reverse=True)
        
        for mov in sorted_movements:
            # Parse date
            mov_date = None
            if "dataHora" in mov:
                try:
                    t_str = mov["dataHora"].replace("Z", "+00:00")
                    mov_date = datetime.fromisoformat(t_str)
                except:
                    pass
            
            # DESCRIPTION FIX: DataJud uses 'nome' for the core movement description
            main_name = mov.get("nome", "")
            if not main_name:
                 main_name = "Movimentação"
            
            # Complements (tipo de petição, etc)
            comps = mov.get("complementosTabelados", [])
            comp_details = []
            for c in comps:
                c_val_name = c.get("nome", "")
                if c_val_name:
                    comp_details.append(c_val_name)
            
            full_description = main_name
            if comp_details:
                full_description += f" ({' | '.join(comp_details)})"

            new_mov = models.Movement(
                process_id=process.id,
                description=full_description,
                code=str(mov.get("codigo")),
                date=mov_date or datetime.now()
            )
            self.db.add(new_mov)

        self.db.commit()
        self.db.refresh(process)
        return process

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
