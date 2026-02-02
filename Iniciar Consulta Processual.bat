@echo off
REM Consulta Processual - Launcher
REM Clique duas vezes neste arquivo para iniciar a aplicacao

title Consulta Processual - Sistema DataJud

REM Muda para o diretorio do script
cd /d "%~dp0"

REM Executa o launcher Python
python launcher.py

pause
