# AGENTS.md — Consulta Processual (PGM-Rio)

Monorepo: Python backend (`backend/`) + React 19 frontend (`frontend/`).

## Commands

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn backend.main:app --reload           # Dev :8000

# Frontend (--legacy-peer-deps required)
cd frontend && npm install --legacy-peer-deps
npm run dev                                  # Dev :5173
npm run build
npm run lint                                 # ESLint
npm run storybook                            # Storybook :6006

# Tests
cd backend && python -m pytest -q            # Backend (pytest, 44 test files)
cd frontend && npm test -- --run             # Frontend (Vitest, jsdom)
npm run e2e                                  # Root Playwright (3 browsers + mobile)
cd frontend && npm run test:coverage         # Coverage (v8)
```

`.env` required at root (`cp .env.example .env`).

## Architecture

- **Data sources** (priority): DataJud API → Fusion REST API → Fusion SQL Server
- **Backend auto-migrates** DB schema on startup (`main.py::lifespan`): adds columns for hierarchical classification to existing tables
- **Phase classification**: hierarchical 3-field model (stage 1-5, substage "1.1"-"2.3", transit_julgado). Legacy flat phase "01"-"15" maintained for compatibility
- **Phase correction system**: manual corrections stored in `phase_corrections` + `phase_confirmations` tables → ML training data for classifier
- **Fusion/PAV integration**: `FusionService` (SQL first → API fallback), cookie-session auth via PAV, bookmarklet updates cookie at `PATCH /fusion/cookie`
- **Patterns**: CircuitBreaker on `DataJudClient`, SoftDeleteMixin on models, AuditLog via SQLAlchemy event listeners
- **Middleware order** (`main.py`): CorrelationId runs outermost (added last), RequestLogger runs inside it — this is intentional so correlation ID is available to the logger

## Project structure

```
backend/         # FastAPI app (main.py entrypoint)
  services/      # process_service, fusion_service, datajud, phase_analyzer, etc
  patterns/      # CircuitBreaker
  middleware/    # CorrelationIdMiddleware, RequestLoggerMiddleware
  tests/         # 44 pytest files
frontend/        # Vite + React 19 + TailwindCSS
  src/
    services/    # api.js (axios), phaseCorrections.js
    stores/      # zustand: searchStore, settingsStore
    components/  # ui/, SearchProcess, BulkSearch, ProcessDetails, etc
    tests/       # 26 Vitest test files
    constants/   # phases.js
fase-processual-doctree/   # Classification rules & decision tree
scripts/         # backup_db.sh, restore_database.sh
```

## Quirks

- **`npm install` requires `--legacy-peer-deps`** (react 19 + old deps)
- **Vite dev server proxies** `/processes`, `/health`, `/stats`, `/history`, `/settings`, `/fusion`, `/sql`, `/openapi.json`, `/phase-corrections`, `/phase-confirmations` → `http://127.0.0.1:8000`
- **Sentry is optional**: guarded by try/except import in `main.py`; Sentry DSN in `.env`
- **Rate limiting** via slowapi (disabled by default, `RATE_LIMIT_ENABLED=false`)
- Frontend API uses `VITE_API_BASE_URL || '/'` (proxied in dev, configurable in prod)
- Root `package.json` only has Playwright e2e scripts; frontend has its own `package.json`
- No CI workflows committed (`.github/workflows/` is empty)
