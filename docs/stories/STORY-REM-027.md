# STORY-REM-027: Evaluate Authentication Layer

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** SEC-ARCH-003
**Type:** Security
**Complexity:** 5 pts (M - 2-3 days)
**Priority:** MEDIUM
**Assignee:** Backend Developer
**Status:** Done
**Sprint:** Sprint 9

## Description

Evaluate need for authentication (JWT, OAuth, etc.) and document decision (yes/no, which approach).

## Acceptance Criteria

- [x] Requirements gathered (internal tool, 1-50 users, VPN-protected)
- [x] Decision documented: NO-GO (defer authentication)
- [ ] If YES: Auth library selected (N/A — NO-GO)
- [ ] If YES: User model designed (N/A — NO-GO)
- [x] If NO: Rationale documented (internal tool behind VPN, AuditLog user_id prepared for future)
- [x] Security implications documented (IP whitelist, VPN, rate limiting)

## Technical Notes

```markdown
# Authentication Decision Document

## Requirements
- Application is: [PUBLIC / INTERNAL / HYBRID]
- Expected users: [1-10 / 10-100 / 100+]
- User management needed: [YES / NO]
- Network protection: [VPN / IP whitelist / Public internet]

## Decision: [GO / NO-GO]

**Rationale:**
- If internal tool behind VPN → NO-GO (defer auth)
- If public-facing → GO (implement JWT or OAuth)

## Recommended Approach (if GO):
- FastAPI-Users (batteries-included, JWT + OAuth)
- Supabase Auth (managed service, RLS integration)
- Custom JWT (lightweight, full control)

## Security Implications:
- If NO auth: IP whitelisting + VPN required
- If YES auth: Password hashing (bcrypt), token expiration, refresh tokens
```

## Dependencies

None

## Definition of Done

- [ ] Code complete and peer-reviewed
- [ ] Unit tests written (if applicable)
- [ ] Acceptance criteria met (all checkboxes ✅)
- [ ] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

- `docs/decisions/auth-decision.md` — Decision document (NO-GO, defer)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-27 | @dev | Documented authentication decision — NO-GO (internal tool/VPN) [Sprint 9] |
