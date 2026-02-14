import asyncio
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_datajud_direct():
    # Allow overriding key for test
    api_key = os.getenv("DATAJUD_API_KEY", "")
    base_url = "https://api-publica.datajud.cnj.jus.br/api_publica_cnj/v1"
    
    # Processo fornecido pelo usuario
    process_number = "0001745-93.1989.8.19.0002"
    clean_number = "".join(filter(str.isdigit, process_number))
    
    print(f"Testing DataJud API for: {process_number} (Clean: {clean_number})")
    print(f"API Key present: {bool(api_key)}")

    headers = {
        "Authorization": f"APIKey {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "numeroProcesso": clean_number
    }

    async with httpx.AsyncClient() as client:
        try:
            print("Sending request...")
            response = await client.post(
                f"{base_url}/processo/consultar", 
                json=payload, 
                headers=headers,
                timeout=30.0
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}...") # Print first 500 chars
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_datajud_direct())
