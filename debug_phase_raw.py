#!/usr/bin/env python
"""Debug the phase classification from raw_data."""
import json
import sys
sys.path.insert(0, '.')

from backend.database import SessionLocal
from backend import models

db = SessionLocal()
processo = db.query(models.Process).filter(models.Process.number == '0029123-13.2015.8.19.0002').first()

if processo and processo.raw_data:
    data = processo.raw_data
    print("Keys no raw_data:")
    for key in data.keys():
        print(f"  - {key}")
    
    # Check for 'fase' field
    if 'fase' in data:
        print(f"\nFase no raw_data: {data['fase']}")
    
    if 'movimentos' in data:
        movs = data['movimentos']
        print(f"\nTotal movimentos no raw_data: {len(movs)}")
        
    # Check class
    class_node = data.get('classe', {})
    class_code = class_node.get('codigo')
    print(f"\nClasse código: {class_code}")
    print(f"Classe nome: {class_node.get('nome')}")

db.close()
