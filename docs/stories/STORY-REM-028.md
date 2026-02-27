# STORY-REM-028: Dashboard Chart Accessibility

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-004
**Type:** Accessibility
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Done
**Sprint:** Sprint 5+

## Description

Add ARIA labels, keyboard navigation, and screen reader support to all dashboard charts for WCAG 2.1 AA compliance.

## Acceptance Criteria

- [x] All charts have aria-label or aria-labelledby attributes
- [x] Chart data accessible via keyboard navigation
- [x] Screen reader announces chart title and data points
- [x] Alternative text descriptions for complex visualizations
- [x] Axe accessibility audit passes for dashboard
- [x] Keyboard-only navigation test successful

## Technical Notes

- Add ARIA labels to Chart.js or Recharts components
- Provide data table alternatives for complex charts
- Test with NVDA or JAWS screen readers
- Ensure proper focus management

## Dependencies

None

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [x] Merged to `main` branch

## File List

- `frontend/src/components/Dashboard.jsx` — Added figure elements with aria-labels, role="meter" attributes on bars, and sr-only data tables
- `frontend/src/tests/DashboardA11y.test.jsx` — 23 comprehensive accessibility tests for chart a11y
- `frontend/src/tests/Dashboard.test.jsx` — Updated tests to handle sr-only table elements

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-27 | @dev | Implemented: Added figure elements, role="meter", sr-only tables to all 3 charts (tribunals, phases, timeline). Created 23 a11y tests (all passing). Lint and build successful. Sprint 10 Task 4 Complete. |
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
