# STORY-REM-040: Form Validation Library

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-010
**Type:** Code Quality
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Integrate form validation library (React Hook Form + Zod) for consistent, declarative form validation across all forms.

## Acceptance Criteria

- [ ] React Hook Form installed
- [ ] Zod schema validation configured
- [ ] All forms migrated to use React Hook Form
- [ ] Validation errors display inline
- [ ] CNJ number validation schema created
- [ ] Form submission prevents invalid data
- [ ] Performance improved (less re-renders)

## Technical Notes

```javascript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  cnj: z.string().regex(/^\d{20}$/, 'CNJ deve ter 20 dígitos'),
  email: z.string().email('Email inválido')
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema)
});
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
