import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_detect_cookie_endpoint_exists():
    """Testa se o endpoint /fusion/detect-cookie existe (deve retornar 200 ou erro real, não 404)"""
    response = client.post('/fusion/detect-cookie')
    # O endpoint deve existir (não 404)
    assert response.status_code in [200, 400, 503, 500], f"Endpoint retornou {response.status_code}"
    # Resposta deve ter 'success' ou 'error'
    data = response.json()
    assert 'success' in data or 'error' in data

def test_detect_cookie_success_basic():
    """Testa estrutura de resposta quando sucesso"""
    # Este teste será melhorado quando o endpoint estiver implementado
    response = client.post('/fusion/detect-cookie')
    if response.status_code == 200:
        data = response.json()
        assert data.get('success') is True
        assert 'message' in data or 'jsessionid' in data

def test_detect_cookie_error_structure():
    """Testa estrutura de resposta quando erro"""
    response = client.post('/fusion/detect-cookie')
    if response.status_code >= 400:
        data = response.json()
        assert 'error' in data or 'success' in data
