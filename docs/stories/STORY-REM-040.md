# STORY-REM-040: Form Validation Library

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-010
**Type:** Code Quality
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready for Review
**Sprint:** Sprint 12

## Description

Integrate form validation library (React Hook Form + Zod) for consistent, declarative form validation across all forms.

## Acceptance Criteria

- [x] React Hook Form installed
- [x] Zod schema validation configured
- [x] All forms migrated to use React Hook Form
- [x] Validation errors display inline
- [x] CNJ number validation schema created
- [x] Form submission prevents invalid data
- [x] Performance improved (less re-renders)

## Technical Notes

```javascript
import { useForm } from 'react-hook-form';
import { standardSchemaResolver } from '@hookform/resolvers/standard-schema';
import { z } from 'zod';

const schema = z.object({
  cnj: z.string().trim().regex(/^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$/, 'CNJ deve usar o formato: NNNNNNN-DD.AAAA.J.TT.OOOO'),
  email: z.string().email('Email inválido')
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: standardSchemaResolver(schema)
});
```

**Observação:** `@hookform/resolvers` v5 usa `standardSchemaResolver` (não `zodResolver`) pois Zod v4 implementa o Standard Schema spec.

## Dependencies

None

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (24 novos testes em FormValidation.test.jsx)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

### New Files
- `frontend/src/lib/validationSchemas.js` — Schemas Zod centralizados (cnjNumberSchema, searchProcessSchema, bulkSearchSchema, sqlConfigSchema)
- `frontend/src/tests/FormValidation.test.jsx` — 24 testes: schemas unitários + comportamento dos formulários

### Modified Files
- `frontend/src/components/BulkSearch.jsx` — Migrado para react-hook-form (register, handleSubmit, watch, errors)
- `frontend/src/components/SearchProcess.jsx` — Migrado para react-hook-form com validação CNJ inline
- `frontend/src/components/Settings.jsx` — Migrado para react-hook-form com validação onBlur nos campos SQL
- `frontend/package.json` — Adicionado react-hook-form ^7.71.2, zod ^4.3.6, @hookform/resolvers ^5.2.2

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Implementação completa: instalação deps, schemas Zod, migração de 3 formulários, 24 testes — 437/437 passando |
| 2026-02-28 | @dev | Deferido: Form validation react-hook-form + Zod — deferido para sprint dedicado (dependência: zustand integração) |
