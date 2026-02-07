import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

from .classification_rules import (
    ClassificadorFases, ProcessoJudicial, MovimentoProcessual, 
    GrauJurisdicao, DocumentoProcessual
)

logger = logging.getLogger(__name__)

class PhaseAnalyzer:
    """
    Analyzes process phases using the strict deterministic rules from
    'classification_rules.py' (based on PGM-Rio Business Rules).
    """

    @staticmethod
    def analyze(class_code: int, movements: List[Dict], tribunal: str = "", grau: str = "G1", process_number: str = "", raw_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Main entry point for phase analysis. Adapts the input data to the
        ProcessoJudicial dataclass and runs the ClassificadorFases.
        
        Args:
            class_code: CNJ Class Code (int)
            movements: List of movement dicts (must contain 'codigo' and 'dataHora')
            tribunal: Tribunal identifier
            grau: 'G1', 'G2', 'STJ', etc.
            process_number: Process number (CNJ format)
            raw_data: Full raw data from DataJud (optional, but useful for extra fields)
        """
        try:
            # 1. Adapt Inputs to ProcessoJudicial
            
            # Map Grau
            grau_enum = GrauJurisdicao.G1  # Default
            if grau in ["G2", "TR"]: 
                grau_enum = GrauJurisdicao.G2
            elif grau in ["STJ", "STF", "TST", "SUP"]:
                grau_enum = GrauJurisdicao.SUP
            elif grau == "JE":
                grau_enum = GrauJurisdicao.JE
            
            # Helper to safely parse dates
            def parse_date(date_str: str) -> datetime:
                try:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    return datetime.min

            # Adapt Movements
            movimentos_adaptados = []
            if movements:
                for m in movements:
                    try:
                        cod = int(m.get('codigo', 0))
                        # Inferir grau do movimento se não explícito (simplificação)
                        # Idealmente o DataJud/MNI traz isso, mas nem sempre claro no JSON simplificado
                        # Assumimos o grau atual do processo para os movimentos, a menos que especificado
                        mov_grau = grau_enum 
                        
                        movimentos_adaptados.append(MovimentoProcessual(
                            codigo=cod,
                            descricao=m.get('nome') or m.get('descricao', ''),
                            data=parse_date(m.get('dataHora', '')),
                            grau=mov_grau,
                            complementos=m.get('complementos', {})
                        ))
                    except (ValueError, TypeError):
                        continue

            # Adapt Documents (if available in raw_data)
            documentos_adaptados = []
            # TODO: Extract documents from raw_data if structure permits. 
            # DataJud 'hits' usually have a list of movements, and documents might be nested or separate.
            # strict rules rely partially on documents. using movements as proxy where possible.

            # Determine Polo (Autora vs Ré)
            # This is tricky without analyzing the 'partes'. Defaulting to RE (Fazenda Ré) 
            # unless we can determine otherwise from raw_data.
            polo = "RE"
            # TODO: Implement basic logic to check if PGM/Município is in 'poloAtivo'
            
            class_desc = "" # We might not have description easily available, but code is what matters most
            if raw_data:
                class_desc = raw_data.get('classe', {}).get('nome', '')

            processo = ProcessoJudicial(
                numero=process_number or "0000000-00.0000.0.00.0000",
                classe_codigo=int(class_code or 0),
                classe_descricao=class_desc,
                grau_atual=grau_enum,
                situacao="MOVIMENTO", # Default
                movimentos=movimentos_adaptados,
                documentos=documentos_adaptados,
                polo_fazenda=polo
            )

            # 2. Run Classification
            classificador = ClassificadorFases()
            resultado = classificador.classificar(processo)
            
            # 3. Return Phase Code + Description
            return f"{resultado.fase.value} {resultado.fase.descricao}"

        except Exception as e:
            logger.error(f"Error in PhaseAnalyzer: {e}")
            return "Erro na Análise"
