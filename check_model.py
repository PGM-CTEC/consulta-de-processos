#!/usr/bin/env python
"""Check process model and raw_data for fase field."""
import json
import sys
sys.path.insert(0, '.')

from backend.database import SessionLocal
from backend import models

db = SessionLocal()
processo = db.query(models.Process).filter(models.Process.number == '0029123-13.2015.8.19.0002').first()

print(f"Processo: {processo.number}")
print(f"Fase no modelo: {repr(processo.phase)}")
print(f"\nCampos no modelo Process:")
for column in models.Process.__table__.columns:
    print(f"  - {column.name}")

# Check raw_data for any 'fase' related field
if processo.raw_data:
    print("\nVerificando raw_data para campos relacionados a 'fase':")
    for key, value in processo.raw_data.items():
        if 'fase' in key.lower():
            print(f"  {key}: {value}")

    # Save raw_data to file for inspection
    with open('raw_data_debug.json', 'w', encoding='utf-8') as f:
        json.dump(processo.raw_data, f, ensure_ascii=False, indent=2)
    print("\nRaw data saved to raw_data_debug.json")

db.close()
