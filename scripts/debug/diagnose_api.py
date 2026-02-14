import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def diagnose():
    api_key = os.getenv("DATAJUD_API_KEY")
    url = "https://api-publica.datajud.cnj.jus.br/api_publica_cnj/_search"
    
    number = "00017459319898190002"
    
    payload = {
        "query": {
            "match": {
                "numeroProcesso": number
            }
        }
    }

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"APIKey {api_key}",
            "Content-Type": "application/json"
        }
        print(f"Testing URL: {url}")
        try:
            resp = await client.post(url, json=payload, headers=headers, timeout=10.0)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
