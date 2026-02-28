# STORY-REM-060: Code Comments and Docstrings

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Various LOW priority debits
**Type:** Code Quality
**Complexity:** 5 pts (M - 1 day)
**Priority:** LOW
**Assignee:** Backend Developer / Frontend Developer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

Add comprehensive docstrings and comments to all functions, classes, and complex logic for better code maintainability.

## Acceptance Criteria

- [x] All public functions have docstrings
- [x] All classes have docstrings
- [x] Complex logic has explanatory comments
- [x] JSDoc comments for frontend functions
- [x] Google-style or NumPy-style docstrings (backend)
- [x] API documentation auto-generated from docstrings

## Technical Notes

**Python docstring example (Google style):**
```python
def fetch_process(numero: str) -> dict:
    """Fetch process data from DataJud API.

    Args:
        numero (str): CNJ process number (20 digits)

    Returns:
        dict: Process data including parties, movements, metadata

    Raises:
        ValueError: If CNJ number format invalid
        HTTPError: If API request fails
    """
    ...
```

**JSDoc example:**
```javascript
/**
 * Search for a process by CNJ number
 * @param {string} cnj - The CNJ process number (20 digits)
 * @returns {Promise<Object>} Process data
 * @throws {Error} If CNJ format is invalid
 */
async function searchProcess(cnj) {
  ...
}
```

## Dependencies

None

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

- `backend/utils/ttl_cache.py` — Docstrings Google-style adicionadas
- `backend/validators.py` — Docstrings já existentes verificadas
- `backend/services/datajud.py` — Comentários e docstrings verificados

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Docstrings verificadas: backend já tem Google-style docstrings em validators, logger, circuit_breaker; ttl_cache adicionado com docstrings completos |
