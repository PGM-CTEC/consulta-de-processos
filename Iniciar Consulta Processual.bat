@echo off
REM Consulta Processual - Launcher
REM Clique duas vezes neste arquivo para iniciar a aplicacao

title Consulta Processual - Sistema DataJud

REM Muda para o diretorio do script
cd /d "%~dp0"

REM Executa o launcher Python
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 launcher.py
) else (
    python launcher.py
)

pause
