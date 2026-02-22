# STORY-REM-034: Atomic Components (Shadcn/UI)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-ARCH-002
**Type:** Frontend Architecture
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Install Shadcn/UI library and create atomic component library (Button, Input, Card, Badge, etc.) with consistent styling.

## Acceptance Criteria

- [ ] Shadcn/UI installed and configured
- [ ] Button component with variants (primary, secondary, ghost, link)
- [ ] Input component with validation states
- [ ] Card component with header, body, footer sections
- [ ] Badge component with color variants
- [ ] All components support dark mode
- [ ] Storybook documentation created

## Technical Notes

```bash
# Install Shadcn/UI
npx shadcn-ui@latest init

# Add components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add badge
```

## Dependencies

REM-033 (design tokens)

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
