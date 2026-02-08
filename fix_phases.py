#!/usr/bin/env python
"""Corrige a fase do processo no banco de dados."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend import models
from backend.services.phase_analyzer import PhaseAnalyzer

def corrigir_fase_processos():
    """Corrige fases de processos de Cumprimento de Sentença."""
    
    db = SessionLocal()
    
    print("=" * 70)
    print("CORREÇÃO DE FASES DE PROCESSOS")
    print("=" * 70)
    
    # Buscar todos os processos
    processos = db.query(models.Process).all()
    
    corrigidos = 0
    erros = 0
    
    for processo in processos:
        if not processo.raw_data:
            continue
        
        data = processo.raw_data
        class_node = data.get("classe", {})
        class_code = class_node.get("codigo")
        class_name = class_node.get("nome", "")
        
        # Verificar se é classe de execução
        classes_execucao = {1116, 156, 12078, 159, 229, 1727, 165}
        
        if class_code in classes_execucao:
            movements_data = data.get("movimentos", [])
            
            # Chamar PhaseAnalyzer
            nova_fase = PhaseAnalyzer.analyze(
                class_code=class_code,
                movements=movements_data,
                tribunal=data.get("tribunal", ""),
                grau=data.get("grau", "G1"),
                process_number=processo.number,
                raw_data=data
            )
            
            fase_atual = processo.phase or ""
            
            # Verificar se a fase atual está errada
            if "10 Execução" not in fase_atual and "Execução" not in fase_atual:
                print(f"\n>>> CORRIGINDO: {processo.number}")
                print(f"    Classe: {class_name} ({class_code})")
                print(f"    Fase anterior: {fase_atual}")
                print(f"    Nova fase: {nova_fase}")
                
                processo.phase = nova_fase
                corrigidos += 1
            else:
                print(f"OK: {processo.number} - Ja esta correto: {fase_atual}")
    
    db.commit()
    
    print("\n" + "=" * 70)
    print(f"RESUMO:")
    print(f"  Total de processos verificados: {len(processos)}")
    print(f"  Processos corrigidos: {corrigidos}")
    print(f"  Erros: {erros}")
    print("=" * 70)
    
    db.close()

if __name__ == '__main__':
    corrigir_fase_processos()
