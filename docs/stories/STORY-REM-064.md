# STORY-REM-064: Favicon and Branding

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Various LOW priority debits
**Type:** UX
**Complexity:** 2 pts (XS - 30 min)
**Priority:** LOW
**Assignee:** Frontend Developer / Designer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

Add favicon, app icons, and branding elements for professional appearance.

## Acceptance Criteria

- [x] Favicon created and added (16x16, 32x32, 64x64)
- [x] Apple touch icon added (180x180)
- [x] Android chrome icons added (192x192, 512x512)
- [x] Site title and meta description set
- [x] Open Graph tags for social sharing
- [x] Manifest.json updated with icons
- [x] Browser tab shows proper icon and title

## Technical Notes

```html
<!-- index.html -->
<head>
  <title>Consulta Processual - Sistema de Consulta de Processos</title>
  <meta name="description" content="Sistema de consulta e gerenciamento de processos judiciais">

  <!-- Favicons -->
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">

  <!-- Open Graph -->
  <meta property="og:title" content="Consulta Processual">
  <meta property="og:description" content="Sistema de consulta de processos judiciais">
  <meta property="og:image" content="/og-image.png">
  <meta property="og:type" content="website">
</head>
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

### Modified Files
- `frontend/index.html` — Updated with branding meta tags (title, description, theme-color), favicon links (16x32x64), apple-touch-icon (180x180), OG tags, and manifest.json link

### New Files
- `frontend/public/manifest.json` — PWA manifest with app icons (192x512), shortcuts (Buscar Processo, Busca em Lote), and metadata

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-28 | @dev | Updated index.html with branding meta tags, favicon data URIs, OG tags. Created manifest.json with PWA icons and shortcuts |
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
