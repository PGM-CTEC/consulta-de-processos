param([switch]$Debug)

$ErrorActionPreference = "Continue"
$BASE = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BASE

# Cabecalho
Clear-Host
Write-Host ""
Write-Host "  === CONSULTA PROCESSUAL ===" -ForegroundColor Cyan
Write-Host ""

function Write-Step($num, $msg) {
    Write-Host "  [$num] $msg..." -ForegroundColor Yellow
}
function Write-OK($msg) {
    Write-Host "       OK - $msg" -ForegroundColor Green
}
function Write-Fail($msg) {
    Write-Host ""
    Write-Host "  [ERRO] $msg" -ForegroundColor Red
    Write-Host ""
    Read-Host "  Pressione Enter para sair"
    exit 1
}

# Verificar pre-requisitos
Write-Step "0/4" "Verificando pre-requisitos"

$pyTest = python --version 2>&1
if ($LASTEXITCODE -ne 0) { Write-Fail "Python nao encontrado. Instale Python 3.11+" }

$ndTest = node --version 2>&1
if ($LASTEXITCODE -ne 0) { Write-Fail "Node.js nao encontrado. Instale Node.js 18+" }

if (-not (Test-Path ".env")) { Write-Fail "Arquivo .env nao encontrado. Copie .env.example para .env" }
if (-not (Test-Path "backend\main.py")) { Write-Fail "backend\main.py nao encontrado" }
if (-not (Test-Path "frontend\package.json")) { Write-Fail "frontend\package.json nao encontrado" }
if (-not (Test-Path "backend\requirements.txt")) { Write-Fail "backend\requirements.txt nao encontrado" }

Write-OK "Python $pyTest, Node $ndTest"
Write-Host ""

# Matar processos anteriores
Write-Step "1/4" "Encerrando processos anteriores (portas 8000 e 5173)"

@(8000, 5173) | ForEach-Object {
    $port = $_
    $result = netstat -ano 2>$null | Select-String ":$port\s.*LISTENING"
    if ($result) {
        $pid_ = ($result.ToString().Trim() -split '\s+')[-1]
        if ($Debug) { Write-Host "       [DEBUG] Matando PID $pid_ na porta $port" -ForegroundColor Gray }
        try { Stop-Process -Id $pid_ -Force -ErrorAction SilentlyContinue } catch {}
        Start-Sleep -Seconds 1
    }
}

Write-OK "Portas liberadas"
Write-Host ""

# Dependencias backend
Write-Step "2/4" "Verificando dependencias do backend (pip)"

pip install -r backend\requirements.txt -q 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    pip install -r backend\requirements.txt
    Write-Fail "Falha ao instalar dependencias. Rode: pip install -r backend\requirements.txt"
}

Write-OK "Dependencias Python OK"
Write-Host ""

# Dependencias frontend
Write-Step "3/4" "Verificando dependencias do frontend (npm)"

Set-Location "$BASE\frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "       Instalando node_modules (primeira vez, pode demorar)..." -ForegroundColor Gray
}
$npmOut = npm install --legacy-peer-deps --silent 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ($npmOut | Out-String) -ForegroundColor Red
    Write-Fail "Falha no npm install. Rode: cd frontend && npm install --legacy-peer-deps"
}
Set-Location $BASE

Write-OK "Dependencias Node.js OK"
Write-Host ""

# Iniciar servidores
Write-Step "4/4" "Iniciando servidores"
Write-Host ""

# Backend
$winStyle = if ($Debug) { "Normal" } else { "Minimized" }
$backendProc = Start-Process -FilePath "cmd" `
    -ArgumentList "/k python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000" `
    -WorkingDirectory $BASE `
    -WindowStyle $winStyle `
    -PassThru

Write-Host "  Backend iniciado (PID: $($backendProc.Id))" -ForegroundColor Gray

# Aguardar backend
Write-Host "  Aguardando backend em http://localhost:8000/health..." -ForegroundColor Gray
$tries = 0
$backendOK = $false
while ($tries -lt 30) {
    Start-Sleep -Seconds 1
    $tries++
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $backendOK = $true; break }
    } catch {}
    if ($Debug) { Write-Host "  [DEBUG] Backend tentativa $tries/30..." -ForegroundColor Gray }
}

if (-not $backendOK) {
    Write-Host ""
    Write-Host "  [ERRO] Backend nao respondeu em 30s." -ForegroundColor Red
    Write-Host "  Verifique a janela do backend para erros." -ForegroundColor Yellow
    Write-Host "  Ou rode manualmente: python -m uvicorn backend.main:app --port 8000" -ForegroundColor Yellow
    Read-Host "  Pressione Enter para sair"
    exit 1
}
Write-Host "  Backend pronto em ${tries}s!" -ForegroundColor Green
Write-Host ""

# Frontend
$frontendProc = Start-Process -FilePath "cmd" `
    -ArgumentList "/k npm run dev" `
    -WorkingDirectory "$BASE\frontend" `
    -WindowStyle $winStyle `
    -PassThru

Write-Host "  Frontend iniciado (PID: $($frontendProc.Id))" -ForegroundColor Gray

# Aguardar frontend
Write-Host "  Aguardando frontend em http://localhost:5173..." -ForegroundColor Gray
$tries = 0
$frontendOK = $false
while ($tries -lt 60) {
    Start-Sleep -Seconds 1
    $tries++
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $frontendOK = $true; break }
    } catch {}
    if ($Debug) { Write-Host "  [DEBUG] Frontend tentativa $tries/60..." -ForegroundColor Gray }
}

if (-not $frontendOK) {
    Write-Host "  [AVISO] Frontend nao respondeu em 60s - abrindo mesmo assim..." -ForegroundColor Yellow
} else {
    Write-Host "  Frontend pronto em ${tries}s!" -ForegroundColor Green
}

# Abrir navegador
Write-Host ""
Start-Process "http://localhost:5173"

# Resumo final
Write-Host ""
Write-Host "  =============================================" -ForegroundColor Cyan
Write-Host "  APLICACAO INICIADA COM SUCESSO" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  Swagger:   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Para encerrar use: ./encerrar.bat" -ForegroundColor Gray
Write-Host "  Para debug use:    ./iniciar.bat --debug" -ForegroundColor Gray
Write-Host "  =============================================" -ForegroundColor Cyan
Write-Host ""
