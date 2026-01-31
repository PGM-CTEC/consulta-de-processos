from datetime import datetime

class PhaseAnalyzer:
    @staticmethod
    def analyze(class_name: str, movements: list, tribunal: str = "") -> str:
        """
        Determines the process phase based on class and movements.
        """
        class_name = (class_name or "").lower()
        # Ensure we have a sorted list of movements by date desc if needed, 
        # but usually we iterate over all or check the last one.
        # Assuming 'movements' is a list of dicts from DataJud API (or models).
        
        # Heuristics
        
        # 1. Execution Phase (Execução)
        if "execução" in class_name or "cumprimento" in class_name:
            return "Execução"
            
        # 2. Res Judicata (Transitado em Julgado)
        # Check for specific movement codes or names
        # Code 848: Trânsito em Julgado
        for mov in movements:
            name = (mov.get("nome") or "").lower()
            code = str(mov.get("codigo"))
            if "trânsito em julgado" in name or code == "848":
                # Check if there was no later "Baixa" or "Arquivamento" which might supercede,
                # but generally it implies the phase is done or moving to execution.
                # Let's keep it simple: if transitou, it's "Trânsito em Julgado" unless archived.
                pass 
                
        # 3. Check for Archive (Baixa / Arquivamento)
        # Check the *last* movement (most recent)
        if movements:
            # Sort by date desc just to be safe if the list isn't
            try:
                sorted_movs = sorted(movements, key=lambda x: x.get("dataHora", ""), reverse=True)
                last_mov = sorted_movs[0]
                last_name = (last_mov.get("nome") or "").lower()
                last_code = str(last_mov.get("codigo"))
                
                if "baixa" in last_name or "arquiv" in last_name or last_code in ["22", "246"]:
                    return "Arquivado / Baixa Definitiva"
            except:
                pass

        # 4. Superior Instances (Recurso)
        # If tribunal implies G2 or Superior
        # This is hard to detect solely from class/movs without context of the court, 
        # but if the last movement is "Remessa ao Tribunal..."
        if movements:
             try:
                sorted_movs = sorted(movements, key=lambda x: x.get("dataHora", ""), reverse=True)
                last_mov = sorted_movs[0]
                last_name = (last_mov.get("nome") or "").lower()
                if "remessa" in last_name and "tribunal" in last_name:
                    return "Em Grau de Recurso"
             except:
                pass

        # Default
        return "Conhecimento"
