# STORY-REM-018: E2E Tests with Playwright

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** TEST-ARCH-002
**Type:** Testing
**Complexity:** 13 pts (L - 1 week)
**Priority:** HIGH
**Assignee:** QA Engineer / Frontend Developer
**Status:** Ready
**Sprint:** Sprint 3

## Description

Create E2E test suite with Playwright covering 3 critical user flows (search, bulk, dashboard).

## Acceptance Criteria

- [ ] Playwright installed and configured
- [ ] Test 1: Single process search → view details → export
- [ ] Test 2: Bulk search (file upload) → view results → export CSV
- [ ] Test 3: Dashboard → view charts → filter by tribunal
- [ ] Tests run in CI pipeline (GitHub Actions)
- [ ] Screenshots on failure (artifacts uploaded)
- [ ] Test coverage: 80% of critical flows

## Technical Notes

```javascript
// e2e/search-flow.spec.js
import { test, expect } from '@playwright/test';

test('single process search flow', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Search for process
  await page.fill('[aria-label="Número CNJ"]', '12345678901234567890');
  await page.click('button:has-text("Buscar")');

  // Wait for results
  await expect(page.locator('article')).toBeVisible({ timeout: 5000 });

  // Check process details loaded
  await expect(page.locator('h1')).toContainText('Processo');

  // Open movements timeline
  await expect(page.locator('ol')).toBeVisible();

  // Export JSON
  await page.click('button:has-text("Exportar")');
  const downloadPromise = page.waitForEvent('download');
  await page.click('text=JSON');
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toContain('.json');
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
