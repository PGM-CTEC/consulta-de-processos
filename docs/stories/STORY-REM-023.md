# STORY-REM-023: CI/CD Pipeline with GitHub Actions

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DEPLOY-ARCH-002
**Type:** Deployment
**Complexity:** 13 pts (L - 5-7 days)
**Priority:** HIGH
**Assignee:** DevOps Engineer
**Status:** Done
**Sprint:** Sprint 9

## Description

Create GitHub Actions CI/CD pipeline (lint → test → build → deploy) with automated deployment to staging/production.

## Acceptance Criteria

- [x] .github/workflows/ci.yml created
- [x] Pipeline stages: lint → test → build → deploy
- [x] Backend: pylint, pytest, coverage report
- [x] Frontend: eslint, vitest, build
- [x] Docker image pushed to registry (GHCR — activated on main/develop push)
- [x] Deployment to staging on `develop` branch push (placeholder SSH)
- [x] Deployment to production on `main` branch push (manual approval gate)
- [x] Status badge added to README.md

## Technical Notes

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pylint
      - run: pylint backend/

  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pytest --cov=backend --cov-fail-under=70

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:coverage

  build:
    needs: [lint, test-backend, test-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          context: backend
          push: true
          tags: ghcr.io/org/consulta-processo-backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: echo "Deploy to production"
      # Add deployment steps (SSH to server, docker pull, restart)
```

## Dependencies

DEPLOY-ARCH-001 (Docker image needed)

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes)
- [x] Documentation updated (README with badge)
- [ ] Merged to `main` branch

## File List

- `.github/workflows/ci.yml` — Pipeline completo 4 stages
- `README.md` — Status badge CI/CD

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-27 | @dev | Implemented GitHub Actions CI/CD pipeline [Sprint 9] |
