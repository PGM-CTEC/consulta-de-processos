import asyncio
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
sys.path.append(str(project_root))
load_dotenv()

from backend.services.datajud import DataJudClient

async def inspect_data():
    client = DataJudClient()
    number = "0001745-93.1989.8.19.0002"
    print(f"Fetching raw data for: {number}")
    try:
        data = await client.get_process(number)
        if data:
            # Save to file for easy reading
            with open("raw_datajud_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Response saved to raw_datajud_response.json")
            
            # Print key fields to console for quick check
            print("\n--- Structure Preview ---")
            print(f"Keys: {list(data.keys())}")
            if "dadosBasicos" in data:
                print(f"dadosBasicos keys: {list(data['dadosBasicos'].keys())}")
            
            if "movimentos" in data and len(data["movimentos"]) > 0:
                print(f"First Movement keys: {list(data['movimentos'][0].keys())}")
                print(f"First Movement content: {data['movimentos'][0]}")
        else:
            print("No data found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_data())
