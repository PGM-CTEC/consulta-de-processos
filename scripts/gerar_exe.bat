@echo off
REM Script para gerar executavel do Consulta Processual

echo ========================================
echo   Consulta Processual - Gerar EXE
echo ========================================
echo.

echo [1/3] Verificando PyInstaller...
pyinstaller --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Falha ao instalar PyInstaller
        pause
        exit /b 1
    )
)
echo   OK - PyInstaller encontrado
echo.

echo [2/3] Gerando executavel...
echo   Isso pode levar alguns minutos...
echo.

pyinstaller "%~dp0launcher.spec" --clean --noconfirm

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: Falha ao gerar executavel
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando resultado...

if exist "dist\Consulta Processual.exe" (
    del /f /q "dist\Consulta Processual.exe"
)

if exist "dist\Consulta Processual\Consulta Processual.exe" (
    echo.
    echo ========================================
    echo   SUCESSO!
    echo ========================================
    echo.
    echo Executavel gerado em:
    echo   dist\Consulta Processual\Consulta Processual.exe
    echo.
    echo Tamanho do arquivo:
    for %%A in ("dist\Consulta Processual\Consulta Processual.exe") do echo   %%~zA bytes
    echo.
    echo Para usar:
    echo   1. Copie TODO o projeto para o destino
    echo   2. Execute "dist\Consulta Processual\Consulta Processual.exe"
    echo.
) else (
    echo.
    echo ERRO: Executavel nao foi criado
    echo Verifique os erros acima
    echo.
)

pause
