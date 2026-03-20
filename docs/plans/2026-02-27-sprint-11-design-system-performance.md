# Sprint 11 Plan — Design System Consolidation + Performance & UX

**Data:** 2026-02-27
**Status:** Ready for Execution
**Branch:** `sprint-11` (a criar)
**Base:** `main` (ab221f5)

---

## Executive Summary

Sprint 11 consolidates the Design System introduced in Sprint 10 and initiates Performance/UX improvements. All stories are Ready status; no dependency delays.

| Phase | Duration | Stories | Points | Agent |
|-------|----------|---------|--------|-------|
| Design System | 2-3 days | REM-035, REM-036 | 13 | @dev |
| Performance | 2-3 days | REM-037, REM-038 | 16 | @dev |
| UX/Forms | 1-2 days | REM-040 | 8 | @dev |
| **Total** | **5-8 days** | **5 stories** | **37 pts** | — |

---

## Stories in Scope

### Wave 1: Design System Consolidation (REM-035 + REM-036)

#### REM-035: Component Migration to Design System
- **Complexity:** 8 pts (M - 3-5 days)
- **Priority:** MEDIUM
- **Description:** Migrate existing components (Dashboard, BulkSearch, ProcessDetails) to use Button, Card, Badge, Input from Sprint 10
- **Key Changes:**
  - Replace inline `<button>` with `<Button variant="..." />` from `components/ui/button.jsx`
  - Dashboard card layout → `<Card>` component
  - Status badges → `<Badge>` component
  - Form inputs → `<Input>` component
- **Testing:** Visual regression tests, component composition tests
- **Dependencies:** REM-034 (atomic components library) — ✅ Done

#### REM-036: Storybook Setup
- **Complexity:** 5 pts (M - 1 day)
- **Priority:** MEDIUM
- **Description:** Setup Storybook to document atomic components and design system
- **Key Tasks:**
  - Install Storybook 8.x with React preset
  - Create stories for Button (6 variants), Card, Badge (4 variants), Input
  - Add Tailwind CSS addon for live theme switching
  - Configure dark mode preview
  - Deploy to GitHub Pages (CI/CD integration)
- **Testing:** Storybook builds without errors, all stories render correctly
- **Dependencies:** REM-034, REM-035

### Wave 2: Frontend Performance (REM-037 + REM-038)

#### REM-037: Frontend Performance Optimization
- **Complexity:** 8 pts (M - 3-5 days)
- **Priority:** MEDIUM
- **Description:** Optimize bundle size, implement lazy loading, code splitting
- **Key Tasks:**
  - Analyze bundle with `npm run build` and webpack-bundle-analyzer
  - Implement React.lazy() + Suspense for ProcessDetails modal, BulkSearch
  - Code split at route level (React Router)
  - Tree-shake unused CSS from Tailwind
  - Enable gzip compression in Vite
  - Lighthouse audit: Target >85 Performance score
- **Testing:** Lighthouse CI check, bundle size regression tests
- **Dependencies:** None blocking, but REM-035/036 should be done first for clean refactor

#### REM-038: Pagination/Virtualization
- **Complexity:** 8 pts (M - 3-5 days)
- **Priority:** MEDIUM
- **Description:** Add virtualization for large process lists (bulk search results)
- **Key Tasks:**
  - Integrate `react-window` or `tanstack/react-virtual`
  - Implement pagination UI (10/25/50 items per page)
  - Virtual scrolling for >1000 items
  - Optimize row rendering with memo()
  - Performance test: <500ms render for 10k items
- **Testing:** Performance benchmarks, scrolling behavior tests
- **Dependencies:** None blocking

### Wave 3: UX/Forms (REM-040)

#### REM-040: Form Validation Library
- **Complexity:** 8 pts (M - 3-5 days)
- **Priority:** MEDIUM
- **Description:** Implement form validation using react-hook-form + Zod in BulkSearch
- **Key Tasks:**
  - Install `react-hook-form` + `zod` + `@hookform/resolvers`
  - Create validation schema for BulkSearch form (process number format, file size)
  - Integrate with existing form (retain file upload drag-drop)
  - Add real-time validation feedback with error messages
  - Accessibility: `aria-invalid`, `aria-describedby` for error messages
  - Unit tests for validation rules
- **Testing:** Form submit/validation tests, accessibility audit
- **Dependencies:** None blocking

---

## Execution Strategy

### Subagent-Driven Development

**Workflow:**
1. Create `sprint-11` branch from `main`
2. Execute tasks in parallel (Wave 1 in isolation, then Wave 2 independently)
3. Use spec-compliance-check + code-quality-check per task
4. QA loop: Review → Fix → Re-review (max 5 iterations)
5. Final PR creation and merge to `main`

**Branch Management:**
- Feature branch: `sprint-11`
- Commits: `feat:` + story ID (e.g., `feat: migrate components to design system [REM-035]`)
- PR: Merge `sprint-11` → `main` when all tasks complete

---

## Quality Gates

- ✅ All 303 existing frontend tests must pass
- ✅ New tests: REM-035 (15 tests), REM-036 (12 tests), REM-037 (10 tests), REM-038 (12 tests), REM-040 (18 tests)
- ✅ CodeRabbit review: CRITICAL/HIGH auto-fixed, MEDIUM documented as debt
- ✅ Lighthouse CI: >85 Performance score (REM-037)
- ✅ Axe accessibility audit: 0 violations (maintain Sprint 10 standard)

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Component migration breaks existing UI | Incremental migration with visual regression tests |
| Storybook build complexity | Use latest Storybook presets, test early |
| Bundle size grows with new deps | Analyze and tree-shake aggressively |
| Virtualization performance issues | Profile with React DevTools, optimize row component |
| Form validation UX problems | User testing with accessibility validator |

---

## Success Criteria

- [ ] All 5 stories marked `Done` (status: Done in story files)
- [ ] All acceptance criteria met per story
- [ ] 67+ new tests (across all stories)
- [ ] 303+ existing tests still passing
- [ ] Lighthouse Performance >85
- [ ] Axe audit 0 violations
- [ ] PR #2 created and merged to `main`

---

## Timeline

| Date | Phase | Tasks |
|------|-------|-------|
| 2026-02-27 | Day 1-2 | REM-035, REM-036 (Wave 1) |
| 2026-02-28 | Day 3-4 | REM-037, REM-038 (Wave 2) |
| 2026-03-01 | Day 5 | REM-040 (Wave 3) + QA loop |
| 2026-03-02 | Day 6 | Final QA + PR creation |

---

## Execution Modes Available

**Option 1:** Review plan, then start Subagent-Driven Development
**Option 2:** Jump directly to implementation (YOLO mode)

---

**Plan Status:** Ready for Approval
**Created by:** @pm (Morgan)
**Next Step:** Choose execution mode or adjust scope
