@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Consulta Processual

REM ── Modo DEBUG (opcional) ──────────────────────────────────────
set DEBUG=0
if "%1"=="--debug" set DEBUG=1

echo.
echo  ╔══════════════════════════════════════╗
echo  ║       CONSULTA PROCESSUAL            ║
echo  ╚══════════════════════════════════════╝
echo.

if %DEBUG% EQU 1 (
    echo  [DEBUG] Modo verboso ativado
    echo.
)

REM ── Verificações de pré-requisito ─────────────────────────────
if %DEBUG% EQU 1 echo  [DEBUG] Verificando Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [ERRO] Python nao encontrado. Instale o Python 3.11+ e tente novamente.
    pause & exit /b 1
)

if %DEBUG% EQU 1 echo  [DEBUG] Verificando Node.js...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [ERRO] Node.js nao encontrado. Instale o Node.js 18+ e tente novamente.
    pause & exit /b 1
)

REM ── Definir diretório base ──────────────────────────────────────
set BASE=%~dp0
cd /d "%BASE%"

if %DEBUG% EQU 1 echo  [DEBUG] Diretorio base: %BASE%

REM ── Verificar se portas estão livres antes de encerrar ─────────
if %DEBUG% EQU 1 echo  [DEBUG] Verificando ocupacao das portas...
set PORT_8000_USED=0
set PORT_5173_USED=0

for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R " :8000 .*LISTENING"') do (
    set PORT_8000_USED=1
    if %DEBUG% EQU 1 echo  [DEBUG] Porta 8000 ja em uso (PID: %%a^)
)

for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R " :5173 .*LISTENING"') do (
    set PORT_5173_USED=1
    if %DEBUG% EQU 1 echo  [DEBUG] Porta 5173 ja em uso (PID: %%a^)
)

REM ── Encerrar instâncias anteriores nas portas 8000 e 5173 ───────
echo  [0/4] Encerrando processos anteriores nas portas 8000 e 5173...
if !PORT_8000_USED! EQU 1 (
    for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R " :8000 .*LISTENING"') do (
        if %DEBUG% EQU 1 echo  [DEBUG] Matando processo PID %%a na porta 8000
        taskkill /F /PID %%a >nul 2>&1
    )
)

if !PORT_5173_USED! EQU 1 (
    for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R " :5173 .*LISTENING"') do (
        if %DEBUG% EQU 1 echo  [DEBUG] Matando processo PID %%a na porta 5173
        taskkill /F /PID %%a >nul 2>&1
    )
)

REM ── Aguardar portas ficarem livres ──────────────────────────────
if !PORT_8000_USED! EQU 1 (
    echo  Aguardando porta 8000 ficar livre...
    set /a TRIES=0
    :wait_port_8000_free
    timeout /t 1 /nobreak >nul
    set /a TRIES+=1
    netstat -ano 2>nul | findstr /R " :8000 .*LISTENING" >nul
    if %ERRORLEVEL% EQU 0 (
        if !TRIES! LSS 10 goto wait_port_8000_free
    )
)

if !PORT_5173_USED! EQU 1 (
    echo  Aguardando porta 5173 ficar livre...
    set /a TRIES=0
    :wait_port_5173_free
    timeout /t 1 /nobreak >nul
    set /a TRIES+=1
    netstat -ano 2>nul | findstr /R " :5173 .*LISTENING" >nul
    if %ERRORLEVEL% EQU 0 (
        if !TRIES! LSS 10 goto wait_port_5173_free
    )
)

echo        OK

REM ── Backend: instalar dependências se necessário ───────────────
echo  [1/4] Verificando dependencias do backend...
if %DEBUG% EQU 1 echo  [DEBUG] Procurando FastAPI...
pip show fastapi >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo        Instalando dependencias...
    if %DEBUG% EQU 1 echo  [DEBUG] Executando: pip install -r backend\requirements.txt
    pip install -r backend\requirements.txt -q
    if %ERRORLEVEL% NEQ 0 (
        echo  [ERRO] Falha ao instalar dependencias do backend.
        pause & exit /b 1
    )
)
echo        OK

REM ── Frontend: instalar dependências se necessário ──────────────
echo  [2/4] Verificando dependencias do frontend...
if not exist "frontend\node_modules\" (
    echo        Instalando dependencias...
    if %DEBUG% EQU 1 echo  [DEBUG] Instalando node_modules...
    cd /d "%BASE%frontend"
    npm install --silent
    if %ERRORLEVEL% NEQ 0 (
        echo  [ERRO] Falha ao instalar dependencias do frontend.
        cd /d "%BASE%"
        pause & exit /b 1
    )
    cd /d "%BASE%"
) else (
    if %DEBUG% EQU 1 echo  [DEBUG] node_modules ja existe
)
echo        OK

REM ── Iniciar servidores ─────────────────────────────────────────
echo  [3/4] Iniciando servidores...
echo.

if %DEBUG% EQU 1 (
    echo  [DEBUG] Iniciando backend sem /MIN (console visivel)
    start "Backend - Consulta Processual" /D "%BASE%" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
) else (
    start "Backend - Consulta Processual" /MIN /D "%BASE%" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
)

REM ── Aguardar backend estar pronto (max 30s) ─────────────────────
echo  Aguardando backend responder em http://localhost:8000/health...
set /a TRIES=0
:wait_backend
timeout /t 1 /nobreak >nul
set /a TRIES+=1

if %DEBUG% EQU 1 echo  [DEBUG] Tentativa !TRIES!/30 de conectar ao backend...

powershell -command "try { $r = Invoke-WebRequest http://localhost:8000/health -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1

if %ERRORLEVEL% EQU 0 goto backend_ready
if !TRIES! GEQ 30 (
    echo  [ERRO] Backend nao respondeu em 30s. Verifique a janela do backend.
    echo.
    echo  Use ./encerrar.bat para parar os processos e tente novamente.
    pause & exit /b 1
)
goto wait_backend

:backend_ready
echo  ✓ Backend pronto!
echo.

if %DEBUG% EQU 1 (
    echo  [DEBUG] Iniciando frontend sem /MIN (console visivel)
    start "Frontend - Consulta Processual" /D "%BASE%frontend" cmd /k "npm run dev"
) else (
    start "Frontend - Consulta Processual" /MIN /D "%BASE%frontend" cmd /k "npm run dev"
)

REM ── Aguardar frontend estar pronto (max 30s) ────────────────────
echo  Aguardando frontend responder em http://localhost:5173...
set /a TRIES=0
:wait_frontend
timeout /t 1 /nobreak >nul
set /a TRIES+=1

if %DEBUG% EQU 1 echo  [DEBUG] Tentativa !TRIES!/30 de conectar ao frontend...

powershell -command "try { $r = Invoke-WebRequest http://localhost:5173 -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1

if %ERRORLEVEL% EQU 0 goto frontend_ready
if !TRIES! GEQ 30 (
    echo  [AVISO] Frontend nao respondeu em 30s. Abrindo mesmo assim...
    goto open_browser
)
goto wait_frontend

:frontend_ready
echo  ✓ Frontend pronto!

:open_browser
echo  [4/4] Abrindo navegador...
echo.
echo  ┌─────────────────────────────────────────────┐
echo  │  ✓ APLICAÇÃO INICIADA COM SUCESSO           │
echo  │                                             │
echo  │  Frontend:  http://localhost:5173           │
echo  │  Backend:   http://localhost:8000           │
echo  │  Swagger:   http://localhost:8000/docs      │
echo  │                                             │
echo  │  Para encerrar, use: ./encerrar.bat         │
echo  │  Para debug, use:    ./iniciar.bat --debug  │
echo  └─────────────────────────────────────────────┘
echo.

if %DEBUG% EQU 1 (
    echo  [DEBUG] Abrindo frontend no navegador padrão...
)

start "" "http://localhost:5173"

echo  Aplicacao pronta para uso. Esta janela pode ser fechada.
if %DEBUG% EQU 1 (
    echo  [DEBUG] Modo DEBUG ativo - consoles visiveis
    timeout /t 10 /nobreak >nul
) else (
    timeout /t 5 /nobreak >nul
)

exit /b 0
