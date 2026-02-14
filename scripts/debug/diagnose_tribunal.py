import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def diagnose_tribunal():
    api_key = os.getenv("DATAJUD_API_KEY")
    # Number: 0001745-93.1989.8.19.0002 -> TJRJ
    # Path: /{alias}/_search
    
    number = "00017459319898190002"
    
    # Try different URL candidates
    urls = [
        "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search",
        "https://api-publica.datajud.cnj.jus.br/api_publica_cnj/_search"
    ]
    
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
        
        for url in urls:
            print(f"--- Testing URL: {url} ---")
            try:
                resp = await client.post(url, json=payload, headers=headers, timeout=10.0)
                print(f"Status: {resp.status_code}")
                print(f"Response snippet: {resp.text[:500]}")
            except Exception as e:
                print(f"Exception: {e}")
            print("\n")

if __name__ == "__main__":
    asyncio.run(diagnose_tribunal())
