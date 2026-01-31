import asyncio
import sys
import os
from dotenv import load_dotenv
import logging

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# Set up logging to console
logging.basicConfig(level=logging.INFO)

from services.datajud import DataJudClient

async def test_final():
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

if __name__ == "__main__":
    asyncio.run(test_final())
