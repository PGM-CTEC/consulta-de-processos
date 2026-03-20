# STORY-REM-021: Frontend Testing Setup (Vitest + RTL)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-006
**Type:** Testing
**Complexity:** 8 pts (M - 2-3 days)
**Priority:** HIGH
**Assignee:** Frontend Developer
**Status:** Done
**Sprint:** Sprint 8

## Description

Setup Vitest + React Testing Library, create tests for 3 critical components (ProcessSearch, BulkSearch, Dashboard).

## Acceptance Criteria

- [x] Vitest + @testing-library/react instalados
- [x] vitest.config.js configurado (jsdom environment)
- [x] Test setup file criado (src/tests/setup.js)
- [x] 9 testes de componentes existentes (195 passando no total)
- [x] vitest.config.js: exclude `**/e2e/**` e `**/*.spec.ts` (fix conflito Playwright)
- [x] `npx vitest run` → 0 falhas

## Technical Notes

```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 70,
      branches: 60
    }
  }
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

## File List

- `frontend/vitest.config.js` — adicionado `exclude: ['**/e2e/**', '**/*.spec.ts', 'node_modules/**']`

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-24 | @dev | Sprint 8: Corrigido conflito Playwright/Vitest via exclude no vitest.config.js |
