# Story BR-002: Implement Secure Secret Management

**Story ID:** BR-002
**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** 1 (Critical)
**Priority:** CRITICAL (Security)
**Status:** Ready
**Type:** Feature / Security
**Complexity:** 5 points
**Estimated Effort:** 3-4 hours (1 dia)

---

## Description

### Problem
Atualmente, secrets (API keys, DSNs) são armazenados em `.env` files em plaintext:
- **Accidental Commit Risk:** `.gitignore` pode falhar, expondo secrets
- **History Leak:** Se commitado, fica permanente no git history
- **Zero Encryption:** Sem proteção contra acesso não autorizado
- **Compliance Gap:** Não atende requirements de security audits (LGPD, SOC 2)

### Solution
Implementar secure secret management:
1. **Audit:** Verificar se secrets já foram expostos em git history
2. **Protect:** Robust `.gitignore` configuration
3. **Rotate:** Girar keys se necessário
4. **Automate:** Setup para production (GitHub Actions Secrets)

### Business Value
- **Security:** Elimina risco crítico de credential exposure
- **Compliance:** Atende LGPD, security audit requirements
- **Cost Avoidance:** Previne API key theft, incident response ($500+)
- **Trust:** Protege dados de usuários e integridade do sistema

---

## Acceptance Criteria

### Given
- O projeto usa `.env` files para configuração
- Secrets incluem: DATAJUD_API_KEY, OPENROUTER_API_KEY, SENTRY_DSN
- Team já commitou arquivos em git history

### When
- Developer tenta fazer `git add .env`
- CI/CD job tenta fazer deploy
- Security scanner roda em git history
- Novo developer clona o repo

### Then
- ✅ `.env` seja bloqueado por `.gitignore` (commit prevention)
- ✅ `.env.example` template exists com valores safe (documentação)
- ✅ Git history clean (sem secrets commitados)
- ✅ Secrets em produção protected via GitHub Secrets (se CI/CD setup)
- ✅ Team informed de qualquer exposure detectada
- ✅ Exposed keys rotated (se aplicável)
- ✅ Rotation procedure documentado (para future reference)

---

## Scope

### In Scope ✅

1. **Audit Current State**
   - Scan git history para secrets expostos (git-secrets, TruffleHog)
   - Verify `.gitignore` completeness
   - Identificar todos secret files (.env, .env.local, etc)
   - Document inventory (secrets, where used, rotation frequency)

2. **Secure Configuration Files**
   - Update root `.gitignore` (comprehensive patterns)
   - Update `backend/.gitignore` (if separate)
   - Update `frontend/.gitignore` (if separate)
   - Create `.env.example` (root, backend, frontend)
   - Test `.gitignore` effectiveness (force add should fail)

3. **Secret Rotation (if needed)**
   - Rotate OPENROUTER_API_KEY (if exposed)
   - Verify DATAJUD_API_KEY (check if rotation available)
   - Verify SENTRY_DSN (public by design, no action needed)
   - Document rotation in CHANGELOG

4. **Production Secret Management Setup**
   - Setup GitHub Actions Secrets (for future CI/CD)
   - Document secret injection into runtime
   - Create setup guide para team

5. **Documentation & Training**
   - Create `docs/operations/secret-management.md`
   - Document rotation procedure (quarterly)
   - Onboarding guide para new developers (.env setup)

### Out of Scope ❌

- Advanced secret management tools (dotenv-vault, HashiCorp Vault) - Future story
- Key encryption at rest - Future (for enterprise)
- Audit log system - Future
- Automated secret rotation - Future
- Pre-commit hooks (git-secrets) - Future (nice-to-have)

---

## Dependencies

### Prerequisite Stories
- None (independent)

### Blocking This Story
- None

### This Story Blocks
- CI/CD pipeline setup (needs secrets configured)
- Production deployment (needs secret injection)

### External Dependencies
- ✅ Git installed locally
- ✅ GitHub CLI (gh) para management
- ✅ Secret provider dashboards (OpenRouter, Sentry)

---

## Technical Notes

### `.gitignore` Patterns

**Comprehensive Coverage:**
```gitignore
# Environment Variables (PRIORITY)
.env
.env.local
.env.*.local
!.env.example

# Backend-specific
backend/.env
backend/.env.local

# Frontend-specific
frontend/.env
frontend/.env.local
frontend/.env.development.local
frontend/.env.production.local

# Sensitive Files
*.pem
*.key
*.crt
id_rsa
id_rsa.pub
secrets/
.secrets/

# Database backups (if sensitive)
*.db-wal
*.db-shm

# Logs (may contain sensitive data)
*.log
logs/
backend/*.log
```

### Git History Audit

**Command:**
```bash
# Check for API key patterns
git log --all --full-history -S "API_KEY=" -- .env

# Or use git-secrets
git secrets --scan

# Or use TruffleHog
docker run --rm -it -v "$PWD:/proj" trufflesecurity/trufflehog git file:///proj
```

### Secret Inventory Template

| Secret | Location | Purpose | Sensitivity | Rotation |
|--------|----------|---------|-------------|----------|
| DATAJUD_API_KEY | backend/.env | Public API (CNJ) | LOW | Never |
| OPENROUTER_API_KEY | backend/.env | Private LLM API | HIGH | Quarterly |
| SENTRY_DSN | backend/.env | Error tracking (public) | LOW | Never |
| SENTRY_DSN | frontend/.env | Error tracking (public) | LOW | Never |

### GitHub Secrets Setup

**For CI/CD (Future):**
```yaml
# .github/workflows/deploy.yml
env:
  DATAJUD_API_KEY: ${{ secrets.DATAJUD_API_KEY }}
  OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
  SENTRY_DSN_BACKEND: ${{ secrets.SENTRY_DSN_BACKEND }}
  SENTRY_DSN_FRONTEND: ${{ secrets.SENTRY_DSN_FRONTEND }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker build . --build-arg API_KEY=$DATAJUD_API_KEY
```

---

## Files Affected

### Modified
- `.gitignore` (update/enhance)
- `backend/.env` (no changes, stays git-ignored)
- `frontend/.env` (no changes, stays git-ignored)
- `README.md` (add setup instructions)
- `CHANGELOG.md` (document secret rotation if occurred)

### Created
- `.env.example` (NEW)
- `backend/.env.example` (NEW)
- `frontend/.env.example` (NEW)
- `docs/operations/secret-management.md` (NEW)
- `docs/onboarding/secret-setup.md` (NEW - for new developers)

### Verified (No changes needed)
- `.git/config` (verify no credentials stored)
- `git` history (clean or cleaned)

---

## Definition of Done

### Audit Phase
- [ ] Git history scanned for secrets (git-secrets or TruffleHog)
- [ ] Report: "No secrets found" OR "X secrets found and remediated"
- [ ] `.gitignore` verified as comprehensive
- [ ] Secret inventory documented (all secrets listed)

### Protection Phase
- [ ] `.gitignore` updated (all patterns added)
- [ ] `.env.example` created with safe defaults (root, backend, frontend)
- [ ] Test: `git add -f .env` fails with gitignore warning
- [ ] Test: New developer can copy .env.example → .env without secrets

### Rotation Phase (if needed)
- [ ] Exposed keys rotated (OpenRouter, etc)
- [ ] New keys tested and working
- [ ] Old keys revoked
- [ ] CHANGELOG documented with rotation
- [ ] Team notified of changes

### Production Setup Phase
- [ ] GitHub Secrets created (if using GitHub Actions)
- [ ] Secret names documented
- [ ] Injection mechanism tested (if CI/CD setup exists)

### Documentation & Training Phase
- [ ] Secret management guide written
- [ ] Rotation procedure documented
- [ ] Onboarding guide created (for new developers)
- [ ] Team trained (in standup or doc review)

### Verification & Testing
- [ ] Security audit checklist passed:
  - [ ] `.env` not committable
  - [ ] `.env.example` safe to commit
  - [ ] Git history clean
  - [ ] No test secrets in logs
- [ ] New developer simulation test passed
- [ ] TruffleHog scan clean (no secrets detected)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Secrets already in git history** | MEDIUM | CRITICAL | Phase 1 audit + BFG cleanup + rotation |
| **`.gitignore` bypass (developer error)** | MEDIUM | HIGH | Training + pre-commit hooks (future) |
| **Missing `.env.example` patterns** | LOW | MEDIUM | Comprehensive checklist, peer review |
| **Rotation breaks production** | LOW | HIGH | Test in staging first, document rollback |
| **Team resistance to process** | MEDIUM | MEDIUM | Emphasize security, share audit report |

---

## Acceptance Testing Scenarios

### Scenario 1: `.gitignore` Enforcement
```bash
# Attempt to add .env (should fail or warn)
git add backend/.env
# Expected: warning ".env is ignored by .gitignore"

# Attempt force add (should still be blocked by .gitignore logic)
git add -f backend/.env
# Expected: still not staged (modern git behavior)
```

### Scenario 2: New Developer Onboarding
```bash
# 1. Clone repo
git clone <repo>
cd consulta-processo

# 2. Setup .env
cp backend/.env.example backend/.env

# 3. Verify .env not tracked
git status
# Expected: backend/.env NOT listed

# 4. Commit should work
git add .
git commit -m "test"
# Expected: no .env in commit
```

### Scenario 3: Secret Audit
```bash
# Run security scan
git secrets --scan
# OR
docker run --rm -it -v "$PWD:/proj" \
  trufflesecurity/trufflehog git file:///proj

# Expected: "No secrets detected" or list of issues with fixes
```

### Scenario 4: Documentation Completeness
```bash
# Check guides exist
cat docs/operations/secret-management.md
cat docs/onboarding/secret-setup.md

# Expected: Clear instructions for both scenarios
```

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Git Hygiene** | 0 secrets in history | `git secrets --scan` = clean |
| **Configuration Safety** | 100% of .env blocked | `git add .env` = blocked |
| **Team Awareness** | 100% trained | Survey or checklist |
| **Documentation** | Complete | All guides exist and readable |
| **Rotation Compliance** | Quarterly rotation | Calendar reminder + CHANGELOG |

---

## Change Log

- **2026-02-21:** Story created by @architect (Aria) from PLAN-002
- Status: Ready for @dev implementation

---

## Related Documents

- **Implementation Plan:** `docs/brownfield/plans/PLAN-002-secret-management.md`
- **System Architecture:** `docs/brownfield/system-architecture.md` (Section: Configuration Management & Security)

---

**Story Owner:** @dev
**Story Reviewer:** @qa
**Architect:** @architect (Aria)
**Created:** 2026-02-21
**Target Sprint:** 1 (Critical)
