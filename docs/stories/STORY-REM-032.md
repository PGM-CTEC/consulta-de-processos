# STORY-REM-032: Semantic HTML Improvements

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Multiple accessibility debits
**Type:** Accessibility
**Complexity:** 5 pts (M - 1 day)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Done
**Sprint:** Sprint 10

## Description

Replace generic div/span elements with semantic HTML5 elements (header, nav, main, article, section, footer) for better accessibility and SEO.

## Acceptance Criteria

- [x] Page structure uses semantic HTML5 elements
- [x] Headings hierarchy proper (h1 → h2 → h3, no skips)
- [x] Lists use ul/ol/li appropriately
- [x] Forms use fieldset/legend for grouping
- [x] Buttons use <button>, links use <a>
- [x] HTML validator passes with no structural errors

## Technical Notes

- Audit all components for div-soup
- Use semantic elements:
  - `<header>` for page/section headers
  - `<nav>` for navigation
  - `<main>` for primary content
  - `<article>` for self-contained content
  - `<section>` for thematic grouping
  - `<aside>` for sidebars
  - `<footer>` for footer content

## Dependencies

None

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [x] Merged to `main` branch

## File List

- `frontend/src/components/Dashboard.jsx` — Added `<section>` with `aria-labelledby` and converted h3 to h2
- `frontend/src/components/BulkSearch.jsx` — Added `<form>` and `<section>` with semantic headings (h2)
- `frontend/src/tests/SemanticHTML.test.jsx` — New test file with 12 semantic HTML validation tests
- `docs/stories/STORY-REM-032.md` — Story file (this document)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-27 | @subagent:impl | REM-032 Complete — semantic HTML refactor with 12 tests (244 total tests pass, build OK) |
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
