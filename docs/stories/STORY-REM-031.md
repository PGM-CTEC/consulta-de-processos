# STORY-REM-031: Color Contrast Audit

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-005
**Type:** Accessibility
**Complexity:** 3 pts (S - 2 hours)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Done
**Sprint:** Sprint 5+

## Description

Audit and fix color contrast issues to meet WCAG 2.1 AA requirements (4.5:1 for normal text, 3:1 for large text).

## Acceptance Criteria

- [x] All text has minimum 4.5:1 contrast ratio
- [x] Large text (18pt+) has minimum 3:1 contrast ratio
- [x] Interactive elements have 3:1 contrast ratio
- [x] Contrast checker tool used for verification
- [x] No contrast issues in Axe DevTools audit
- [x] Color palette documentation updated

## Technical Notes

- Use WebAIM Contrast Checker or Axe DevTools
- Update CSS color variables if needed
- Consider dark mode contrast as well
- Document approved color combinations

## Dependencies

None

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

| File | Changes |
|------|---------|
| `frontend/src/components/Dashboard.jsx` | Line 148: text-gray-400 → text-gray-600; Line 176: text-gray-400 → text-gray-600; Line 199: text-gray-500 → text-gray-600 |
| `frontend/src/components/BulkSearch.jsx` | Line 132: text-gray-400 → text-gray-600; Line 138: text-gray-400 → text-gray-600; Lines 216-220: text-gray-400 → text-gray-600 (table headers); Line 129: Added aria-label to file input for a11y compliance |
| `frontend/src/tests/a11y-contrast.test.jsx` | NEW: Contrast ratio documentation test (14 test cases) |
| `frontend/src/tests/a11y-axe-audit.test.jsx` | NEW: Axe DevTools audit suite (8 test cases) — confirms zero contrast/a11y violations |

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-27 | @dev (AC5 Fix) | AC5 gap correction: Added Axe DevTools audit test suite (8 tests) confirming zero contrast + a11y violations; Fixed BulkSearch file input aria-label [REM-031 AC5] |
| 2026-02-27 | @dev | REM-031 implemented — color contrast audit, gray-400/500→gray-600 fixes + contrast test suite [REM-031] |
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
