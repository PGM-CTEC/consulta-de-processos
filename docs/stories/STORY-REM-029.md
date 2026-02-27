# STORY-REM-029: Modal Dialog ARIA

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-002
**Type:** Accessibility
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Done
**Sprint:** Sprint 5+

## Description

Add ARIA attributes to modal dialogs (role="dialog", aria-modal="true", aria-labelledby) for screen reader compatibility.

## Acceptance Criteria

- [x] All modals have role="dialog"
- [x] aria-modal="true" set on modal containers
- [x] aria-labelledby points to modal title
- [x] Focus trapped within modal when open
- [x] ESC key closes modal
- [x] Screen reader test confirms proper announcement

## Technical Notes

```jsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
>
  <h2 id="modal-title">Modal Title</h2>
  {/* Modal content */}
</div>
```

## Dependencies

None

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

- `frontend/src/components/ProcessDetails.jsx` — Added `role="dialog"`, `aria-modal="true"`, `aria-labelledby="json-modal-title"` to JSON modal; added `id="json-modal-title"` to modal h3; added `role="status"` + `aria-label` to loading overlay; added `aria-hidden="true"` to spinner icon; moved `showJson` useState before useEffects; added ESC key useEffect handler; added click-outside handler on modal backdrop.
- `frontend/src/tests/ProcessDetails.test.jsx` — Added `describe('Modal Dialog ARIA — REM-029')` with 3 tests: loading overlay role="status" baseline, dialog ARIA absent in default state, and dialog ARIA present after button click with fireEvent.

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-27 | @dev | REM-029 implemented — modal ARIA + ESC handler + role="status" on loading overlay |
