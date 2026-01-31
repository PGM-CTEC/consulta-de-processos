import httpx
import os
import logging
from typing import Dict, Any, Optional

print("\n\n" + "#"*50)
print("LOADING DATAJUD CLIENT FROM services/datajud.py")
print("#"*50 + "\n\n")

logger = logging.getLogger(__name__)

class DataJudClient:
    def __init__(self):
        self.api_key = os.getenv("DATAJUD_API_KEY")
        
    def _get_tribunal_alias(self, process_number: str) -> str:
        """
        Determines the DataJud alias based on CNJ number segments.
        Format: NNNNNNN-DD.AAAA.J.TR.OOOO
        """
        # Remove formatting
        clean = "".join(filter(str.isdigit, process_number))
        if len(clean) != 20:
            return "api_publica_cnj" # Fallback
            
        # J is dig 13, TR is dig 14-15 (0-indexed)
        # 0001745931989 8 19 0002
        #               ^ ^
        #               13 14,15
        j = clean[13]
        tr = clean[14:16]
        
        # State mapping for J=8 (State Courts)
        # This is a simplified map; for 8.19 -> tjrj, 8.10 -> tjma
        state_map = {
            "01": "tjac", "02": "tjal", "03": "tjam", "04": "tjap", "05": "tjba",
            "06": "tjce", "07": "tjdft", "08": "tjes", "09": "tjgo", "10": "tjma",
            "11": "tjmt", "12": "tjms", "13": "tjmg", "14": "tjpa", "15": "tjpb",
            "16": "tjpr", "17": "tjpe", "18": "tjpi", "19": "tjrj", "20": "tjrn",
            "21": "tjrs", "22": "tjro", "23": "tjrr", "24": "tjsc", "25": "tjsp",
            "26": "tjse", "27": "tjto"
        }
        
        if j == "8":
            court = state_map.get(tr, "cnj")
            return f"api_publica_{court}"
        elif j == "4":
            return f"api_publica_trf{int(tr)}"
        elif j == "5":
            return f"api_publica_trt{int(tr)}"
        
        return "api_publica_cnj"

    async def get_process(self, process_number: str) -> Optional[Dict[str, Any]]:
        """
        Fetches detailed process data from DataJud API using the correct tribunal index.
        """
        alias = self._get_tribunal_alias(process_number)
        url = f"https://api-publica.datajud.cnj.jus.br/{alias}/_search"
        logger.error(f"--- ATTEMPTING REQUEST TO: {url} ---")
        
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
             headers["Authorization"] = f"APIKey {self.api_key}"
             
        # CNJ stores number WITHOUT masks in the index
        clean_number = "".join(filter(str.isdigit, process_number))
        
        print(f"\nEXECUTING REQUEST TO: {url}\n")
        
        payload = {
            "query": {
                "match": {
                    "numeroProcesso": clean_number
                }
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Requesting DataJud URL: {url}")
                logger.info(f"Payload: {payload}")
                
                response = await client.post(
                    url, 
                    json=payload, 
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"DataJud Error {response.status_code}: {response.text}")
                    
                response.raise_for_status()
                
                data = response.json()
                
                # Elasticsearch format: data["hits"]["hits"]
                if "hits" in data and "hits" in data["hits"] and len(data["hits"]["hits"]) > 0:
                     return data["hits"]["hits"][0]["_source"]
                     
                return None

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error querying DataJud: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error querying DataJud: {str(e)}")
                raise
