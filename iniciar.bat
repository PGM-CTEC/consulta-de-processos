@echo off
setlocal

REM ── Detectar modo debug ─────────────────────────────────────────
set "ARGS="
if "%1"=="--debug" set "ARGS=-Debug"

REM ── Executar via PowerShell ─────────────────────────────────────
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" %ARGS%

REM ── Manter janela aberta se houve erro ──────────────────────────
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  Script encerrado com erro %ERRORLEVEL%.
    pause
)
