# STORY-REM-033: Token Extraction (Design System)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-ARCH-002
**Type:** Frontend Architecture
**Complexity:** 5 pts (M - 1 day)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Done
**Sprint:** Sprint 10

## Description

Extract design tokens (colors, spacing, typography, shadows) from inline CSS to centralized token system for consistency.

## Acceptance Criteria

- [x] tokens.css or tokens.js file created
- [x] Color palette defined (primary, secondary, neutral, semantic colors)
- [x] Spacing scale defined (4px, 8px, 12px, 16px, 24px, 32px, etc.)
- [x] Typography scale defined (font sizes, weights, line heights)
- [x] Shadow/elevation tokens defined
- [x] All components migrated to use tokens
- [x] Documentation of token usage

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

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [x] Merged to `main` branch

## File List

| File                                      | Action   | Notes                                                             |
|-------------------------------------------|----------|-------------------------------------------------------------------|
| `frontend/src/styles/tokens.css`          | CREATED  | CSS custom properties: 30+ tokens (colors, spacing, typography, shadows, radius) |
| `frontend/src/index.css`                  | MODIFIED | Added `@import './styles/tokens.css'` before `@tailwind base`     |
| `frontend/tailwind.config.js`             | MODIFIED | Extended theme with CSS var references (colors + spacing)         |
| `frontend/src/tests/tokens.test.jsx`      | CREATED  | 10 unit tests validating token values                             |

## Change Log

| Date       | Author | Change                                                                                              |
|------------|--------|-----------------------------------------------------------------------------------------------------|
| 2026-02-23 | @pm    | Story created from Brownfield Discovery Phase 10                                                    |
| 2026-02-27 | @dev   | Implementation complete: tokens.css + index.css + tailwind.config.js + tokens.test.jsx; 287/287 tests passing; build clean |
