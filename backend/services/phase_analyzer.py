import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class PhaseAnalyzer:
    """
    Analyzes process phases based on PGM-Rio Business Rules (Janeiro 2026).
    Implements a deterministic rule engine using CNJ codes (Classes, Movements, Documents).
    """

    # --- Constants: Phase Hierarchy ---
    # 1. Fase Cognitiva
    PHASE_1_1_1 = "1.1.1 Postulatória (Petição Inicial -> Citação)"
    PHASE_1_1_2 = "1.1.2 Defesa (Aguardando Contestação)"
    PHASE_1_1_3 = "1.1.3 Réplica / Especificação de Provas"
    PHASE_1_1_4 = "1.1.4 Saneamento e Organização"
    PHASE_1_1_5 = "1.1.5 Instrução (Perícia, Audiências)"
    PHASE_1_1_6 = "1.1.6 Decisória (Aguardando Prazo Recursal)"
    
    PHASE_1_2_1 = "1.2.1 2ª Instância - Em Recurso"
    PHASE_1_2_4 = "1.2.4 2ª Instância - Julgamento"

    PHASE_1_3_0 = "1.3 Instâncias Superiores (STJ/STF)"

    # 2. Trânsito em Julgado
    PHASE_2_1 = "2.1 Trânsito em Julgado"

    # 3. Fase Satisfativa
    PHASE_3_1_2 = "3.1.2 Cumprimento de Sentença (Intimação)"
    PHASE_3_1_3 = "3.1.3 Cumprimento de Sentença (Impugnação)"
    
    PHASE_3_2_1 = "3.2.1 Execução Fiscal (Citação)"
    PHASE_3_2_2 = "3.2.2 Execução Fiscal (Penhora/Garantia)"
    PHASE_3_2_3 = "3.2.3 Execução Fiscal (Embargos)"
    PHASE_3_2_4 = "3.2.4 Execução Fiscal (Expropriação)"

    # 4. Arquivamento
    PHASE_4_1_1 = "4.1.1 Arquivamento Definitivo"
    PHASE_4_1_2 = "4.1.2 Arquivamento Provisório"

    # --- Mappings: CNJ Code Groups ---
    
    # 3.1 Classes Fazenda Ré (Cognitiva / MS / ACP)
    CLASSES_FAZENDA_RE = [
        7,      # Procedimento Comum Cível
        120,    # Mandado de Segurança Cível
        65,     # Ação Civil Pública
        1707,   # JEC
    ]

    # 3.2 Classes Fazenda Autora (Execução Fiscal / Cobrança)
    CLASSES_FAZENDA_AUTORA = [
        1116,   # Execução Fiscal
        159,    # Ação de Cobrança
    ]

    # Gatilhos de Arquivamento (Prioridade Máxima)
    MOVS_ARQUIVAMENTO = [
        "22",   # Baixa Definitiva
        "246",  # Arquivamento (check context/docs usually, but 22 is strong)
        "40"    # Arquivamento Provisório (LEF) - context
    ]

    # Gatilhos de Trânsito em Julgado
    MOVS_TRANSITO = ["848"]

    @staticmethod
    def analyze(class_code: int, movements: List[Dict], tribunal: str = "", grau: str = "G1") -> str:
        """
        Main entry point for phase analysis.
        
        Args:
            class_code: CNJ Class Code (int)
            movements: List of movement dicts (must contain 'codigo' and 'dataHora')
            tribunal: Tribunal identifier
            grau: 'G1', 'G2', 'STJ', etc.
        """
        try:
            # 0. Pre-processing
            if not movements:
                return "Sem Movimentações"
            
            # Sort movements by date descending (newest first)
            sorted_movements = sorted(
                movements, 
                key=lambda x: x.get("dataHora", ""), 
                reverse=True
            )
            
            class_code = int(class_code) if class_code else 0

            # 1. Check Hierarchical Level (Instance)
            # If explicit G2/Superior, use that context immediately, or check for Remessa
            current_instance = PhaseAnalyzer._determine_instance(sorted_movements, grau)
            
            if current_instance == "SUPERIOR":
                return PhaseAnalyzer.PHASE_1_3_0
            elif current_instance == "G2":
                # Basic check for now; could be refined with G2 specific matrix
                return PhaseAnalyzer.PHASE_1_2_1

            # 2. Check Archive / Baixa (Highest Priority)
            last_mov = sorted_movements[0]
            last_code = str(last_mov.get('codigo', ''))
            
            if last_code == "22":
                return PhaseAnalyzer.PHASE_4_1_1

            # 3. Check Trânsito em Julgado
            if PhaseAnalyzer._has_movement_code(sorted_movements, ["848"]):
                # If the *last* significant movement was 848, it is transitada.
                # Only return if no newer "execution" start movement exists
                return PhaseAnalyzer.PHASE_2_1

            # 4. Routing by Macro Flow (Auto vs Ré)
            if class_code in PhaseAnalyzer.CLASSES_FAZENDA_AUTORA or "execução" in str(class_code): # fallback str check
                return PhaseAnalyzer._resolve_fazenda_autora(sorted_movements)
            else:
                # Default to Fazenda Ré / Common Procedure
                return PhaseAnalyzer._resolve_fazenda_re(sorted_movements)

        except Exception as e:
            logger.error(f"Error in PhaseAnalyzer: {e}")
            return "Erro na Análise"

    @staticmethod
    def _determine_instance(movements: List[Dict], stated_grau: str) -> str:
        """
        Determines if the case is currently in G1, G2 or Superior.
        Checks for 'Remessa' movements if stated_grau is ambiguous.
        """
        if stated_grau in ["STJ", "STF", "SUP"]:
            return "SUPERIOR"
        
        if stated_grau == "G2":
            return "G2"

        # Check for Remessa to Tribunal (970) without subsequent Baixa/Retorno (60303)
        has_remessa = False
        has_retorno = False
        
        for mov in movements:
            code = str(mov.get('codigo', ''))
            if code == "970": # Remessa ao Tribunal
                has_remessa = True
                break # Found most recent remessa
            if code == "60303" or code == "123": # Retorno / Recebimento em G1
                has_retorno = True
        
        if has_remessa and not has_retorno:
            return "G2"
            
        return "G1"

    @staticmethod
    def _resolve_fazenda_re(movements: List[Dict]) -> str:
        """
        Applies rules for Common Procedure / Fazenda as Defendant (Section 6.2).
        Iterates from newest to oldest to find the current valid phase.
        """
        for mov in movements:
            code = str(mov.get('codigo', ''))
            
            # 1.1.6 Decisória
            if code == "246": # Sentença
                return PhaseAnalyzer.PHASE_1_1_6
            if code in ["198", "200", "219"]: # Julgamentos
                return PhaseAnalyzer.PHASE_1_1_6
                
            # 1.1.5 Instrução
            # No specific CNJ code for "Start Instruction" explicitly in doc, 
            # usually implies "Audiência" or "Perícia" designated.
            # Using keyword fallback for now as permitted by doc logic
            name = (mov.get('nome') or "").lower()
            if "audiência" in name or "perícia" in name:
                return PhaseAnalyzer.PHASE_1_1_5

            # 1.1.4 Saneamento
            if code == "25": # Saneador
                return PhaseAnalyzer.PHASE_1_1_4
            
            # 1.1.3 Réplica
            if code == "12177": # Juntada de Contestação
                return PhaseAnalyzer.PHASE_1_1_3

            # 1.1.2 Defesa (Aguardando Contestação)
            if code == "123": # Citação Realizada
                return PhaseAnalyzer.PHASE_1_1_2
            if code == "15216": # Determinação de Citação / Citacao Ordenada
                return PhaseAnalyzer.PHASE_1_1_2

            # 1.1.1 Postulatória (Initial State)
            if code == "26": # Distribuição
                return PhaseAnalyzer.PHASE_1_1_1

        return PhaseAnalyzer.PHASE_1_1_1 # Default fallback

    @staticmethod
    def _resolve_fazenda_autora(movements: List[Dict]) -> str:
        """
        Applies rules for Fiscal Execution / Fazenda as Plaintiff (Section 6.3).
        """
        for mov in movements:
            code = str(mov.get('codigo', ''))
            name = (mov.get('nome') or "").lower()

            # 4.1.2 Arquivamento Provisório
            if "arquivamento provisório" in name:
                return PhaseAnalyzer.PHASE_4_1_2

            # 3.2.4 Expropriação (Post-Judgment of Embargos)
            # Not explicitly coded, usually inferred if judgment happened and not satisfied.
            
            # 3.2.3 Embargos (Juntada de Embargos/Petição)
            # Doc 56 = Embargos. Usually appears as specific movement or Juntada + Doc Type
            # Integrating pure movement check first:
            if "embargos" in name and "juntada" in name:
                return PhaseAnalyzer.PHASE_3_2_3
            
            # 3.2.2 Penhora
            if "penhora" in name:
                return PhaseAnalyzer.PHASE_3_2_2

            # 3.2.1 Citação
            # In Execution, Citação (123) means we are waiting for payment/penhora (Phase 3.2.2 essentially)
            if code == "123":
               return PhaseAnalyzer.PHASE_3_2_2 # Citação Realizada -> Aguardando Penhora

            # Initial Execution State
            if code == "26":
                return PhaseAnalyzer.PHASE_3_2_1

        return PhaseAnalyzer.PHASE_3_2_1

    @staticmethod
    def _has_movement_code(movements: List[Dict], codes: List[str]) -> bool:
        """Helper to check if any movement in the list matches one of the codes."""
        for mov in movements:
            if str(mov.get('codigo', '')) in codes:
                return True
        return False
