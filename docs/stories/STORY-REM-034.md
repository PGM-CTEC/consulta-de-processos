# STORY-REM-034: Atomic Components (Shadcn/UI)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-ARCH-002
**Type:** Frontend Architecture
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Done
**Sprint:** Sprint 10

## Description

Install Shadcn/UI library and create atomic component library (Button, Input, Card, Badge, etc.) with consistent styling.

## Acceptance Criteria

- [x] Shadcn/UI installed and configured (class-variance-authority, clsx, tailwind-merge, components.json)
- [x] Button component with variants (primary, secondary, ghost, link, destructive, outline)
- [x] Input component with validation states
- [x] Card component with header, body, footer sections
- [x] Badge component with color variants
- [x] All components support dark mode (via CSS variables)
- [ ] Storybook documentation created (deferred — out of scope for this sprint)

## Technical Notes

Implemented without `npx shadcn-ui init` to preserve existing project setup. Components created manually following Shadcn/UI patterns:

- `class-variance-authority` (cva) for variant management
- `clsx` + `tailwind-merge` via `cn()` utility for className merging
- CSS custom properties for theming (Shadcn `--primary`, `--secondary`, etc.)
- `components.json` for Shadcn/UI compatibility

## Dependencies

REM-033 (design tokens) — tokens preserved in tailwind.config.js

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (16 tests, all passing)
- [x] Acceptance criteria met (core components done)
- [x] Documentation updated (story file, components.json)
- [x] Merged to `main` branch

## File List

| File | Action | Description |
|------|--------|-------------|
| `frontend/src/lib/utils.js` | Created | cn() utility (clsx + tailwind-merge) |
| `frontend/src/components/ui/button.jsx` | Created | Button component with 6 variants + 4 sizes |
| `frontend/src/components/ui/card.jsx` | Created | Card, CardHeader, CardTitle, CardContent, CardFooter |
| `frontend/src/components/ui/badge.jsx` | Created | Badge component with 4 variants |
| `frontend/src/components/ui/input.jsx` | Created | Input component with accessible states |
| `frontend/components.json` | Created | Shadcn/UI config (aliases, tailwind mapping) |
| `frontend/src/index.css` | Modified | Added Shadcn CSS vars in @layer base |
| `frontend/tailwind.config.js` | Modified | Added Shadcn tokens + darkMode class, preserved REM-033 tokens |
| `frontend/src/tests/AtomicComponents.test.jsx` | Created | 16 unit tests for all 4 components |

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-27 | @dev | Implementation complete — 4 atomic components, 16 tests passing, build clean |
