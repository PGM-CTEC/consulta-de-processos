# STORY-REM-028: Dashboard Chart Accessibility

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-004
**Type:** Accessibility
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Add ARIA labels, keyboard navigation, and screen reader support to all dashboard charts for WCAG 2.1 AA compliance.

## Acceptance Criteria

- [ ] All charts have aria-label or aria-labelledby attributes
- [ ] Chart data accessible via keyboard navigation
- [ ] Screen reader announces chart title and data points
- [ ] Alternative text descriptions for complex visualizations
- [ ] Axe accessibility audit passes for dashboard
- [ ] Keyboard-only navigation test successful

## Technical Notes

- Add ARIA labels to Chart.js or Recharts components
- Provide data table alternatives for complex charts
- Test with NVDA or JAWS screen readers
- Ensure proper focus management

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
