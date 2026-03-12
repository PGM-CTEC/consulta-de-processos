#!/usr/bin/env python3
"""
Simula a chamada de updateFusionCookie do frontend
"""
import sys
import asyncio
import json

# Testar com requests HTTP real
print("[INFO] Testando chamada HTTP do frontend para /fusion/cookie")
print()

try:
    import httpx

    async def test():
        # URL do backend
        base_url = "http://localhost:8000"
        endpoint = f"{base_url}/fusion/cookie"

        # Payload igual ao do frontend
        cookie = "JSESSIONID=157C0FFC503B0892C0D8CB5EF95B8AD8"
        payload = {"cookie": cookie}

        print(f"[REQUEST] PATCH {endpoint}")
        print(f"[PAYLOAD] {json.dumps(payload)}")
        print()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(
                    endpoint,
                    json=payload,
                    timeout=10.0
                )

                print(f"[STATUS] HTTP {response.status_code}")
                print(f"[RESPONSE]")
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print()
                        print("[SUCESSO] Cookie atualizado!")
                    else:
                        print()
                        print(f"[ERRO] {data.get('message')}")

            except Exception as e:
                print(f"[ERRO HTTP] {type(e).__name__}: {e}")
                print()
                print("Possíveis causas:")
                print("1. Backend não está rodando")
                print("2. URL/porta incorreta")
                print("3. Problema de conexão")

    asyncio.run(test())

except ImportError:
    print("[INFO] httpx não instalado, usando curl como alternativa")
    import subprocess

    cookie = "JSESSIONID=157C0FFC503B0892C0D8CB5EF95B8AD8"
    cmd = [
        "curl", "-X", "PATCH",
        "http://localhost:8000/fusion/cookie",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"cookie": cookie}),
        "-v"
    ]

    print(f"[COMANDO] {' '.join(cmd)}")
    print()
    subprocess.run(cmd)
