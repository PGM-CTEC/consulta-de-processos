# Consulta Processual — PGM Rio

[![CI/CD Pipeline](https://github.com/raocg/consulta-de-processos/actions/workflows/ci.yml/badge.svg)](https://github.com/raocg/consulta-de-processos/actions/workflows/ci.yml)

Sistema de consulta e acompanhamento de processos judiciais para a Procuradoria Geral do Município do Rio de Janeiro (PGM-Rio).

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite + Alembic
- **Frontend:** React + Vite + TailwindCSS
- **Tests:** pytest (backend) + Vitest (frontend)
- **Deploy:** Docker + GitHub Actions

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Docker

```bash
docker-compose up -d
```

## Tests

```bash
# Backend
python -m pytest backend/tests/ -q

# Frontend
cd frontend && npm run test -- --run
```
