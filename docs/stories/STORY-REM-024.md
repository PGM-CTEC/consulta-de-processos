# STORY-REM-024: Loading States UI Consistency

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-ARCH-003
**Type:** Frontend
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 4

## Description

Create unified LoadingState, SkeletonLoader, and ErrorState components for consistent UX across all components.

## Acceptance Criteria

- [ ] LoadingState component (spinner, skeleton, text variants)
- [ ] SkeletonCard, SkeletonTable components created
- [ ] ErrorState component (with retry button)
- [ ] All 9 components migrated to use unified loading states
- [ ] Storybook stories created (optional documentation)
- [ ] Loading → Success transition smooth (no content jump)

## Technical Notes

```jsx
// src/components/LoadingState.jsx
export const LoadingState = ({ variant = 'spinner', message }) => {
  if (variant === 'spinner') {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
        {message && <p className="ml-4 text-gray-600">{message}</p>}
      </div>
    );
  }

  if (variant === 'skeleton') {
    return <SkeletonCard />;
  }

  return <div className="text-center p-8 text-gray-600">{message || 'Carregando...'}</div>;
};

export const SkeletonCard = () => (
  <div className="animate-pulse bg-white rounded-lg p-6 shadow">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
  </div>
);
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
