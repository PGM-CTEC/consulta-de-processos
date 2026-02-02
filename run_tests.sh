#!/bin/bash
# Script para executar testes do backend

echo "========================================"
echo "Consulta Processual - Test Suite"
echo "========================================"
echo ""

echo "[1/3] Verificando dependências..."
cd backend
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências"
    exit 1
fi
echo "✓ Dependências OK"
echo ""

echo "[2/3] Executando testes..."
pytest tests/ -v --tb=short -p no:asyncio
TEST_RESULT=$?
echo ""

if [ $TEST_RESULT -eq 0 ]; then
    echo "========================================"
    echo "✓ TODOS OS TESTES PASSARAM!"
    echo "========================================"
    echo ""
    echo "Próximos passos:"
    echo "1. Iniciar backend: uvicorn main:app --reload --port 8010"
    echo "2. Iniciar frontend: cd frontend && npm run dev"
    echo "3. Testar aplicação em http://localhost:5173"
    echo ""
else
    echo "========================================"
    echo "✗ ALGUNS TESTES FALHARAM"
    echo "========================================"
    echo ""
    echo "Execute novamente com mais detalhes:"
    echo "pytest tests/ -vv -s"
    echo ""
fi

cd ..
exit $TEST_RESULT
