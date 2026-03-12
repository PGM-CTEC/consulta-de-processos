#!/bin/bash
# Inicia o backend FastAPI corretamente com cleanup de porta

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Matar qualquer processo Python/uvicorn existente na porta 8000
echo "[INFO] Limpando processos na porta 8000..."
# Tenta matar via netstat + taskkill no Windows
powershell.exe -Command "
    \$port = 8000
    \$conn = netstat -ano | Select-String \":\$port\" | Select-String 'LISTENING'
    if (\$conn) {
        \$pid = (\$conn -split '\s+')[-1]
        if (\$pid -match '^\d+$') {
            Write-Host \"Matando processo PID \$pid na porta \$port\"
            taskkill /F /PID \$pid 2>null
        }
    }
" 2>/dev/null || true

sleep 2

# Verificar se a porta está livre
if netstat -ano 2>/dev/null | grep -q ":8000.*LISTENING"; then
    echo "[AVISO] Porta 8000 ainda em uso — tentando porta alternativa 8000..."
fi

echo "[INFO] Iniciando backend em http://127.0.0.1:8000 ..."
source backend/venv/Scripts/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
