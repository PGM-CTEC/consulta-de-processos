# Sprint 6: Critical Stabilization + Quick Wins

**Sprint Number:** Sprint 6 (Sprint 1 of Brownfield Remediation)
**Duration:** 6-8 days (1 week)
**Status:** Planning
**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Date Range:** 2026-02-24 to 2026-03-02

---

## Sprint Overview

**Objetivo Principal:** Implementar 10 "Quick Wins" que removem 40% dos HIGH débitos em apenas 6 horas de esforço total, estabilizando o sistema para os sprints de performance/testing que virão.

**Business Value:**
- 🔒 **Segurança:** Secrets vault + rate limiting + CORS whitelist (elimina 3 HIGH vulns)
- ⚡ **Performance:** Database indexes (20-100x query speedup)
- 📊 **Confiabilidade:** Backup automation + log rotation (data loss prevention)
- ♿ **Compliance:** Label associations (WCAG 2.1 accessibility)
- 🧹 **Code Quality:** Remove dead code (OpenRouter)

**Effort Distribution:**
- Backend Developer: 3 days
- DevOps Engineer: 1 day
- Frontend Developer: 1 day
- Data Engineer: 1 day

---

## Stories Sprint 6 (11 Total)

### 🟢 Quick Wins (10 stories) — TARGET: 6 hours total

| ID | Story | Effort | Developer | Status |
|----|-------|--------|-----------|--------|
| REM-001 | Add Missing Database Indexes | 30 min | Data Eng | [ ] TODO |
| REM-002 | Implement Automated Database Backup | 2h | DevOps | [ ] TODO |
| REM-003 | Implement Secrets Vault | 1d | Backend | [ ] TODO |
| REM-004 | Add API Rate Limiting | 2h | Backend | [ ] TODO |
| REM-005 | Add CORS Whitelist Configuration | 30 min | Backend | [ ] TODO |
| REM-006 | Remove OpenRouter Dead Code | 30 min | Backend | [ ] TODO |
| REM-007 | Add Label HTML Associations (A11y) | 30 min | Frontend | [ ] TODO |
| REM-008 | Add Phase CHECK Constraint | 15 min | Data Eng | [ ] TODO |
| REM-009 | Add CNJ Number CHECK Constraint | 15 min | Data Eng | [ ] TODO |
| REM-010 | Configure Database Connection Pooling | 30 min | Backend | [ ] TODO |
| REM-011 | Add Log Rotation | 30 min | Backend | [ ] TODO |

---

## Acceptance Criteria (Sprint Level)

- [ ] All 10 Quick Wins completed and merged to `sprint-6-remediation` branch
- [ ] Code review passed (CodeRabbit + manual review)
- [ ] All tests passing (pytest + npm test)
- [ ] Database indexes verified (performance test <5ms latency)
- [ ] Secrets vault operational (no plaintext secrets in repo)
- [ ] Rate limiter tested (101st request → 429)
- [ ] Backup script tested (manual restore successful)
- [ ] PR created and ready for merge to main

---

## Story Assignments

### Backend Developer (Dex)
- [ ] REM-003: Secrets Vault (1 day)
- [ ] REM-004: Rate Limiting (2 hours)
- [ ] REM-005: CORS Whitelist (30 min)
- [ ] REM-006: Remove Dead Code (30 min)
- [ ] REM-010: Connection Pooling (30 min)
- [ ] REM-011: Log Rotation (30 min)

**Total: 3 days**

### Data Engineer (Dara)
- [ ] REM-001: Database Indexes (30 min)
- [ ] REM-008: Phase CHECK Constraint (15 min)
- [ ] REM-009: CNJ CHECK Constraint (15 min)

**Total: 1 day**

### DevOps Engineer (Gage)
- [ ] REM-002: Backup Automation (2 hours)

**Total: 1 day**

### Frontend Developer (Alex)
- [ ] REM-007: Label HTML Associations (30 min)

**Total: 1 day**

---

## Implementation Order (Dependency-Based)

**Phase 1: Security Foundation (Day 1)**
1. REM-003: Secrets Vault (unblocks deployment later)
2. REM-002: Backup Automation (data protection)
3. REM-004: Rate Limiting (DoS prevention)

**Phase 2: Data Quality (Day 2)**
4. REM-001: Database Indexes (quick performance win)
5. REM-008: Phase CHECK Constraint
6. REM-009: CNJ CHECK Constraint

**Phase 3: Code & Config (Day 3)**
7. REM-010: Connection Pooling (database tuning)
8. REM-011: Log Rotation (ops)
9. REM-005: CORS Whitelist (security)
10. REM-006: Remove Dead Code (cleanup)
11. REM-007: Label HTML Associations (accessibility)

---

## Daily Standup Template

### Day 1 (Security Foundation)
**Goal:** REM-003, REM-002, REM-004 complete

```
@Backend (Dex):
- [ ] REM-003: Secrets vault selection (dotenv-vault vs AWS)
- [ ] REM-003: Implementation (.env migration)
- [ ] REM-004: Rate limiter integrated

@DevOps (Gage):
- [ ] REM-002: Backup script created
- [ ] REM-002: Cron job configured
- [ ] REM-002: Manual restore tested

Blockers: None expected
```

### Day 2 (Data Quality)
**Goal:** REM-001, REM-008, REM-009 complete

```
@Data Engineer (Dara):
- [ ] REM-001: CREATE INDEX statements executed
- [ ] REM-001: Performance test: Movement query <5ms
- [ ] REM-008/009: CHECK constraints created

Blockers: None expected
```

### Day 3 (Code & Config)
**Goal:** REM-010, REM-011, REM-005, REM-006, REM-007 complete

```
@Backend (Dex):
- [ ] REM-010: Connection pooling configured
- [ ] REM-011: Log rotation handler added
- [ ] REM-005: CORS origins whitelisted
- [ ] REM-006: OpenRouter code deleted

@Frontend (Alex):
- [ ] REM-007: htmlFor attributes added
- [ ] REM-007: Axe audit clean

Blockers: None expected
```

---

## Success Metrics

### Performance
- **Before:** Movement queries 100-500ms
- **After:** <5ms (with indexes)
- **Target:** ✅ 20-100x speedup

### Security
- **Before:** Secrets in plaintext (.env)
- **After:** Encrypted vault
- **Target:** ✅ Zero plaintext secrets

### Reliability
- **Before:** No backups, unbounded log growth
- **After:** Daily backups + log rotation
- **Target:** ✅ Data loss prevention

### Compliance
- **Before:** 15 form fields without htmlFor
- **After:** All labeled
- **Target:** ✅ WCAG 1.3.1 compliance

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Secrets migration breaks production | LOW | HIGH | Test vault locally first, rollback plan |
| DB schema changes cause issues | LOW | MEDIUM | Backup before constraint changes, test on copy |
| Rate limiter too strict | MEDIUM | MEDIUM | Start at 100/min, adjust based on metrics |
| Backup script fails silently | MEDIUM | HIGH | Test cron manually, add email alerts |

---

## Definition of Done

For each story:
- [ ] Code written and tested locally
- [ ] All acceptance criteria met
- [ ] Unit tests added (if applicable)
- [ ] CodeRabbit review passed
- [ ] Manual code review approved
- [ ] Merged to sprint-6-remediation branch
- [ ] Verified in dev environment
- [ ] Story file updated with completion notes

---

## Files to Review

**Stories referenced:**
- [EPIC-BROWNFIELD-REMEDIATION.md](docs/stories/epics/EPIC-BROWNFIELD-REMEDIATION.md) (REM-001 to REM-011 detailed)

**Codebase affected:**
- `backend/main.py` (rate limiter, CORS, log rotation)
- `backend/config.py` (secrets vault)
- `backend/database.py` (connection pooling)
- `backend/models.py` (CHECK constraints)
- `frontend/src/components/BulkSearch.jsx` (labels)
- `frontend/src/components/Settings.jsx` (labels)
- `scripts/backup_db.sh` (new file)

---

## Communication

**Daily Sync:** Slack #sprint-6-updates
**Issues:** GitHub Issues tagged `sprint-6-remediation`
**Code Review:** PR review comments
**Blockers:** Escalate to @pm (Morgan)

---

## Next Steps After Sprint 6

**Sprint 7 Planning (3 days after Sprint 6 start):**
- Review Sprint 6 results
- Plan Sprint 2 (Performance & Observability)
- Stories: REM-012 to REM-016
  - Async bulk processing
  - Sentry integration
  - Health checks
  - Retry logic
  - CloudWatch logging

---

**Sprint 6 Kickoff:** 2026-02-24
**Sprint 6 Completion Target:** 2026-03-02
**Status:** Ready for Development

