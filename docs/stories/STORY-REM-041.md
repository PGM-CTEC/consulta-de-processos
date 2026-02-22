# STORY-REM-041: Analytics/Telemetry

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-011
**Type:** Observability
**Complexity:** 3 pts (S - 1 day)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Integrate analytics (Google Analytics or Plausible) to track user behavior, popular features, and conversion funnels.

## Acceptance Criteria

- [ ] Analytics library selected (GA4 or Plausible)
- [ ] Tracking code installed
- [ ] Page views tracked automatically
- [ ] Custom events tracked (search, bulk upload, export)
- [ ] Privacy policy updated
- [ ] GDPR consent banner (if using GA)
- [ ] Analytics dashboard configured

## Technical Notes

```javascript
// Option 1: Plausible (privacy-friendly)
<script defer data-domain="consulta-processo.com" src="https://plausible.io/js/script.js"></script>

// Option 2: Google Analytics 4
import ReactGA from 'react-ga4';

ReactGA.initialize('G-XXXXXXXXXX');

// Track page view
ReactGA.send({ hitType: 'pageview', page: window.location.pathname });

// Track custom event
ReactGA.event({
  category: 'Search',
  action: 'CNJ Search',
  label: 'Single Process'
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
