# Consulta Processual — PGM Rio

[![CI/CD Pipeline](https://github.com/raocg/consulta-de-processos/actions/workflows/ci.yml/badge.svg)](https://github.com/raocg/consulta-de-processos/actions/workflows/ci.yml)

Sistema de consulta e acompanhamento de processos judiciais para a Procuradoria Geral do Município do Rio de Janeiro (PGM-Rio).

Aplicação brownfield remediada com design system, validação de formulários, otimizações de performance e monitoramento de erros via Sentry.

## 🎯 Features

- **Busca de processos** por número CNJ (NNNNNNN-DD.AAAA.J.TT.OOOO)
- **Busca em lote** com suporte a upload de arquivos (TXT, CSV, XLSX)
- **Design System** consolidado (Button, Card, Badge, Input components)
- **Form Validation** com react-hook-form + Zod
- **Lazy Loading & Code Splitting** (bundle -70%)
- **Virtualization** para resultados em massa (100+ itens)
- **Pagination** com usePagination hook
- **Monitoring** via Sentry (erros e performance)
- **Circuit Breaker** pattern para DataJudClient (API externa)
- **Dark Mode** ready UI
- **Acessibilidade** (ARIA labels, roles, keyboard navigation)

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite (→ PostgreSQL) + Alembic
- **Frontend:** React 18 + Vite + TailwindCSS + Storybook 8
- **Form:** react-hook-form 7.71 + Zod 4
- **Tests:** pytest (backend, 437 testes) + Vitest (frontend, 437 testes)
- **Deploy:** Docker + GitHub Actions
- **Monitoring:** Sentry

## Prerequisites

- Python 3.9+
- Node.js 18+
- Docker (optional)

## Installation

### Backend

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
```

## Environment Variables

Crie `.env` na raiz do projeto:

```env
# Backend
SENTRY_DSN=https://...@sentry.io/...
DATAJUD_API_URL=https://www1.cnj.jus.br/datajud/api/graphql
CIRCUIT_BREAKER_TIMEOUT=60

# Frontend (se necessário)
VITE_API_URL=http://localhost:8000
VITE_SENTRY_DSN=https://...@sentry.io/...
```

## Quick Start

### Local Development

```bash
# Terminal 1: Backend
cd backend
uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

Acesso:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker

```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## Tests

```bash
# Backend (pytest)
cd backend
python -m pytest -q

# Frontend (Vitest)
cd frontend
npm test -- --run

# Lint + Type Check (Frontend)
cd frontend
npm run lint
npm run typecheck
```

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app
│   ├── services/            # Business logic
│   ├── models/              # SQLAlchemy models
│   ├── patterns/            # CircuitBreaker, etc
│   └── tests/               # pytest tests (437)
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks (usePagination)
│   │   ├── lib/             # validationSchemas (Zod)
│   │   ├── services/        # API calls
│   │   └── tests/           # Vitest tests (437)
│   ├── .storybook/          # Storybook config
│   └── vitest.config.js
└── docs/
    ├── stories/             # Development stories
    ├── architecture/        # System design
    └── guides/              # User & deployment guides
```

## API Documentation

**Base URL:** `http://localhost:8000`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/search` | Buscar processo por número |
| POST | `/api/search/bulk` | Busca em lote (múltiplos números) |
| GET | `/circuit-breaker/status` | Status do Circuit Breaker |
| GET | `/docs` | OpenAPI documentation |

### Example: Search by Process Number

```bash
curl "http://localhost:8000/api/search?number=0001745-64.1989.8.19.0002"
```

### Example: Bulk Search

```bash
curl -X POST "http://localhost:8000/api/search/bulk" \
  -H "Content-Type: application/json" \
  -d '{"numbers": ["0001745-64.1989.8.19.0002", "0002345-12.2020.8.19.0001"]}'
```

## Form Validation (REM-040)

Todos os formulários usam **react-hook-form + Zod** para validação declarativa:

### SearchProcess Component
```javascript
const searchProcessSchema = z.object({
  number: cnjNumberSchema  // NNNNNNN-DD.AAAA.J.TT.OOOO
});
```

### BulkSearch Component
```javascript
const bulkSearchSchema = z.object({
  numbers: z.string().min(1, "...)  // Um por linha
});
```

### Settings Component (SQL Config)
```javascript
const sqlConfigSchema = z.object({
  driver: z.enum(['postgresql', 'mysql', 'mssql+pyodbc', 'sqlite']),
  host: z.string().min(1),
  port: z.coerce.number().min(1).max(65535),
  user: z.string().optional(),
  password: z.string().optional(),
  database: z.string().min(1),
  query: z.string().min(1)
});
```

## Performance Optimizations

### Frontend (Sprint 11 - REM-037, REM-038)
- **Lazy Loading:** React.lazy() + Suspense (bundle -70%)
- **Code Splitting:** Route-based + component-based
- **Virtualization:** @tanstack/react-virtual para 100+ resultados
- **Pagination:** usePagination hook (10 itens/página)
- **Memoization:** React.memo() para ResultRow

### Bundle Size
- Antes: 800 KB
- Depois: 236 KB (-70%)

## Monitoring & Error Handling

### Sentry Integration
- Erro reporting automático
- Performance monitoring
- User session tracking

### Circuit Breaker (DataJudClient)
- Threshold: 5 falhas
- Recovery timeout: 60s
- Status endpoint: `GET /circuit-breaker/status`

## Deployment

### Manual Deployment

```bash
# Build
npm run build

# Push to production
git push origin main
```

### Docker Production Build

```bash
docker build -f docker/Dockerfile -t consulta-processual:latest .
docker push your-registry/consulta-processual:latest
```

### Environment Setup for Production

```env
SENTRY_DSN=https://your-sentry-key@sentry.io/project-id
DATAJUD_API_URL=https://www1.cnj.jus.br/datajud/api/graphql
CIRCUIT_BREAKER_TIMEOUT=60
DATABASE_URL=postgresql://user:pass@prod-db:5432/consulta  # Após migração
```

## Troubleshooting

### "Número do processo é obrigatório"
- Valide o formato: `NNNNNNN-DD.AAAA.J.TT.OOOO`
- Exemplo válido: `0001745-64.1989.8.19.0002`

### Circuit Breaker está OPEN
- Aguarde 60s (recovery timeout) ou reinicie o backend
- Verifique: `GET /circuit-breaker/status`

### Testes falhando
```bash
# Clear cache
rm -rf node_modules/.vite
npm run test -- --run

# Backend testes
cd backend && python -m pytest -x -q
```

### Build falha com peer deps
```bash
npm install --legacy-peer-deps
```

## Contributing

1. Crie uma branch: `git checkout -b feature/REM-XXX`
2. Implemente a story
3. Execute testes: `npm test -- --run`
4. Commit: `git commit -m "feat: descrição [REM-XXX]"`
5. Push: `git push origin feature/REM-XXX`
6. Crie um Pull Request

## License

MIT
