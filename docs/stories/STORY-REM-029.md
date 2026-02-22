# STORY-REM-029: Modal Dialog ARIA

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-002
**Type:** Accessibility
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Add ARIA attributes to modal dialogs (role="dialog", aria-modal="true", aria-labelledby) for screen reader compatibility.

## Acceptance Criteria

- [ ] All modals have role="dialog"
- [ ] aria-modal="true" set on modal containers
- [ ] aria-labelledby points to modal title
- [ ] Focus trapped within modal when open
- [ ] ESC key closes modal
- [ ] Screen reader test confirms proper announcement

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
