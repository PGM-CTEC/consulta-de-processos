# STORY-REM-023: CI/CD Pipeline with GitHub Actions

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DEPLOY-ARCH-002
**Type:** Deployment
**Complexity:** 13 pts (L - 5-7 days)
**Priority:** HIGH
**Assignee:** DevOps Engineer
**Status:** Ready
**Sprint:** Sprint 4

## Description

Create GitHub Actions CI/CD pipeline (lint → test → build → deploy) with automated deployment to staging/production.

## Acceptance Criteria

- [ ] .github/workflows/ci.yml created
- [ ] Pipeline stages: lint → test → build → deploy
- [ ] Backend: pylint, pytest, coverage report
- [ ] Frontend: eslint, vitest, build
- [ ] Docker image pushed to registry (Docker Hub or GitHub Container Registry)
- [ ] Deployment to staging on `develop` branch push
- [ ] Deployment to production on `main` branch push (manual approval)
- [ ] Status badge added to README.md

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

- [ ] Code complete and peer-reviewed
- [ ] Unit tests written (if applicable)
- [ ] Acceptance criteria met (all checkboxes ✅)
- [ ] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

_To be updated during development_

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
