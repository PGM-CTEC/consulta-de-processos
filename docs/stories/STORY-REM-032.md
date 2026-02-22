# STORY-REM-032: Semantic HTML Improvements

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Multiple accessibility debits
**Type:** Accessibility
**Complexity:** 5 pts (M - 1 day)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Replace generic div/span elements with semantic HTML5 elements (header, nav, main, article, section, footer) for better accessibility and SEO.

## Acceptance Criteria

- [ ] Page structure uses semantic HTML5 elements
- [ ] Headings hierarchy proper (h1 → h2 → h3, no skips)
- [ ] Lists use ul/ol/li appropriately
- [ ] Forms use fieldset/legend for grouping
- [ ] Buttons use <button>, links use <a>
- [ ] HTML validator passes with no structural errors

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
