# STORY-REM-033: Token Extraction (Design System)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-ARCH-002
**Type:** Frontend Architecture
**Complexity:** 5 pts (M - 1 day)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Extract design tokens (colors, spacing, typography, shadows) from inline CSS to centralized token system for consistency.

## Acceptance Criteria

- [ ] tokens.css or tokens.js file created
- [ ] Color palette defined (primary, secondary, neutral, semantic colors)
- [ ] Spacing scale defined (4px, 8px, 12px, 16px, 24px, 32px, etc.)
- [ ] Typography scale defined (font sizes, weights, line heights)
- [ ] Shadow/elevation tokens defined
- [ ] All components migrated to use tokens
- [ ] Documentation of token usage

## Technical Notes

```css
/* tokens.css */
:root {
  /* Colors */
  --color-primary-600: #4f46e5;
  --color-primary-700: #4338ca;

  /* Spacing */
  --spacing-1: 0.25rem; /* 4px */
  --spacing-2: 0.5rem;  /* 8px */
  --spacing-4: 1rem;    /* 16px */

  /* Typography */
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
}
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
