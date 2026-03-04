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

start "Backend - Consulta Processual" /MIN /D "%BASE%" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

start "Frontend - Consulta Processual" /MIN /D "%BASE%frontend" cmd /k "npm run dev"

timeout /t 4 /nobreak >nul

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
