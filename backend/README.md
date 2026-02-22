# Consulta Processual - Backend API

FastAPI backend para consulta de processos judiciais via API DataJud.

## 🚀 Quick Start

### 1. Setup Ambiente

```bash
# Criar virtual environment
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp ../.env.example ../.env

# Editar .env e adicionar sua DATAJUD_API_KEY
# OBRIGATÓRIO: DATAJUD_API_KEY=your_key_here
```

**Como obter DataJud API Key:**
1. Acesse: https://datajud.cnj.jus.br
2. Faça login/registro
3. Gere API Key na seção "Configurações > API Keys"
4. Cole a chave Base64 no arquivo `.env`

### 3. Rodar Servidor

```bash
# Desenvolvimento (auto-reload)
python -m uvicorn main:app --reload --port 8000

# Ou usar script de conveniência
python main.py
```

Servidor disponível em: http://localhost:8000

**API Docs:** http://localhost:8000/docs (Swagger UI)

---

## 📋 Variáveis de Ambiente

### Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATAJUD_API_KEY` | Chave de API do DataJud (Base64) | `cDZHYzlZ...` |

### Opcionais (com defaults seguros)

| Variável | Default | Descrição |
|----------|---------|-----------|
| `DATABASE_URL` | `sqlite:///./consulta_processual.db` | URL do banco de dados |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins (comma-separated) |
| `ENVIRONMENT` | `development` | `development\|staging\|production` |
| `DEBUG` | `true` | Debug mode |
| `LOG_LEVEL` | `INFO` | `DEBUG\|INFO\|WARNING\|ERROR` |
| `RATE_LIMIT_ENABLED` | `false` | Habilitar rate limiting |
| `RATE_LIMIT_PER_MINUTE` | `60` | Requests/minuto por IP |
| `SENTRY_DSN` | `""` | Sentry error tracking (vazio = desabilitado) |

Ver `.env.example` para lista completa e documentação detalhada.

---

## 🗄️ Banco de Dados

### SQLite (Desenvolvimento - Default)

```python
# config.py
DATABASE_URL = "sqlite:///./consulta_processual.db"
```

**Migrations:**
- Migrations SQL em `backend/migrations/`
- Ver `backend/migrations/README.md` para instruções

### PostgreSQL (Produção - Recomendado)

```bash
# .env
DATABASE_URL=postgresql://user:password@host:5432/database_name
```

**Vantagens:**
- Suporte a múltiplos usuários simultâneos
- Performance superior para grandes volumes
- Constraints e índices mais robustos

---

## 📚 API Endpoints

### Health Check
```http
GET /health
```

Retorna status do backend + conexão com DataJud.

### Buscar Processo (Single)
```http
POST /api/search
Content-Type: application/json

{
  "cnj_number": "12345678901234567890"
}
```

### Buscar Processos (Bulk)
```http
POST /api/bulk
Content-Type: application/json

{
  "cnj_numbers": [
    "12345678901234567890",
    "09876543210987654321"
  ]
}
```

### Histórico de Buscas
```http
GET /api/history?limit=50
```

**Documentação Interativa:** http://localhost:8000/docs

---

## 🧪 Testes

```bash
# Rodar todos os testes
pytest

# Com coverage
pytest --cov=. --cov-report=html

# Ver relatório
open htmlcov/index.html
```

---

## 🔧 Desenvolvimento

### Estrutura de Arquivos

```
backend/
├── main.py              # Entry point + FastAPI app
├── config.py            # Configuração centralizada (Pydantic)
├── database.py          # SQLAlchemy setup + session management
├── models.py            # SQLAlchemy models (Process, Movement)
├── routers/             # API endpoints
│   ├── search.py
│   └── history.py
├── services/            # Business logic
│   ├── datajud.py      # DataJud API client
│   └── classifier.py   # Phase classification
├── migrations/          # SQL migrations
└── tests/              # Unit tests
```

### Adicionar Dependency

```bash
pip install package-name
pip freeze > requirements.txt
```

### Linting & Formatting

```bash
# Linting
pylint *.py

# Formatting
black .

# Type checking
mypy .
```

---

## 🚨 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'main'"

**Solução:** Rode com `python -m uvicorn` ao invés de importar diretamente:
```bash
python -m uvicorn main:app --reload
```

### Erro: "DATAJUD_API_KEY not configured"

**Solução:** Verifique que `.env` existe e contém `DATAJUD_API_KEY=...`

### Erro: "database is locked"

**Solução (SQLite):**
- Certifique-se que apenas 1 instância do backend está rodando
- Considere migrar para PostgreSQL para produção

### Porta 8000 já em uso

**Solução:** Use porta diferente:
```bash
python -m uvicorn main:app --reload --port 8001
```

---

## 📦 Deploy

### Railway / Render / Fly.io

1. Criar `Procfile`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. Configurar variáveis de ambiente na plataforma:
   - `DATAJUD_API_KEY` (obrigatório)
   - `DATABASE_URL` (PostgreSQL recomendado)
   - `ENVIRONMENT=production`
   - `DEBUG=false`

3. Deploy:
   ```bash
   git push railway main  # Railway
   # ou
   flyctl deploy         # Fly.io
   ```

---

## 📝 License

MIT

## 👥 Contribuindo

Pull requests são bem-vindos! Para mudanças grandes, abra uma issue primeiro.

---

**Dúvidas?** Abra uma issue ou veja a documentação principal no README.md da raiz do projeto.
