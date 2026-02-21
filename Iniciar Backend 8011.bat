@echo off
setlocal

title Consulta Processual - Backend 8011

REM Vai para a pasta raiz do projeto
cd /d "%~dp0"

REM Resolve o Python instalado (prioriza py launcher)
set "PY_CMD="
where py >nul 2>&1
if %errorlevel%==0 (
    set "PY_CMD=py -3"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        set "PY_CMD=python"
    )
)

if "%PY_CMD%"=="" (
    echo [ERRO] Python nao encontrado no PATH.
    pause
    exit /b 1
)

echo Iniciando backend em http://127.0.0.1:8011
echo Comando: %PY_CMD% -m uvicorn backend.main:app --host 127.0.0.1 --port 8011

%PY_CMD% -m uvicorn backend.main:app --host 127.0.0.1 --port 8011

pause

