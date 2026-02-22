# STORY-REM-035: Component Migration to Design System

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-ARCH-002
**Type:** Frontend Architecture
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Migrate all existing components to use new design system components and tokens, ensuring visual consistency.

## Acceptance Criteria

- [ ] All 9 components migrated to use atomic components
- [ ] No hardcoded colors (all use tokens)
- [ ] No hardcoded spacing values (all use spacing scale)
- [ ] Visual regression tests pass
- [ ] No breaking changes to component APIs
- [ ] Consistent styling across all pages

## Technical Notes

- Replace custom buttons with design system Button
- Replace custom inputs with design system Input
- Replace custom cards with design system Card
- Update spacing to use design tokens
- Test each component after migration

## Dependencies

REM-034 (atomic components)

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
