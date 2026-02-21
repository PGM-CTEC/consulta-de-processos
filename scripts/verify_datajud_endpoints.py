import asyncio
import httpx
import sys
import os

# Adiciona o diretório raiz ao path para importar módulos do backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.config import settings

async def verify_endpoint(client, alias: str, name: str):
    url = f"{settings.DATAJUD_BASE_URL}/{alias}/_search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"APIKey {settings.DATAJUD_API_KEY}"
    }
    # Payload vazio ou busca genérica para testar conectividade/autenticação
    # Usando uma query que provavelmente não retorna nada, mas valida o endpoint
    payload = {
        "query": {"match_all": {}},
        "size": 1
    }

    try:
        response = await client.post(url, json=payload, headers=headers, timeout=10.0)
        
        status = "OK" if response.status_code == 200 else f"ERRO ({response.status_code})"
        print(f"[{status}] {name} ({alias})")
        
        if response.status_code != 200:
             print(f"    Detalhes: {response.text[:200]}")
             return False
        return True

    except Exception as e:
        print(f"[FALHA] {name} ({alias}): {str(e)}")
        return False

async def main():
    print("=== Verificação de Endpoints DataJud ===\n")
    
    # Lista de endpoints para testar
    # Baseado na documentação do DataJudClient e mapeamento comum
    endpoints = [
        ("api_publica_cnj", "CNJ (Conselho Nacional de Justiça)"),
        ("api_publica_tst", "TST (Tribunal Superior do Trabalho)"),
        ("api_publica_stm", "STM (Superior Tribunal Militar)"),
        ("api_publica_tjrj", "TJRJ (Rio de Janeiro)"),
        ("api_publica_tjsp", "TJSP (São Paulo)"),
        ("api_publica_tjmg", "TJMG (Minas Gerais)"),
        ("api_publica_trf1", "TRF1 (Federal Região 1)"),
        ("api_publica_trf2", "TRF2 (Federal Região 2)"),
        ("api_publica_trt1", "TRT1 (Trabalho Rio de Janeiro)"),
        ("api_publica_trt2", "TRT2 (Trabalho São Paulo)"),
    ]

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(verify_endpoint(client, alias, name) for alias, name in endpoints))
    
    print("\n=== Resumo ===")
    success_count = sum(results)
    print(f"Sucesso: {success_count}/{len(endpoints)}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
