# STORY-REM-062: Loading State Consistency

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Various LOW priority debits
**Type:** UX
**Complexity:** 2 pts (XS - 30 min)
**Priority:** LOW
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Ensure all async operations display consistent loading indicators to improve perceived performance.

## Acceptance Criteria

- [ ] All API calls show loading state
- [ ] Loading indicators consistent (same spinner component)
- [ ] Loading text appropriate for context
- [ ] No blank screens during loading
- [ ] Skeleton loaders used where appropriate
- [ ] Minimum loading time (avoid flashing: 300ms min)

## Technical Notes

```javascript
// Use minimum loading time to prevent flashing
const [isLoading, setIsLoading] = useState(false);

async function fetchData() {
  setIsLoading(true);
  const startTime = Date.now();

  const data = await apiCall();

  const elapsed = Date.now() - startTime;
  if (elapsed < 300) {
    await new Promise(resolve => setTimeout(resolve, 300 - elapsed));
  }

  setIsLoading(false);
  return data;
}
```

## Dependencies

REM-024 (LoadingState component)

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
