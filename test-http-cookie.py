#!/usr/bin/env python3
"""
Teste do endpoint HTTP /fusion/cookie
Simula exatamente o que um cliente HTTP faria
"""
import sys
sys.path.insert(0, './backend')

import asyncio
import json
from fastapi.testclient import TestClient
from backend.main import app

print("[INFO] Testando endpoint HTTP /fusion/cookie")
print()

# Criar cliente de teste
client = TestClient(app)

# Payload
cookie = "JSESSIONID=157C0FFC503B0892C0D8CB5EF95B8AD8"
payload = {"cookie": cookie}

try:
    print(f"[REQUISIÇÃO] PATCH /fusion/cookie")
    print(f"[PAYLOAD] {json.dumps(payload)}")
    print()

    # Fazer requisição
    response = client.patch("/fusion/cookie", json=payload)

    print(f"[RESPOSTA] Status: {response.status_code}")
    print(f"[RESPOSTA] Corpo:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    if response.status_code == 200:
        print()
        print("[SUCESSO] Cookie atualizado com sucesso!")
    else:
        print()
        print(f"[ERRO] Falha ao atualizar cookie (HTTP {response.status_code})")

except Exception as e:
    print(f"[ERRO CRÍTICO] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
