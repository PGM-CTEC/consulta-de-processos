#!/usr/bin/env python3
"""
Script para testar a validação e uso do cookie Fusion PAV
"""
import sys
sys.path.insert(0, './backend')

import asyncio
import logging
from backend.services.fusion_api_client import FusionAPIClient
from backend.config import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_cookie():
    """Testa se o cookie Fusion é válido"""

    cookie = "JSESSIONID=157C0FFC503B0892C0D8CB5EF95B8AD8"
    base_url = settings.FUSION_PAV_BASE_URL

    print(f"[TESTE] Testando cookie Fusion PAV")
    print(f"   Base URL: {base_url}")
    print(f"   Cookie: {cookie[:50]}...")
    print()

    # Criar cliente
    client = FusionAPIClient(base_url, cookie, timeout=10)

    # Testar com um número CNJ
    test_cnj = "00017456419898190002"  # Processo do teste

    try:
        print(f"[REQUISIÇÃO] Testando requisição ao Fusion com processo: {test_cnj}")
        result = await client.get_document_tree(test_cnj)

        if result:
            print(f"[SUCESSO] Processo encontrado:")
            print(f"   Classe: {result.classe_processual}")
            print(f"   Sistema: {result.sistema}")
            print(f"   Movimentos: {len(result.movimentos)}")
        else:
            print(f"[AVISO] Processo não encontrado (pode estar inativo ou não existe)")

    except Exception as e:
        print(f"[ERRO] Erro ao consultar Fusion:")
        print(f"   {type(e).__name__}: {e}")

        # Verificar tipo de erro
        if "401" in str(e) or "Unauthorized" in str(e):
            print(f"\n[AUTENTICAÇÃO] Cookie pode estar expirado ou inválido")
        elif "403" in str(e) or "Forbidden" in str(e):
            print(f"\n[PERMISSÃO] Usuário não tem acesso")
        elif "Connection" in str(e):
            print(f"\n[CONEXÃO] Verifique se o PAV está acessível")

if __name__ == "__main__":
    asyncio.run(test_cookie())
