# STORY-REM-046: Denormalized Court Cleanup

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-009
**Type:** Database
**Complexity:** 3 pts (S - 1 day)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Evaluate if court data (tribunal, comarca) should be normalized to separate table or remain denormalized. Document decision.

## Acceptance Criteria

- [ ] Analysis completed (query patterns, update frequency)
- [ ] Decision documented: NORMALIZE or KEEP DENORMALIZED
- [ ] If NORMALIZE: Migration plan created, foreign keys designed
- [ ] If KEEP: Rationale documented (performance trade-offs)
- [ ] Performance impact assessed

## Technical Notes

**Considerations:**
- How often is court data updated? (rarely → denormalized OK)
- How many unique courts? (low → denormalized OK)
- Query patterns: Filter by court? (yes → index sufficient)
- Storage impact: (minimal → denormalized OK)

**Decision template:**
```markdown
## Normalization Decision: [NORMALIZE / DENORMALIZED]

**Rationale:**
- Update frequency: [Once/year | Monthly | Daily]
- Unique courts: [~100 | ~1000 | 10,000+]
- Storage overhead: [<1% | 5-10% | >10%]
- Query performance: [Index sufficient | Join needed]

**Recommendation:** [NORMALIZE / KEEP DENORMALIZED]
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

_To be updated during development_

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
