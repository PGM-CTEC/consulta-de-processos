# STORY-REM-060: Code Comments and Docstrings

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Various LOW priority debits
**Type:** Code Quality
**Complexity:** 5 pts (M - 1 day)
**Priority:** LOW
**Assignee:** Backend Developer / Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Add comprehensive docstrings and comments to all functions, classes, and complex logic for better code maintainability.

## Acceptance Criteria

- [ ] All public functions have docstrings
- [ ] All classes have docstrings
- [ ] Complex logic has explanatory comments
- [ ] JSDoc comments for frontend functions
- [ ] Google-style or NumPy-style docstrings (backend)
- [ ] API documentation auto-generated from docstrings

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
