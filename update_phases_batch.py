"""
Script para atualizar as fases de todos os processos no banco de dados
usando as novas regras de classificação.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from services.phase_analyzer import PhaseAnalyzer

DATABASE_URL = "sqlite:///consulta_processual.db"

def update_all_phases():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        processes = session.query(models.Process).all()
        total = len(processes)
        updated = 0
        errors = 0
        
        print(f"Encontrados {total} processos para atualizar...")
        print("-" * 50)
        
        for i, process in enumerate(processes, 1):
            try:
                raw_data = process.raw_data or {}
                
                # Extract class code
                class_node = raw_data.get('classe', {})
                class_code = class_node.get('codigo', 0)
                
                # Extract movements
                movements = raw_data.get('movimentos', [])
                
                # Get tribunal and grau
                tribunal = raw_data.get('tribunal', '')
                grau = raw_data.get('grau', 'G1')
                
                # Run new classification
                new_phase = PhaseAnalyzer.analyze(
                    class_code=class_code,
                    movements=movements,
                    tribunal=tribunal,
                    grau=grau,
                    process_number=process.number,
                    raw_data=raw_data
                )
                
                old_phase = process.phase
                if old_phase != new_phase:
                    process.phase = new_phase
                    updated += 1
                    print(f"[{i}/{total}] {process.number}")
                    print(f"  Antes: {old_phase}")
                    print(f"  Depois: {new_phase}")
                else:
                    print(f"[{i}/{total}] {process.number} - Sem alteração")
                    
            except Exception as e:
                errors += 1
                print(f"[{i}/{total}] ERRO em {process.number}: {e}")
        
        session.commit()
        
        print("-" * 50)
        print(f"Atualização concluída!")
        print(f"  Total: {total}")
        print(f"  Atualizados: {updated}")
        print(f"  Erros: {errors}")
        
    except Exception as e:
        session.rollback()
        print(f"Erro geral: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    update_all_phases()
