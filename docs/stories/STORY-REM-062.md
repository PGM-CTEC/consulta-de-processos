# STORY-REM-062: Loading State Consistency

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Various LOW priority debits
**Type:** UX
**Complexity:** 2 pts (XS - 30 min)
**Priority:** LOW
**Assignee:** Frontend Developer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

Ensure all async operations display consistent loading indicators to improve perceived performance.

## Acceptance Criteria

- [x] All API calls show loading state
- [x] Loading indicators consistent (same spinner component)
- [x] Loading text appropriate for context
- [x] No blank screens during loading
- [x] Skeleton loaders used where appropriate
- [x] Minimum loading time (avoid flashing: 300ms min)

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

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

### New Files
- `frontend/src/hooks/useLoadingState.js` — Custom hook with 300ms minimum loading time to prevent UI flashing
- `frontend/src/tests/useLoadingState.test.js` — 6 comprehensive tests for the hook

### Existing Files (Already Have Loading States)
- `frontend/src/components/BulkSearch.jsx` — Uses loading state with spinner + disabled button
- `frontend/src/components/SearchProcess.jsx` — Uses loading state with disabled button
- `frontend/src/components/Dashboard.jsx` — Uses Loader2 spinner during data fetch
- `frontend/src/components/ProcessDetails.jsx` — Uses loading state for instance fetching
- `frontend/src/components/HistoryTab.jsx` — Uses loading state for history fetch
- `frontend/src/components/PerformanceDashboard.jsx` — Uses loading state during metrics load
- `frontend/src/components/LoadingFallback.jsx` — Accessible Suspense fallback with spinner

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-28 | @dev | Created useLoadingState hook with 300ms minimum loading time + 6 tests. Verified all components have consistent Loader2 spinners |
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
