@echo off
setlocal
REM Script para executar testes do backend

echo ========================================
echo Consulta Processual - Test Suite
echo ========================================
echo.

echo [1/3] Verificando dependencias...
pushd backend
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias
    popd
    exit /b 1
)
echo Dependencias OK
echo.

echo [2/3] Executando testes...
set "PYTHONPATH=%CD%"
pytest tests/ -v --tb=short -p no:asyncio
set TEST_RESULT=%ERRORLEVEL%
echo.

if "%TEST_RESULT%"=="0" (
    echo ========================================
    echo TODOS OS TESTES PASSARAM!
    echo ========================================
    echo.
    echo Proximos passos:
    echo 1. Iniciar backend: uvicorn main:app --reload --port 8010
    echo 2. Iniciar frontend: cd frontend ^&^& npm run dev
    echo 3. Testar aplicacao em http://localhost:5173
    echo.
) else (
    echo ========================================
    echo ALGUNS TESTES FALHARAM
    echo ========================================
    echo.
    echo Execute novamente com mais detalhes:
    echo pytest tests/ -vv -s
    echo.
)

popd
exit /b %TEST_RESULT%
