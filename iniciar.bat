@echo off
chcp 65001 >nul 2>&1
title Consulta Processual

echo.
echo  ╔══════════════════════════════════════╗
echo  ║       CONSULTA PROCESSUAL            ║
echo  ╚══════════════════════════════════════╝
echo.

REM ── Verificações de pré-requisito ─────────────────────────────
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [ERRO] Python nao encontrado. Instale o Python 3.11+ e tente novamente.
    pause & exit /b 1
)

node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [ERRO] Node.js nao encontrado. Instale o Node.js 18+ e tente novamente.
    pause & exit /b 1
)

REM ── Definir diretório base ──────────────────────────────────────
set BASE=%~dp0
cd /d "%BASE%"

REM ── Encerrar instâncias anteriores nas portas 8000 e 5173 ───────
echo  [0/3] Encerrando processos anteriores nas portas 8000 e 5173...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R " :8000 .*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R " :5173 .*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul
echo        OK

REM ── Backend: instalar dependências se necessário ───────────────
echo  [1/3] Verificando dependencias do backend...
pip show fastapi >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo        Instalando dependencias...
    pip install -r backend\requirements.txt -q
    if %ERRORLEVEL% NEQ 0 (
        echo  [ERRO] Falha ao instalar dependencias do backend.
        pause & exit /b 1
    )
)
echo        OK

REM ── Frontend: instalar dependências se necessário ──────────────
echo  [2/3] Verificando dependencias do frontend...
if not exist "frontend\node_modules\" (
    echo        Instalando dependencias...
    cd /d "%BASE%frontend"
    npm install --silent
    if %ERRORLEVEL% NEQ 0 (
        echo  [ERRO] Falha ao instalar dependencias do frontend.
        pause & exit /b 1
    )
    cd /d "%BASE%"
)
echo        OK

REM ── Iniciar servidores ─────────────────────────────────────────
echo  [3/3] Iniciando servidores...
echo.

start "Backend - Consulta Processual" /MIN /D "%BASE%" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

REM ── Aguardar backend estar pronto (max 30s) ─────────────────────
echo  Aguardando backend...
set /a TRIES=0
:wait_backend
timeout /t 1 /nobreak >nul
set /a TRIES+=1
powershell -command "try { $r = Invoke-WebRequest http://localhost:8000/health -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop; exit 0 } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto backend_ready
if %TRIES% GEQ 30 (
    echo  [ERRO] Backend nao respondeu em 30s. Verifique a janela do backend.
    pause & exit /b 1
)
goto wait_backend
:backend_ready
echo  Backend pronto!

start "Frontend - Consulta Processual" /MIN /D "%BASE%frontend" cmd /k "npm run dev"

REM ── Aguardar frontend estar pronto (max 30s) ────────────────────
echo  Aguardando frontend...
set /a TRIES=0
:wait_frontend
timeout /t 1 /nobreak >nul
set /a TRIES+=1
powershell -command "try { $r = Invoke-WebRequest http://localhost:5173 -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop; exit 0 } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto frontend_ready
if %TRIES% GEQ 30 (
    echo  [AVISO] Frontend nao respondeu em 30s. Abrindo mesmo assim...
    goto open_browser
)
goto wait_frontend
:frontend_ready
echo  Frontend pronto!

:open_browser
echo.
echo  ┌──────────────────────────────────────┐
echo  │  Backend:   http://localhost:8000    │
echo  │  Frontend:  http://localhost:5173    │
echo  │                                      │
echo  │  Feche as janelas para encerrar.     │
echo  └──────────────────────────────────────┘
echo.

start "" "http://localhost:5173"

echo  Aplicacao iniciada. Esta janela pode ser fechada.
timeout /t 5 /nobreak >nul
exit
