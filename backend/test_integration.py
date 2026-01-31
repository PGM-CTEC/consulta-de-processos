import asyncio
import sys
import os
from dotenv import load_dotenv

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from services.datajud import DataJudClient

async def test_integration():
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

if __name__ == "__main__":
    asyncio.run(test_integration())
