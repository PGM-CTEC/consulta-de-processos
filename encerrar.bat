@echo off
chcp 65001 >nul 2>&1
title Encerrar Consulta Processual

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   ENCERRANDO CONSULTA PROCESSUAL     ║
echo  ╚══════════════════════════════════════╝
echo.

REM ── Definir diretório base ──────────────────────────────────────
set BASE=%~dp0
cd /d "%BASE%"

REM ── Encerrar processos nas portas 8000 e 5173 ───────────────────
echo  [1/2] Encerrando processos nas portas 8000 e 5173...

REM Tentar encerrar por título de janela primeiro (mais limpo)
taskkill /FI "WINDOWTITLE eq Backend - Consulta Processual" /T >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend - Consulta Processual" /T >nul 2>&1

REM Depois encerrar por porta (mais robusto, caso o título não funcione)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R " :8000 .*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R " :5173 .*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 1 /nobreak >nul
echo        OK

REM ── Finalizando ─────────────────────────────────────────────────
echo  [2/2] Finalizando...
echo        OK

echo.
echo  ┌────────────────────────────────────────┐
echo  │  ✓ Aplicacao encerrada com sucesso     │
echo  │                                        │
echo  │  Use ./iniciar.bat para reiniciar      │
echo  └────────────────────────────────────────┘
echo.

timeout /t 3 /nobreak >nul
exit
