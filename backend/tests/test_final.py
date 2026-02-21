import asyncio
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up logging to console
logging.basicConfig(level=logging.INFO)

from backend.services.datajud import DataJudClient

async def _run_test_final():
    client = DataJudClient()
    number = "0001745-93.1989.8.19.0002"
    print(f"Testing client logic for: {number}")
    try:
        data = await client.get_process(number)
        if data:
            print("SUCCESS: Data retrieved!")
            print(f"Keys found: {data.keys()}")
        else:
            print("FAILURE: No data found.")
    except Exception as e:
        print(f"EXCEPTION: {e}")

def test_final():
    asyncio.run(_run_test_final())

if __name__ == "__main__":
    asyncio.run(_run_test_final())
