# STORY-REM-039: PWA Offline Support

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-009
**Type:** Feature
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Convert application to Progressive Web App (PWA) with offline support, service worker, and installability.

## Acceptance Criteria

- [ ] Service worker configured
- [ ] Manifest.json created (name, icons, theme_color)
- [ ] Offline fallback page displayed when no network
- [ ] App installable on mobile/desktop
- [ ] Cached assets for offline viewing
- [ ] Lighthouse PWA score >90

## Technical Notes

```javascript
// vite.config.js
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Consulta Processual',
        short_name: 'ConsultaProc',
        theme_color: '#4f46e5',
        icons: [
          {
            src: 'icon-192.png',
            sizes: '192x192',
            type: 'image/png'
          }
        ]
      }
    })
  ]
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
