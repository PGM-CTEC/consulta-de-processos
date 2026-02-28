# STORY-REM-007: Add Label HTML Associations (Accessibility)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 | **Complexity:** 2 pts (XS - 30min) | **Priority:** MEDIUM
**Assignee:** Frontend Developer | **Status:** Done

---

## Description

Add htmlFor attribute to all form labels (15+ fields) for WCAG 1.3.1 compliance.

## Acceptance Criteria

- [x] BulkSearch.jsx textarea has htmlFor="bulk-numbers-textarea"
- [x] Settings.jsx: All 15+ fields have htmlFor associations
- [x] Axe accessibility audit passes
- [x] Screen reader test: Labels announced on focus

## Implementation

```jsx
// BEFORE
<label>Listagem de Números</label>
<textarea />

// AFTER
<label htmlFor="bulk-numbers-textarea">Listagem de Números</label>
<textarea id="bulk-numbers-textarea" />
```

## Files

- `frontend/src/components/BulkSearch.jsx` (modified)
- `frontend/src/components/Settings.jsx` (modified)


## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-28 | @dev | Verificado: htmlFor presente em BulkSearch.jsx e Settings.jsx (15+ campos) |
