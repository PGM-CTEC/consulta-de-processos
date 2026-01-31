import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from services.datajud import DataJudClient

async def inspect():
    client = DataJudClient()
    number = "0001745-93.1989.8.19.0002"
    print(f"Fetching for: {number}")
    data = await client.get_process(number)
    if data:
        print("KEYS:", list(data.keys()))
        print("CLASSE:", data.get("classe"))
        print("TRIBUNAL:", data.get("tribunal"))
        print("ASSUNTOS:", data.get("assuntos"))
        print("ORGAO:", data.get("orgaoJulgador"))
        # Save sample
        with open("sample_source.json", "w") as f:
            json.dump(data, f, indent=2)
    else:
        print("NO DATA")

if __name__ == "__main__":
    asyncio.run(inspect())
