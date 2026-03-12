#!/usr/bin/env python3
"""
Teste do endpoint /fusion/cookie
"""
import sys
sys.path.insert(0, './backend')

from backend.services.dependency_container import update_fusion_cookie, get_fusion_service
from backend.config import settings

print("[INFO] Testando atualização de cookie")
print(f"[INFO] Fusion API configurado? {settings.fusion_api_configured}")
print()

# Tentar atualizar o cookie
cookie = "JSESSIONID=157C0FFC503B0892C0D8CB5EF95B8AD8"

try:
    print(f"[TENTATIVA] Atualizando cookie: {cookie[:50]}...")

    # Validar cookie (mesmo que o endpoint faz)
    if not cookie:
        raise ValueError("Cookie não informado.")
    if "JSESSIONID" not in cookie:
        raise ValueError("Cookie inválido — deve conter JSESSIONID.")

    # Chamar função de atualização
    update_fusion_cookie(cookie)

    # Verificar se foi atualizado
    fusion_service = get_fusion_service()
    if fusion_service:
        print(f"[SUCESSO] Cookie atualizado!")
        print(f"[INFO] FusionService inicializado")
        print(f"[INFO] Cookie armazenado: {fusion_service._api_client.session_cookie[:50] if fusion_service._api_client else 'N/A'}...")
    else:
        print(f"[AVISO] FusionService não inicializado")

except Exception as e:
    print(f"[ERRO] Falha ao atualizar cookie:")
    print(f"       {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
