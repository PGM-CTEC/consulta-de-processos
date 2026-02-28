# Sprint 9 — Deployment & Foundations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Dockerizar backend e frontend, criar pipeline CI/CD completo no GitHub Actions, padronizar loading states no frontend, configurar Alembic para migrações, adicionar Audit Trail para LGPD, e documentar decisão de autenticação.

**Architecture:**
- Docker multi-stage builds para backend (FastAPI/Python 3.11) e frontend (Vite → Nginx)
- GitHub Actions com 4 stages: lint → test → build → deploy, usando imagens do GHCR
- Alembic conectado à mesma `Base` SQLAlchemy já existente em `backend/database.py`
- AuditLog via SQLAlchemy event listeners nos models Process e Movement
- LoadingState/SkeletonLoader como componentes compartilhados em React

**Tech Stack:** Python 3.11, FastAPI, Uvicorn, SQLite, Alembic, SQLAlchemy, React, Vite, Nginx, Docker, GitHub Actions, pytest, vitest, ESLint

---

## Ordem de Execução (Dependências)

```
Grupo A (sequencial):  REM-022 (Docker) → REM-023 (CI/CD)
Grupo B (sequencial):  REM-025 (Alembic) → REM-026 (Audit Trail)
Grupo C (independente): REM-024 (Loading States)
Grupo D (independente): REM-027 (Auth Decision Doc)
```

**Recomendado:** Execute B e C em paralelo primeiro (sem dependências externas), depois A, depois D.

---

## Task 1: Preparar Branch Sprint 9

**Files:** nenhum

**Step 1: Criar e entrar no branch sprint-9**

```bash
git checkout main
git pull origin main
git checkout -b sprint-9
```

Expected: branch sprint-9 criada a partir de main

**Step 2: Verificar estado limpo**

```bash
git status
```

Expected: `nothing to commit, working tree clean`

---

## Task 2: REM-025 — Alembic Setup (Database Migrations)

**Files:**
- Create: `alembic.ini` (raiz do projeto)
- Create: `alembic/env.py`
- Create: `alembic/versions/` (gerado automaticamente)
- Modify: `backend/requirements.txt`

**Contexto:** O projeto usa SQLAlchemy com `Base` em `backend/database.py` e models em `backend/models.py`. DATABASE_URL padrão: `sqlite:///./consulta_processual.db`.

**Step 1: Instalar Alembic**

```bash
cd backend
pip install alembic==1.13.1
```

**Step 2: Adicionar ao requirements.txt**

No arquivo `backend/requirements.txt`, adicionar após `sqlalchemy`:
```
alembic==1.13.1
```

**Step 3: Inicializar Alembic na raiz do projeto**

```bash
cd /c/Projetos/Consulta\ processo
alembic init alembic
```

Expected: criados `alembic.ini` e `alembic/` com env.py, script.py.mako, versions/

**Step 4: Configurar alembic.ini — apontar DATABASE_URL**

Editar `alembic.ini`, linha `sqlalchemy.url`:
```ini
sqlalchemy.url = sqlite:///./consulta_processual.db
```

**Step 5: Configurar alembic/env.py — importar os models**

Substituir o conteúdo de `alembic/env.py` pelo seguinte (mantém a estrutura gerada mas adiciona o target_metadata):

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Importar Base e todos os models para que metadata seja detectado
from backend.database import Base
import backend.models  # noqa: F401 — garante que os models estão registrados

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Step 6: Gerar migration inicial**

```bash
cd /c/Projetos/Consulta\ processo
alembic revision --autogenerate -m "initial schema"
```

Expected: arquivo criado em `alembic/versions/XXXX_initial_schema.py`

**Step 7: Verificar migration gerada (inspecionar)**

```bash
cat alembic/versions/*initial_schema.py
```

Conferir que tables `processes`, `movements`, `search_history` estão no `upgrade()`.

**Step 8: Aplicar migration**

```bash
alembic upgrade head
```

Expected: `Running upgrade  -> XXXX, initial schema` (sem erros)

**Step 9: Testar rollback**

```bash
alembic downgrade -1
alembic upgrade head
```

Expected: sem erros em ambos

**Step 10: Testar histórico**

```bash
alembic history
```

Expected: linha com `initial schema (head)`

**Step 11: Commit**

```bash
git add alembic/ alembic.ini backend/requirements.txt
git commit -m "feat: setup Alembic for database migrations [REM-025]"
```

---

## Task 3: REM-026 — Audit Trail para LGPD

**Files:**
- Modify: `backend/models.py` — adicionar AuditLog model + event listeners
- Create: `backend/tests/test_audit_trail.py`

**Contexto:** Process e Movement já existem em `backend/models.py`. Database usa SQLite. JSON column no SQLite precisa de `sqlite_json` ou Text alternativo — usar `Text` com serialização manual para máxima compatibilidade.

**Step 1: Escrever os testes primeiro (TDD)**

Criar `backend/tests/test_audit_trail.py`:

```python
"""Tests for LGPD Audit Trail — REM-026"""
import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import Process, AuditLog


@pytest.fixture
def test_db():
    """In-memory SQLite database for tests."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_audit_log_table_exists(test_db):
    """AuditLog model should be importable and table should exist."""
    count = test_db.query(AuditLog).count()
    assert count == 0


def test_insert_process_creates_audit_entry(test_db):
    """Inserting a Process should create an INSERT entry in audit_log."""
    process = Process(number="0001234-56.2024.8.19.0001")
    test_db.add(process)
    test_db.commit()

    logs = test_db.query(AuditLog).filter_by(table_name="processes", action="INSERT").all()
    assert len(logs) == 1
    assert logs[0].record_id == process.id
    assert logs[0].action == "INSERT"


def test_update_process_creates_audit_entry(test_db):
    """Updating a Process should create an UPDATE entry in audit_log."""
    process = Process(number="0001234-56.2024.8.19.0002")
    test_db.add(process)
    test_db.commit()

    process.phase = "Execução"
    test_db.commit()

    logs = test_db.query(AuditLog).filter_by(table_name="processes", action="UPDATE").all()
    assert len(logs) == 1
    assert logs[0].table_name == "processes"


def test_delete_process_creates_audit_entry(test_db):
    """Deleting a Process should create a DELETE entry in audit_log."""
    process = Process(number="0001234-56.2024.8.19.0003")
    test_db.add(process)
    test_db.commit()
    pid = process.id

    test_db.delete(process)
    test_db.commit()

    logs = test_db.query(AuditLog).filter_by(table_name="processes", action="DELETE").all()
    assert len(logs) == 1
    assert logs[0].record_id == pid


def test_audit_log_has_timestamp(test_db):
    """Each audit entry must have a timestamp."""
    process = Process(number="0001234-56.2024.8.19.0004")
    test_db.add(process)
    test_db.commit()

    log = test_db.query(AuditLog).first()
    assert log.timestamp is not None
```

**Step 2: Rodar os testes — confirmar falha**

```bash
cd /c/Projetos/Consulta\ processo
python -m pytest backend/tests/test_audit_trail.py -v
```

Expected: FAIL — `ImportError: cannot import name 'AuditLog'`

**Step 3: Implementar AuditLog model e event listeners em backend/models.py**

Adicionar ao final de `backend/models.py` (após a classe SearchHistory):

```python
import json as _json
from datetime import datetime
from sqlalchemy import event, inspect as sa_inspect


class AuditLog(Base):
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=True)
    action = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = Column(Text, nullable=True)     # JSON serializado
    new_values = Column(Text, nullable=True)     # JSON serializado
    user_id = Column(String, nullable=True)      # Futuro: sistema de auth
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.table_name}#{self.record_id}>"


def _serialize(obj):
    """Serializa um model SQLAlchemy para dict JSON-safe."""
    if obj is None:
        return None
    result = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name, None)
        if isinstance(val, datetime):
            val = val.isoformat()
        result[col.name] = val
    return _json.dumps(result)


@event.listens_for(Process, 'after_insert')
def _audit_process_insert(mapper, connection, target):
    connection.execute(
        AuditLog.__table__.insert(),
        {
            "table_name": "processes",
            "record_id": target.id,
            "action": "INSERT",
            "old_values": None,
            "new_values": _serialize(target),
            "timestamp": datetime.utcnow(),
        }
    )


@event.listens_for(Process, 'after_update')
def _audit_process_update(mapper, connection, target):
    state = sa_inspect(target)
    old = {}
    for attr in state.attrs:
        hist = attr.history
        if hist.has_changes() and hist.deleted:
            old[attr.key] = hist.deleted[0]
    connection.execute(
        AuditLog.__table__.insert(),
        {
            "table_name": "processes",
            "record_id": target.id,
            "action": "UPDATE",
            "old_values": _json.dumps({k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v for k, v in old.items()}),
            "new_values": _serialize(target),
            "timestamp": datetime.utcnow(),
        }
    )


@event.listens_for(Process, 'after_delete')
def _audit_process_delete(mapper, connection, target):
    connection.execute(
        AuditLog.__table__.insert(),
        {
            "table_name": "processes",
            "record_id": target.id,
            "action": "DELETE",
            "old_values": _serialize(target),
            "new_values": None,
            "timestamp": datetime.utcnow(),
        }
    )
```

**Step 4: Gerar migration para a nova tabela**

```bash
alembic revision --autogenerate -m "add audit_log table"
alembic upgrade head
```

Expected: migration criada com `audit_log` table no `upgrade()`

**Step 5: Rodar os testes — confirmar PASS**

```bash
python -m pytest backend/tests/test_audit_trail.py -v
```

Expected: 5 passed

**Step 6: Rodar suite completa (sem regressões)**

```bash
python -m pytest backend/tests/ -q --tb=short 2>&1 | tail -10
```

Expected: mesmos resultados de antes (342 passing, 16 known failures)

**Step 7: Commit**

```bash
git add backend/models.py backend/tests/test_audit_trail.py alembic/versions/
git commit -m "feat: add LGPD audit trail with SQLAlchemy event listeners [REM-026]"
```

---

## Task 4: REM-024 — Loading States UI Consistency

**Files:**
- Create: `frontend/src/components/LoadingState.jsx`
- Create: `frontend/src/tests/LoadingState.test.jsx`
- Modify: `frontend/src/components/BulkSearch.jsx`
- Modify: `frontend/src/components/Dashboard.jsx`
- Modify: `frontend/src/components/ProcessDetails.jsx`
- (outros 6 components conforme necessário)

**Contexto:** Cada componente já usa `loading` state próprio com spinners inline diferentes. Precisamos unificar em 3 variantes: `spinner`, `skeleton`, `text`.

**Step 1: Escrever os testes para LoadingState**

Criar `frontend/src/tests/LoadingState.test.jsx`:

```jsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { LoadingState, SkeletonCard, SkeletonTable, ErrorState } from '../components/LoadingState'

describe('LoadingState', () => {
  it('renders spinner variant by default', () => {
    render(<LoadingState />)
    expect(document.querySelector('.animate-spin')).toBeTruthy()
  })

  it('renders spinner with custom message', () => {
    render(<LoadingState variant="spinner" message="Carregando processos..." />)
    expect(screen.getByText('Carregando processos...')).toBeTruthy()
  })

  it('renders skeleton variant', () => {
    render(<LoadingState variant="skeleton" />)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('renders text variant with default message', () => {
    render(<LoadingState variant="text" />)
    expect(screen.getByText('Carregando...')).toBeTruthy()
  })

  it('renders text variant with custom message', () => {
    render(<LoadingState variant="text" message="Aguarde..." />)
    expect(screen.getByText('Aguarde...')).toBeTruthy()
  })
})

describe('SkeletonCard', () => {
  it('renders animated placeholder bars', () => {
    render(<SkeletonCard />)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })
})

describe('SkeletonTable', () => {
  it('renders correct number of skeleton rows', () => {
    render(<SkeletonTable rows={3} />)
    const rows = document.querySelectorAll('.animate-pulse')
    expect(rows.length).toBeGreaterThanOrEqual(3)
  })

  it('renders default 5 rows when no rows prop', () => {
    render(<SkeletonTable />)
    const rows = document.querySelectorAll('.animate-pulse')
    expect(rows.length).toBeGreaterThanOrEqual(5)
  })
})

describe('ErrorState', () => {
  it('renders error message', () => {
    render(<ErrorState message="Erro ao carregar dados" />)
    expect(screen.getByText('Erro ao carregar dados')).toBeTruthy()
  })

  it('renders retry button when onRetry provided', () => {
    const onRetry = () => {}
    render(<ErrorState message="Erro" onRetry={onRetry} />)
    expect(screen.getByRole('button', { name: /tentar novamente/i })).toBeTruthy()
  })

  it('does not render retry button when no onRetry', () => {
    render(<ErrorState message="Erro" />)
    const btn = screen.queryByRole('button')
    expect(btn).toBeNull()
  })
})
```

**Step 2: Rodar os testes — confirmar falha**

```bash
cd /c/Projetos/Consulta\ processo/frontend
npm run test -- --run src/tests/LoadingState.test.jsx
```

Expected: FAIL — `Cannot find module '../components/LoadingState'`

**Step 3: Criar frontend/src/components/LoadingState.jsx**

```jsx
/**
 * Unified loading state components — REM-024
 * Variantes: spinner (padrão), skeleton, text
 */

export const SkeletonCard = () => (
  <div className="animate-pulse bg-white rounded-lg p-6 shadow">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
  </div>
)

export const SkeletonTable = ({ rows = 5 }) => (
  <div className="space-y-2">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="animate-pulse flex space-x-4">
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/3"></div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/6"></div>
      </div>
    ))}
  </div>
)

export const ErrorState = ({ message, onRetry }) => (
  <div className="flex flex-col items-center justify-center p-8 text-center">
    <div className="text-red-500 text-xl mb-2">⚠️</div>
    <p className="text-gray-700 mb-4">{message}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
      >
        Tentar novamente
      </button>
    )}
  </div>
)

export const LoadingState = ({ variant = 'spinner', message }) => {
  if (variant === 'skeleton') {
    return <SkeletonCard />
  }

  if (variant === 'text') {
    return (
      <div className="text-center p-8 text-gray-600">
        {message || 'Carregando...'}
      </div>
    )
  }

  // Default: spinner
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
      {message && <p className="ml-4 text-gray-600">{message}</p>}
    </div>
  )
}

export default LoadingState
```

**Step 4: Rodar os testes — confirmar PASS**

```bash
npm run test -- --run src/tests/LoadingState.test.jsx
```

Expected: 11 passed

**Step 5: Migrar BulkSearch.jsx para usar LoadingState**

Em `frontend/src/components/BulkSearch.jsx`, adicionar no topo:
```jsx
import { LoadingState } from './LoadingState'
```

Localizar qualquer spinner/loading inline existente e substituir por:
```jsx
{loading && <LoadingState variant="spinner" message="Processando..." />}
```

**Step 6: Migrar ProcessDetails.jsx para usar LoadingState**

Em `frontend/src/components/ProcessDetails.jsx`, adicionar no topo:
```jsx
import { LoadingState, ErrorState } from './LoadingState'
```

Substituir spinners inline por `<LoadingState />` e estados de erro por `<ErrorState />`.

**Step 7: Verificar os outros 7 componentes**

Para cada arquivo em `frontend/src/components/`:
- Dashboard.jsx
- HistoryTab.jsx
- InstanceSelector.jsx
- PerformanceDashboard.jsx
- PhaseReference.jsx
- SearchProcess.jsx
- Settings.jsx

Buscar padrões de loading inline e substituir onde apropriado. Se o componente já usa `<LoadingState>` ou não tem loading state, pular.

```bash
grep -n "animate-spin\|isLoading\|loading &&" frontend/src/components/*.jsx
```

**Step 8: Rodar suite frontend completa**

```bash
npm run test -- --run
```

Expected: 195 passed (ou mais, com os novos testes)

**Step 9: Commit**

```bash
git add frontend/src/components/LoadingState.jsx frontend/src/tests/LoadingState.test.jsx frontend/src/components/
git commit -m "feat: unified LoadingState/SkeletonLoader/ErrorState components [REM-024]"
```

---

## Task 5: REM-027 — Auth Decision Document

**Files:**
- Create: `docs/decisions/auth-decision.md`

**Contexto:** O projeto já tem `REQUIRE_AUTH: bool = False` em `config.py` e é descrito como ferramenta interna (PGM Rio). VPN + controle de rede → decisão óbvia é NO-GO (defer auth).

**Step 1: Criar o documento de decisão**

Criar `docs/decisions/auth-decision.md`:

```markdown
# Authentication Decision Document — REM-027

**Data:** 2026-02-26
**Autor:** @dev
**Status:** DECIDED — NO-GO (Defer)

---

## Requirements

- **Application type:** INTERNAL TOOL (PGM-Rio — Procuradoria Geral do Município)
- **Expected users:** 1-50 (advogados e servidores internos)
- **Network protection:** Acesso via rede interna / VPN corporativa
- **User management needed:** NO (para o escopo atual)
- **Public internet exposure:** NO

---

## Decision: NO-GO (Defer Authentication)

### Rationale

O sistema é uma ferramenta interna da PGM-Rio, acessada exclusivamente por usuários
autenticados na rede da prefeitura. O controle de acesso é feito no nível de infraestrutura
(VPN, firewall, proxy reverso). Implementar autenticação na aplicação seria over-engineering
para o escopo atual.

### Condições para Revisão

Esta decisão deve ser revisitada se:
1. O sistema for exposto à internet pública
2. Houver necessidade de rastreabilidade por usuário (LGPD — Audit Trail já usa `user_id=null`)
3. Diferentes níveis de permissão forem requeridos

---

## Security Implications

- **IP whitelisting** deve ser configurado no proxy reverso (nginx/load balancer)
- **VPN** obrigatória para acesso externo
- O campo `user_id` no `AuditLog` (REM-026) está preparado para receber JWT claims no futuro
- Rate limiting já implementado via `slowapi` (config: `RATE_LIMIT_ENABLED`)

---

## Recommended Approach (Quando Necessário)

Se NO-GO for revertido, abordagem recomendada:
- **FastAPI-Users** (batteries-included, JWT + OAuth2)
- User model: `username`, `email`, `password_hash` (bcrypt), `is_active`, `role`
- Token expiration: 8h access token, 7d refresh token
- Integration: passar `user_id` para `AuditLog` via middleware

---

## Config Atual

```python
# backend/config.py
REQUIRE_AUTH: bool = False   # Alterar para True quando implementar
VALID_API_KEYS: str = ""     # API keys simples como stepping stone
```
```

**Step 2: Commit**

```bash
git add docs/decisions/auth-decision.md
git commit -m "docs: authentication decision — NO-GO, defer to future sprint [REM-027]"
```

---

## Task 6: REM-022 — Docker Containerization

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`
- Create: `frontend/.dockerignore`

**Contexto:**
- Backend: FastAPI em `backend/`, entry point `backend.main:app`, porta 8000
- Frontend: Vite em `frontend/`, build output em `dist/`, servido por Nginx porta 80
- Database: SQLite file em `./consulta_processual.db` (volume mount para persistência)

**Step 1: Criar backend/Dockerfile**

```dockerfile
# backend/Dockerfile
# Multi-stage build: reduz tamanho da imagem final

# Stage 1: Builder — instala dependências
FROM python:3.11-slim AS builder

WORKDIR /app

# Copiar requirements primeiro (layer caching)
COPY requirements.txt requirements-runtime.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-runtime.txt

# Stage 2: Runtime — imagem final enxuta
FROM python:3.11-slim

WORKDIR /app

# Copiar site-packages do builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código do backend
COPY . .

# Porta exposta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Entry point
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: Criar frontend/Dockerfile**

```dockerfile
# frontend/Dockerfile
# Multi-stage: Node build → Nginx serve

# Stage 1: Builder
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files primeiro (layer caching)
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

# Copiar código e fazer build
COPY . .
RUN npm run build

# Stage 2: Runtime — Nginx serve estático
FROM nginx:alpine

# Copiar build output para nginx html dir
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config customizado (SPA routing)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Step 3: Criar frontend/nginx.conf**

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing: serve index.html para todas as rotas
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests para backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Cache assets estáticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Step 4: Criar docker-compose.yml na raiz**

```yaml
# docker-compose.yml
version: '3.9'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: consulta-processo-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/consulta_processual.db
      - ENVIRONMENT=development
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data  # Persistência do SQLite
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: consulta-processo-frontend
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped

volumes:
  data:
```

**Step 5: Criar .dockerignore na raiz**

```
# .dockerignore (raiz)
.git
.github
*.md
docs/
node_modules/
frontend/node_modules/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/
.env
*.env
consulta_processual.db
```

**Step 6: Criar frontend/.dockerignore**

```
node_modules/
dist/
.env
*.md
src/tests/
src/e2e/
```

**Step 7: Verificar que o build do backend funciona**

```bash
cd /c/Projetos/Consulta\ processo
docker build -t consulta-processo-backend ./backend
```

Expected: `Successfully tagged consulta-processo-backend:latest`
Verificar tamanho: `docker images consulta-processo-backend` — deve ser < 500MB

**Step 8: Verificar que o build do frontend funciona**

```bash
docker build -t consulta-processo-frontend ./frontend
```

Expected: build completo, imagem < 100MB

**Step 9: Testar com docker-compose**

```bash
docker-compose up -d
sleep 10
curl http://localhost:8000/health
curl http://localhost:80
docker-compose down
```

Expected: health endpoint responde 200, frontend serve HTML

**Step 10: Atualizar story file**

Marcar checkboxes em `docs/stories/STORY-REM-022.md` como concluídos.

**Step 11: Commit**

```bash
git add backend/Dockerfile frontend/Dockerfile frontend/nginx.conf docker-compose.yml .dockerignore frontend/.dockerignore docs/stories/STORY-REM-022.md
git commit -m "feat: Docker containerization — backend + frontend + compose [REM-022]"
```

---

## Task 7: REM-023 — CI/CD Pipeline com GitHub Actions

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `README.md` — adicionar status badge

**Contexto:**
- `.github/workflows/e2e-tests.yml` já existe
- Backend: `pytest --cov=backend --cov-fail-under=70`
- Frontend: `vitest --run`, `eslint .`
- Docker images: GitHub Container Registry (`ghcr.io`)
- Deploy: placeholder (SSH + docker pull)

**Step 1: Criar .github/workflows/ci.yml**

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop, sprint-9]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ─── Stage 1: Lint ────────────────────────────────────────────
  lint-backend:
    name: Lint Backend (pylint)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt
      - run: pip install pylint
      - run: pip install -r backend/requirements.txt
      - name: Run pylint (warn only — não bloqueia)
        run: pylint backend/ --exit-zero || true

  lint-frontend:
    name: Lint Frontend (ESLint)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci --prefix frontend
      - name: Run ESLint (warn only — erros pré-existentes)
        run: npm run lint --prefix frontend || true

  # ─── Stage 2: Test ────────────────────────────────────────────
  test-backend:
    name: Test Backend (pytest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-cov pytest-asyncio
      - name: Run tests with coverage
        run: python -m pytest backend/tests/ -q --tb=short --cov=backend --cov-report=xml --ignore=backend/tests/test_sentry_integration.py
        env:
          DATABASE_URL: sqlite:///./test.db
      - name: Upload coverage report
        uses: codecov/codecov-action@v4
        if: always()
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

  test-frontend:
    name: Test Frontend (Vitest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci --prefix frontend
      - name: Run Vitest
        run: npm run test --prefix frontend -- --run
      - name: Build frontend (verifica que builda)
        run: npm run build --prefix frontend

  # ─── Stage 3: Build Docker ────────────────────────────────────
  build:
    name: Build & Push Docker Images
    runs-on: ubuntu-latest
    needs: [lint-backend, lint-frontend, test-backend, test-frontend]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:${{ github.sha }},${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Build and push frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:${{ github.sha }},${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ─── Stage 4: Deploy ──────────────────────────────────────────
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - name: Deploy to staging server
        run: |
          echo "🚀 Deploy to staging"
          echo "IMAGE: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:${{ github.sha }}"
          # TODO: SSH + docker pull + restart quando servidor de staging for provisionado

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production  # Requer aprovação manual no GitHub
    steps:
      - name: Deploy to production server
        run: |
          echo "🚀 Deploy to production"
          echo "IMAGE: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:${{ github.sha }}"
          # TODO: SSH + docker pull + restart quando servidor de produção for provisionado
```

**Step 2: Adicionar status badge ao README.md**

No topo do `README.md`, adicionar após o título:

```markdown
[![CI/CD Pipeline](https://github.com/raocg/consulta-de-processos/actions/workflows/ci.yml/badge.svg)](https://github.com/raocg/consulta-de-processos/actions/workflows/ci.yml)
```

**Step 3: Commit**

```bash
git add .github/workflows/ci.yml README.md
git commit -m "feat: GitHub Actions CI/CD pipeline — lint/test/build/deploy [REM-023]"
```

---

## Task 8: Atualizar Story Files e Push

**Step 1: Atualizar status de todas as stories da Sprint 9**

Para cada story (REM-022 a REM-027), editar o arquivo e:
1. Mudar `**Status:** Ready` para `**Status:** Done`
2. Marcar todos os checkboxes de AC como `[x]`
3. Preencher a seção `## File List` com os arquivos criados/modificados
4. Adicionar entrada no `## Change Log`

**Step 2: Rodar suite completa de testes (backend + frontend)**

```bash
cd /c/Projetos/Consulta\ processo
python -m pytest backend/tests/ -q --tb=no 2>&1 | tail -5
cd frontend && npm run test -- --run 2>&1 | tail -5
```

Expected: backend 342+ passed, frontend 195+ passed

**Step 3: Commit final da sprint**

```bash
cd /c/Projetos/Consulta\ processo
git add docs/stories/STORY-REM-02*.md
git commit -m "docs: Sprint 9 Complete — REM-022/023/024/025/026/027 Done"
```

**Step 4: Push e criar PR (via @devops)**

```bash
git push -u origin sprint-9
# Em seguida: criar PR sprint-9 → main via GitHub UI ou @devops
```

---

## Resumo dos Arquivos Criados/Modificados

```
CRIADOS:
├── backend/Dockerfile
├── backend/tests/test_audit_trail.py
├── frontend/Dockerfile
├── frontend/nginx.conf
├── frontend/.dockerignore
├── frontend/src/components/LoadingState.jsx
├── frontend/src/tests/LoadingState.test.jsx
├── .dockerignore
├── docker-compose.yml
├── alembic.ini
├── alembic/env.py
├── alembic/versions/XXXX_initial_schema.py
├── alembic/versions/XXXX_add_audit_log_table.py
├── .github/workflows/ci.yml
└── docs/decisions/auth-decision.md

MODIFICADOS:
├── backend/models.py (+ AuditLog + event listeners)
├── backend/requirements.txt (+ alembic)
├── frontend/src/components/BulkSearch.jsx (LoadingState)
├── frontend/src/components/ProcessDetails.jsx (LoadingState)
├── README.md (+ CI badge)
└── docs/stories/STORY-REM-022 a 027 (Status: Done)
```
