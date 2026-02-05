
import pytest
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from services.phase_analyzer import PhaseAnalyzer

def test_fazenda_re_flow():
    """Test standard flow for Fazenda as Defendant (Procedimento Comum - 7)"""
    
    # 1. Distribution
    movs = [{"codigo": 26, "nome": "Distribuído", "dataHora": "2024-01-01"}]
    assert PhaseAnalyzer.analyze(7, movs) == PhaseAnalyzer.PHASE_1_1_1
    
    # 2. Citação
    movs.insert(0, {"codigo": 123, "nome": "Citação Realizada", "dataHora": "2024-01-15"})
    assert PhaseAnalyzer.analyze(7, movs) == PhaseAnalyzer.PHASE_1_1_2
    
    # 3. Contestação
    movs.insert(0, {"codigo": 12177, "nome": "Juntada de Contestação", "dataHora": "2024-02-01"})
    assert PhaseAnalyzer.analyze(7, movs) == PhaseAnalyzer.PHASE_1_1_3
    
    # 4. Saneamento
    movs.insert(0, {"codigo": 25, "nome": "Despacho Saneador", "dataHora": "2024-03-01"})
    assert PhaseAnalyzer.analyze(7, movs) == PhaseAnalyzer.PHASE_1_1_4
    
    # 5. Sentença
    movs.insert(0, {"codigo": 246, "nome": "Sentença Proferida", "dataHora": "2024-06-01"})
    assert PhaseAnalyzer.analyze(7, movs) == PhaseAnalyzer.PHASE_1_1_6
    
    # 6. Trânsito
    movs.insert(0, {"codigo": 848, "nome": "Trânsito em Julgado", "dataHora": "2024-07-01"})
    assert PhaseAnalyzer.analyze(7, movs) == PhaseAnalyzer.PHASE_2_1
    
    # 7. Baixa
    movs.insert(0, {"codigo": 22, "nome": "Baixa Definitiva", "dataHora": "2024-08-01"})
    assert PhaseAnalyzer.analyze(7, movs) == PhaseAnalyzer.PHASE_4_1_1

def test_fazenda_autora_flow():
    """Test flow for Fazenda as Plaintiff (Execução Fiscal - 1116)"""
    
    # 1. Distribution
    movs = [{"codigo": 26, "nome": "Distribuído", "dataHora": "2024-01-01"}]
    assert PhaseAnalyzer.analyze(1116, movs) == PhaseAnalyzer.PHASE_3_2_1
    
    # 2. Citação (In execution this moves to waiting for payment/penhora)
    movs.insert(0, {"codigo": 123, "nome": "Citação Realizada", "dataHora": "2024-02-01"})
    assert PhaseAnalyzer.analyze(1116, movs) == PhaseAnalyzer.PHASE_3_2_2
    
    # 3. Penhora
    movs.insert(0, {"codigo": 0, "nome": "Penhora Realizada", "dataHora": "2024-03-01"})
    assert PhaseAnalyzer.analyze(1116, movs) == PhaseAnalyzer.PHASE_3_2_2
    
    # 4. Embargos
    movs.insert(0, {"codigo": 0, "nome": "Juntada de Petição de Embargos", "dataHora": "2024-04-01"})
    assert PhaseAnalyzer.analyze(1116, movs) == PhaseAnalyzer.PHASE_3_2_3

def test_instance_logic():
    """Test G1 vs G2 logic"""
    movs = [
        {"codigo": 26, "nome": "Distribuído", "dataHora": "2024-01-01"},
        {"codigo": 246, "nome": "Sentença", "dataHora": "2024-06-01"},
        {"codigo": 970, "nome": "Remessa ao Tribunal", "dataHora": "2024-07-01"}
    ]
    
    # Should be G2 because of Remessa
    assert PhaseAnalyzer.analyze(7, movs) == PhaseAnalyzer.PHASE_1_2_1
    
    # Explicit G2
    assert PhaseAnalyzer.analyze(7, movs, grau="G2") == PhaseAnalyzer.PHASE_1_2_1
    
    # Return to G1
    movs.insert(0, {"codigo": 60303, "nome": "Baixa/Retorno dos Autos", "dataHora": "2024-12-01"})
    # Only checks last code if it maps to specific phase, otherwise fallback logic might apply.
    # In our logic, 60303 is not a phase trigger itself, but "Retorno" flag in _determine_instance should toggle it back to G1.
    # If back in G1, it resumes checking G1 phases. The last G1 trigger was Sentença (246).
    assert PhaseAnalyzer.analyze(7, movs) == PhaseAnalyzer.PHASE_1_1_6 # Back in G1, status is Decisória (post-sentence)

if __name__ == "__main__":
    # Simple manual runner if pytest not available/configured
    print("Running manual tests...")
    try:
        test_fazenda_re_flow()
        print("✓ Fazenda Ré Flow Passed")
        test_fazenda_autora_flow()
        print("✓ Fazenda Autora Flow Passed")
        test_instance_logic()
        print("✓ Instance Logic Passed")
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test Failed: {e}")
    except Exception as e:
        print(f"Error: {e}")
