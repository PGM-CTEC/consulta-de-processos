#!/usr/bin/env python
"""Check process phase and movements."""
import json
import sys
sys.path.insert(0, '.')

from backend.database import SessionLocal
from backend import models

db = SessionLocal()
processo = db.query(models.Process).filter(models.Process.number == '0029123-13.2015.8.19.0002').first()

if processo:
    print(f'Processo: {processo.number}')
    print(f'Fase atual: {processo.phase}')
    print(f'Classe: {processo.class_nature}')
    print(f'Tribunal: {processo.court}')
    
    # Get movements
    movements = db.query(models.Movement).filter(models.Movement.process_id == processo.id).order_by(models.Movement.date).all()
    print(f'\nTotal de movimentos: {len(movements)}')
    print('\nÚltimos 10 movimentos:')
    for m in movements[-10:]:
        print(f'  {m.date}: [{m.code}] {m.description[:60]}')
    
    # Analyze using PhaseAnalyzer
    if processo.raw_data:
        from backend.services.phase_analyzer import PhaseAnalyzer
        data = processo.raw_data
        class_node = data.get('classe', {})
        class_code = class_node.get('codigo')
        movements_data = data.get('movimentos', [])
        
        nova_fase = PhaseAnalyzer.analyze(
            class_code=class_code,
            movements=movements_data,
            tribunal=data.get('tribunal', ''),
            grau=data.get('grau', 'G1'),
            process_number=processo.number,
            raw_data=data
        )
        print(f'\n>>> Nova fase calculada: {nova_fase}')
        
        # Update if different
        if nova_fase != processo.phase:
            print(f'>>> CORRIGINDO fase de "{processo.phase}" para "{nova_fase}"')
            processo.phase = nova_fase
            db.commit()
            print('>>> Fase corrigida com sucesso!')
        else:
            print('>>> Fase já está correta.')
else:
    print('Processo não encontrado!')

db.close()
