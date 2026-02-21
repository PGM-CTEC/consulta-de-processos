import asyncio
from dotenv import load_dotenv

load_dotenv()

from backend.services.datajud import DataJudClient

async def _run_test_integration():
    client = DataJudClient()
    print(f"API Key from env: {client.api_key}")
    
    number = "00017459319898190002"
    print(f"Testing with cleaned number: {number}")
    
    try:
        result = await client.get_process(number)
        if result:
            print("Success! Process found.")
        else:
            print("Success! No process found (but no error).")
    except Exception as e:
        print(f"Integration Test Failed: {e}")

def test_integration():
    asyncio.run(_run_test_integration())

if __name__ == "__main__":
    asyncio.run(_run_test_integration())
