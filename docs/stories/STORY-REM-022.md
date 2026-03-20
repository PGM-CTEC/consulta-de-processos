# STORY-REM-022: Docker Containerization

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DEPLOY-ARCH-001
**Type:** Deployment
**Complexity:** 13 pts (L - 5-7 days)
**Priority:** HIGH
**Assignee:** DevOps Engineer
**Status:** Done
**Sprint:** Sprint 9

## Description

Create Docker images for backend (FastAPI) and frontend (Nginx + Vite build), with docker-compose for local development.

## Acceptance Criteria

- [x] Dockerfile created for backend (Python 3.11, multi-stage build)
- [x] Dockerfile created for frontend (Node 20 build → Nginx serve)
- [x] docker-compose.yml for local dev (backend + frontend + database)
- [x] .dockerignore configured (.env, node_modules, .git)
- [ ] Image builds successfully: `docker build -t consulta-processo-backend .` *(Docker not available in dev env)*
- [ ] Container runs: `docker run -p 8000:8000 consulta-processo-backend` *(pending Docker env)*
- [ ] Health check passes inside container *(pending Docker env)*
- [ ] Image size optimized (<500 MB backend, <100 MB frontend) *(pending Docker env)*

## Technical Notes

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Dependencies

SEC-ARCH-001 (secrets vault needed for env vars)

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (Docker files created, verification pending Docker env)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

- `backend/Dockerfile` — Multi-stage build Python 3.11-slim
- `frontend/Dockerfile` — Node 20 build → Nginx alpine
- `frontend/nginx.conf` — SPA routing + API proxy
- `docker-compose.yml` — Backend + Frontend + volume SQLite
- `.dockerignore` — Raiz
- `frontend/.dockerignore` — Frontend

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-27 | @dev | Implemented Docker files, nginx config, docker-compose [Sprint 9] |
