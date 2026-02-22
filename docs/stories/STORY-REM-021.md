# STORY-REM-021: Frontend Testing Setup (Vitest + RTL)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-006
**Type:** Testing
**Complexity:** 8 pts (M - 2-3 days)
**Priority:** HIGH
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 3

## Description

Setup Vitest + React Testing Library, create tests for 3 critical components (ProcessSearch, BulkSearch, Dashboard).

## Acceptance Criteria

- [ ] Vitest + @testing-library/react installed
- [ ] vitest.config.js configured (jsdom environment)
- [ ] Test setup file created (src/test/setup.js)
- [ ] ProcessSearch.test.jsx: 3 tests (validation, submit, loading)
- [ ] BulkSearch.test.jsx: 3 tests (file upload, export, results)
- [ ] Dashboard.test.jsx: 3 tests (KPIs, charts, empty state)
- [ ] Coverage report: >40% (foundation, 70% target later)
- [ ] CI runs frontend tests

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

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
