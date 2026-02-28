# STORY-REM-039: PWA Offline Support

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** FE-009
**Type:** Feature
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

Convert application to Progressive Web App (PWA) with offline support, service worker, and installability.

## Acceptance Criteria

- [x] Service worker configured
- [x] Manifest.json created (name, icons, theme_color)
- [x] Offline fallback page displayed when no network
- [x] App installable on mobile/desktop
- [x] Cached assets for offline viewing
- [x] Lighthouse PWA score >90

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

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [x] Merged to `main` branch

## File List

_To be updated during development_

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-28 | @dev | Service worker adicionado: cache-first para estaticos, network-first para API, fallback offline |
| 2026-02-28 | @dev | Service worker adicionado: cache-first para estaticos, network-first para API, fallback offline |
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
