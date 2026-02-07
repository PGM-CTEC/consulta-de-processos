import sys
import os
sys.path.append(os.path.abspath('backend'))

from services.phase_analyzer import PhaseAnalyzer

def verify():
    # Mock data for a "Procedimento Comum" with "Sentença"
    result = PhaseAnalyzer.analyze(
        class_code=7,
        movements=[
             {'codigo': 246, 'dataHora': '2025-01-01T10:00:00', 'nome': 'Sentença'},
             {'codigo': 26, 'dataHora': '2024-01-01T10:00:00', 'nome': 'Distribuição'}
        ],
        tribunal="TJRJ"
    )
    print(f"ANALYZER OUTPUT: {result}")
    
    if "Conhecimento" in result and "02" in result:
        print("VERIFICATION PASSED: New format detected.")
    else:
        print("VERIFICATION FAILED: Output does not match new format.")

if __name__ == "__main__":
    verify()
