# Guia de Testes - Consulta Processual

Este documento contém instruções para testar as melhorias implementadas nas Fases 1 e 2.

## 📋 Pré-requisitos

### Backend
```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx
```

### Frontend
```bash
cd frontend
npm install
```

---

## 🧪 Testes Automatizados

### Backend - Executar Testes

```bash
# Todos os testes
pytest backend/tests/ -v

# Com cobertura
pytest backend/tests/ -v --cov=backend --cov-report=html

# Teste específico
pytest backend/tests/test_validators.py -v
```

### Testes Esperados

✅ **test_validators.py** - 11 testes de validação CNJ
✅ **test_config.py** - 7 testes de configuração
✅ **test_exceptions.py** - 7 testes de exceções customizadas

**Total:** 25 testes automatizados

---

## ✅ Checklist de Validação Manual

### Fase 1 - Configuração e Segurança

#### 1.1 Variáveis de Ambiente

**Backend:**
```bash
cd backend

# Testar com .env
cp .env.example .env
# Editar DATABASE_URL, ALLOWED_ORIGINS, etc.
python -c "from config import settings; print('CORS:', settings.allowed_origins_list)"

# Testar sem .env (deve usar defaults)
mv .env .env.backup
python -c "from config import settings; print('Default DB:', settings.DATABASE_URL)"
mv .env.backup .env
```

**Resultado Esperado:**
- ✅ Com .env: carrega valores personalizados
- ✅ Sem .env: usa valores default
- ✅ Sem erros de import

**Frontend:**
```bash
cd frontend

# Verificar que env vars são usadas
grep -n "import.meta.env" src/services/api.js
```

**Resultado Esperado:**
- ✅ Linha 4-5: `VITE_API_BASE_URL` e `VITE_API_TIMEOUT`

---

#### 1.2 Exception Handling Seguro

**Teste 1: Erro 500 não expõe stack trace**

```bash
# Inicie o backend
cd backend
uvicorn main:app --reload --port 8010
```

**No navegador ou Postman:**
```
GET http://localhost:8010/processes/12345678901234567890
```

**Resultado Esperado:**
- ✅ Status 400 (validation error) OU 404 (not found)
- ✅ Resposta JSON com campo "detail"
- ✅ Mensagem user-friendly (sem stack trace Python)

**Teste 2: Logs contêm detalhes completos**

```bash
# Verificar logs no terminal do backend
# Deve haver logs detalhados server-side mesmo que resposta seja sanitizada
```

**Resultado Esperado:**
- ✅ Logs mostram erro completo
- ✅ API retorna apenas mensagem sanitizada

---

#### 1.3 Validação de Input

**Teste 1: Número CNJ válido**
```bash
# Python console
python
>>> from validators import ProcessNumberValidator
>>> ProcessNumberValidator.validate("0001745-93.1989.8.19.0002")
'00017459319898190002'
```

**Teste 2: Número CNJ inválido**
```bash
>>> ProcessNumberValidator.validate("123456")
# Deve lançar InvalidProcessNumberException
```

**Teste 3: Check digit incorreto**
```bash
>>> ProcessNumberValidator.validate("0001745-99.1989.8.19.0002")
# Deve lançar InvalidProcessNumberException sobre dígito verificador
```

**Teste 4: Bulk request limitado**
```bash
# Via API
POST http://localhost:8010/processes/bulk
Content-Type: application/json

{
  "numbers": ["processo1", "processo2", ..., "processo1001"]  // 1001 items
}
```

**Resultado Esperado:**
- ✅ Status 422 (Validation Error)
- ✅ Mensagem sobre limite de 1000

---

### Fase 2 - Integridade de Dados

#### 2.1 Transaction Management

**Teste: Race Condition Prevention**

Você pode simular requisições concorrentes usando scripts Python:

```python
# test_concurrency.py
import asyncio
import httpx

async def fetch_process(number):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8010/processes/{number}")
        return response.status_code

async def test_concurrent_requests():
    """Envia 10 requisições simultâneas para o mesmo processo"""
    number = "0001745-93.1989.8.19.0002"  # Use um número válido
    tasks = [fetch_process(number) for _ in range(10)]
    results = await asyncio.gather(*tasks)
    print(f"Results: {results}")
    print(f"All 200? {all(r == 200 for r in results)}")

asyncio.run(test_concurrent_requests())
```

**Resultado Esperado:**
- ✅ Todas as requisições retornam 200
- ✅ Sem erros de IntegrityError nos logs
- ✅ Processo não está duplicado no banco de dados

**Verificar unicidade:**
```bash
# SQLite
sqlite3 consulta_processual.db "SELECT COUNT(*) FROM processes WHERE number='00017459319898190002';"
# Deve retornar 1
```

---

#### 2.2 Error Handling DataJud

**Teste 1: Timeout**
```bash
# Modifique temporariamente timeout no .env
DATAJUD_TIMEOUT=1

# Faça uma requisição
GET http://localhost:8010/processes/0001745-93.1989.8.19.0002
```

**Resultado Esperado:**
- ✅ Status 503 (Service Unavailable)
- ✅ Mensagem user-friendly sobre timeout
- ✅ Não expõe detalhes internos

**Teste 2: API Key inválida (se aplicável)**
```bash
# Coloque uma API key inválida no .env
DATAJUD_API_KEY=invalid_key

# Faça uma requisição
```

**Resultado Esperado:**
- ✅ Status 503
- ✅ Mensagem sobre autenticação

---

#### 2.3 Exception Handlers Silenciosos

**Teste: Logs de Warning**
```bash
# Inicie o backend com LOG_LEVEL=DEBUG
LOG_LEVEL=DEBUG uvicorn main:app --reload --port 8010

# Faça requisições e observe os logs
```

**Resultado Esperado:**
- ✅ Warnings aparecem para parsing failures
- ✅ Errors são logados para problemas inesperados
- ✅ Sem bare except silenciosos

---

## 🌐 Teste End-to-End

### 1. Iniciar Backend
```bash
cd backend
uvicorn main:app --reload --port 8010
```

### 2. Iniciar Frontend
```bash
cd frontend
npm run dev
```

### 3. Testar Fluxo Completo

**Navegador:** http://localhost:5173

**Cenário 1: Busca Simples**
1. Digite um número CNJ válido
2. Clique em "Consultar"
3. Verifique que dados são exibidos

**Resultado Esperado:**
- ✅ Loading spinner aparece
- ✅ Dados são carregados
- ✅ Timeline de movimentações aparece

**Cenário 2: Busca Inválida**
1. Digite "123456"
2. Clique em "Consultar"

**Resultado Esperado:**
- ✅ Toast de erro aparece
- ✅ Mensagem user-friendly
- ✅ Sem crash da aplicação

**Cenário 3: Busca em Lote**
1. Vá para aba "Busca em Lote"
2. Digite vários números (um por linha)
3. Clique em "Buscar Lote"

**Resultado Esperado:**
- ✅ Tabela com resultados
- ✅ Processos bem-sucedidos listados
- ✅ Processos falhados listados separadamente
- ✅ Exportação funciona (XLSX, CSV, TXT, MD)

---

## 📊 Relatório de Cobertura

Após executar os testes com cobertura:
```bash
pytest backend/tests/ --cov=backend --cov-report=html
```

Abra o relatório:
```bash
open backend/htmlcov/index.html  # macOS/Linux
start backend/htmlcov/index.html  # Windows
```

**Cobertura Esperada:**
- validators.py: ~95%
- config.py: ~80%
- exceptions.py: 100%
- error_handlers.py: ~85%

---

## 🐛 Troubleshooting

### Backend não inicia
```bash
# Verificar dependências
pip list | grep pydantic
pip list | grep fastapi

# Reinstalar se necessário
pip install pydantic-settings pydantic fastapi
```

### Frontend não conecta ao backend
```bash
# Verificar CORS no terminal do backend
# Deve mostrar: allow_origins=['http://localhost:5173']

# Verificar .env.development existe
ls frontend/.env.development
```

### Testes falhando
```bash
# Limpar cache
pytest --cache-clear

# Executar com output verboso
pytest -vv -s

# Verificar imports
python -c "from validators import ProcessNumberValidator"
```

---

## ✅ Critérios de Sucesso

Para considerar as Fases 1 e 2 validadas:

- [ ] ✅ Todos os 25 testes automatizados passam
- [ ] ✅ Backend inicia sem erros
- [ ] ✅ Frontend inicia sem erros
- [ ] ✅ Busca simples funciona
- [ ] ✅ Busca em lote funciona
- [ ] ✅ Erros são user-friendly (sem stack traces)
- [ ] ✅ CORS configurado corretamente
- [ ] ✅ Validação CNJ funciona
- [ ] ✅ Sem race conditions em requisições concorrentes
- [ ] ✅ Logs contêm informação adequada
- [ ] ✅ Sem API keys expostas em logs

---

## 📝 Próximos Passos

Após validar tudo:
1. ✅ Commit das mudanças
2. ✅ Continuar com Fase 3 (Frontend improvements)
3. ✅ Fase 4 (Code quality)
4. ✅ Deploy para produção
