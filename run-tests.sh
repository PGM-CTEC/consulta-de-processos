#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT=$(pwd)
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${YELLOW}=== Iniciando Backend (FastAPI) ===${NC}"
cd "$PROJECT_ROOT"
source backend/venv/Scripts/activate
# Executar como módulo do pacote pai para que imports relativos funcionem
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}Backend iniciado com PID $BACKEND_PID${NC}"
sleep 6

echo -e "${YELLOW}=== Iniciando Frontend (Vite Dev Server) ===${NC}"
cd "$FRONTEND_DIR"
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend iniciado com PID $FRONTEND_PID${NC}"
sleep 5

echo -e "${YELLOW}=== Rodando Testes E2E ===${NC}"
npm run test:e2e
TEST_RESULT=$?

echo -e "${YELLOW}=== Limpando ===${NC}"
kill $BACKEND_PID 2>/dev/null || true
kill $FRONTEND_PID 2>/dev/null || true

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Todos os testes passaram!${NC}"
else
    echo -e "${RED}✗ Alguns testes falharam${NC}"
fi

exit $TEST_RESULT
