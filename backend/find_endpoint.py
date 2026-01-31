import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def find_correct_endpoint():
    api_key = os.getenv("DATAJUD_API_KEY")
    variants = [
        "api_publica_tjrj",
        "tjrj",
        "api_publica_cnj",
        "api_publica_v1_tjrj",
        "tjrj_pje",
        "api_publica_tjrj_pje"
    ]
    
    number = "00017459319898190002"
    payload = {"query": {"match": {"numeroProcesso": number}}}
    headers = {"Authorization": f"APIKey {api_key}", "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        for v in variants:
            url = f"https://api-publica.datajud.cnj.jus.br/{v}/_search"
            print(f"Testing: {url}")
            try:
                resp = await client.post(url, json=payload, headers=headers, timeout=5.0)
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"SUCCESS with index: {v}")
                    return
                elif resp.status_code == 400:
                    print(f"Bad Request: {resp.text[:200]}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(find_correct_endpoint())
