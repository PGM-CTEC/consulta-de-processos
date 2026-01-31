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
        # 1. Upsert Process
        process = self.get_from_db(process_number)
        
        # Extract fields (Updated Mapping based on Inspection)
        # Root keys: classe, tribunal, dataAjuizamento
        
        class_node = data.get("classe", {})
        class_name = class_node.get("nome", "")
        
        tribunal = data.get("tribunal", "")
        
        # Try to find specific unit (Vara) from the last movement or other heuristic
        # DataJud response doesn't always have "orgaoJulgador" at root for public API sometimes
        specific_unit = ""
        movements_data = data.get("movimentos", [])
        if movements_data:
             # Look at the most recent movement for current location
             try:
                 # Ensure sorted? DataJud usually sends sorted by date desc? Let's check or just take first
                 # Inspection showed item 0 is oldest (1989)? 
                 # Wait, inspection output (Step 542) showed item 0 has date "1989". 
                 # Item 0 is Distribution. Last item is recent (2020).
                 # So list is ASCENDING? 
                 # I should sort it DESC to find current status.
                 sorted_movs = sorted(movements_data, key=lambda x: x.get("dataHora", ""), reverse=True)
                 last_mov = sorted_movs[0]
                 specific_unit = last_mov.get("orgaoJulgador", {}).get("nome", "")
             except:
                 pass
        
        court_display = f"{tribunal} - {specific_unit}" if specific_unit else tribunal
        
        # Distribution Date
        dist_raw = data.get("dataAjuizamento", "")
        dist_date = None
        if dist_raw:
             # Format YYYYMMDDHHMMSS -> 20070423000000
             try:
                 dist_date = datetime.strptime(dist_raw, "%Y%m%d%H%M%S")
             except:
                 pass
        
        # Phase Analysis
        from .phase_analyzer import PhaseAnalyzer
        phase = PhaseAnalyzer.analyze(class_name, movements_data, tribunal, data.get("grau", "G1"))

        mapped_data = {
            "class_nature": class_name,
            "subject": str(data.get("assunto", {}).get("nome", "")), # Assuming similar structure if exists, or check raw
            "court": court_display,
            "district": data.get("orgaoJulgador", {}).get("codigoMunicipioIBGE", ""), 
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
        
        # Sort movements desc (Newest first) for UI
        sorted_movements = sorted(movements_data, key=lambda x: x.get("dataHora", ""), reverse=True)
        
        for mov in sorted_movements:
            # Parse date
            mov_date = None
            if "dataHora" in mov:
                try:
                    # ISO Format from DataJud: 2020-09-09T14:22:21.000Z
                    # Python 3.11 fromisoformat handles Z. 
                    t_str = mov["dataHora"].replace("Z", "+00:00")
                    mov_date = datetime.fromisoformat(t_str)
                except:
                    pass
            
            # Name/Description Logic
            # Use 'nome' primarily, fall back to 'descricao' in complements
            description = mov.get("nome", "")
            if not description:
                 description = "Movimentação"
            
            # Append complements if any (e.g. "tipo_de_peticao: Petição (outras)")
            # In raw data: complementosTabelados: [{nome: ..., descricao: ...}]
            comps = mov.get("complementosTabelados", [])
            for c in comps:
                c_name = c.get("nome")
                if c_name:
                    description += f" - {c_name}"

            new_mov = models.Movement(
                process_id=process.id,
                description=description,
                code=str(mov.get("codigo")),
                date=mov_date or datetime.now()
            )
            self.db.add(new_mov)

        self.db.commit()
        self.db.refresh(process)
        return process
