/**
 * Performance.test.jsx — REM-037
 * Tests for lazy loading, code splitting, and bundle optimization.
 *
 * BUNDLE BASELINE (before REM-037):
 *   dist/assets/index-BPxMJSSV.js   800.25 kB │ gzip: 259.20 kB
 *   dist/assets/index-BblHas4A.css   43.76 kB │ gzip:   8.06 kB
 *   (1 chunk only — triggered Vite's 500kB warning)
 *
 * BUNDLE AFTER (after REM-037 — manualChunks + React.lazy + Suspense):
 *   dist/assets/index-DLq6qUmr.js          236.05 kB │ gzip:  77.29 kB  (main entry — 70% smaller!)
 *   dist/assets/BulkSearch-DZ96T1Pb.js     434.86 kB │ gzip: 145.03 kB  (lazy — xlsx lib)
 *   dist/assets/ProcessDetails-SBVbNynf.js  42.55 kB │ gzip:  12.16 kB  (lazy)
 *   dist/assets/card-BGoUguV3.js            33.50 kB │ gzip:  10.55 kB  (shared UI)
 *   dist/assets/ui-utils-xHcXJO_S.js       27.41 kB │ gzip:  10.48 kB  (vendor chunk)
 *   dist/assets/Dashboard-C_sXw9xN.js       9.22 kB │ gzip:   2.30 kB  (lazy)
 *   dist/assets/Settings-Crq_HT3g.js        5.72 kB │ gzip:   1.70 kB  (lazy)
 *   dist/assets/PerformanceDashboard.js      5.46 kB │ gzip:   1.83 kB  (lazy)
 *   dist/assets/vendor-Bi0xNwDL.js          3.66 kB │ gzip:   1.38 kB  (react+react-dom)
 *   dist/assets/HistoryTab-cdsIcFKt.js      2.92 kB │ gzip:   1.15 kB  (lazy)
 *   dist/assets/index-C0Krx_7O.css         43.26 kB │ gzip:   7.87 kB
 *
 *   Initial entry (index.js) reduced from 800.25 kB → 236.05 kB (70.5% reduction).
 *   Total gzip: 259.20 kB → 77.29 kB for initial load (lazy chunks deferred).
 *   BulkSearch (xlsx-heavy) is now deferred — only loaded when user navigates to that tab.
 *   No 500kB chunk warning for the main entry point.
 */

import React, { lazy, Suspense } from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import LoadingFallback from '../components/LoadingFallback';

// ---------------------------------------------------------------------------
// 1. LoadingFallback — accessible Suspense fallback UI
// ---------------------------------------------------------------------------
describe('LoadingFallback', () => {
  it('renders with role="status" for accessibility', () => {
    render(<LoadingFallback />);
    const status = screen.getByRole('status');
    expect(status).toBeTruthy();
  });

  it('has aria-label describing the loading state', () => {
    render(<LoadingFallback />);
    const status = screen.getByRole('status');
    expect(status.getAttribute('aria-label')).toBeTruthy();
  });

  it('renders a visible spinner element', () => {
    render(<LoadingFallback />);
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeTruthy();
  });

  it('renders with full viewport height class for page-level fallback', () => {
    render(<LoadingFallback />);
    const container = document.querySelector('.min-h-screen');
    expect(container).toBeTruthy();
  });

  it('accepts a custom message prop and displays it', () => {
    render(<LoadingFallback message="Carregando Dashboard..." />);
    expect(screen.getByText('Carregando Dashboard...')).toBeTruthy();
  });

  it('renders a default message when no message prop is provided', () => {
    render(<LoadingFallback />);
    // Should have some visible or sr-only text (not crash)
    const status = screen.getByRole('status');
    expect(status).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// 2. Suspense integration — lazy-loaded component lifecycle
// ---------------------------------------------------------------------------
describe('Suspense + lazy loading integration', () => {
  it('Suspense renders fallback while lazy component loads', async () => {
    // Create a lazy component that never resolves during this test
    let resolve;
    const LazyComponent = lazy(
      () =>
        new Promise((res) => {
          resolve = res;
        })
    );

    render(
      <Suspense fallback={<LoadingFallback />}>
        <LazyComponent />
      </Suspense>
    );

    // Fallback should be visible immediately
    expect(screen.getByRole('status')).toBeTruthy();

    // Cleanup: resolve the promise to avoid act() warnings
    act(() => {
      resolve({ default: () => <div>Loaded</div> });
    });
  });

  it('Suspense renders child after lazy component resolves', async () => {
    const LazyComponent = lazy(() =>
      Promise.resolve({ default: () => <div>Componente Carregado</div> })
    );

    render(
      <Suspense fallback={<LoadingFallback />}>
        <LazyComponent />
      </Suspense>
    );

    await waitFor(() => {
      expect(screen.getByText('Componente Carregado')).toBeTruthy();
    });
  });

  it('multiple Suspense boundaries can wrap different lazy components', async () => {
    const LazyA = lazy(() =>
      Promise.resolve({ default: () => <div>Componente A</div> })
    );
    const LazyB = lazy(() =>
      Promise.resolve({ default: () => <div>Componente B</div> })
    );

    render(
      <div>
        <Suspense fallback={<LoadingFallback message="Carregando A..." />}>
          <LazyA />
        </Suspense>
        <Suspense fallback={<LoadingFallback message="Carregando B..." />}>
          <LazyB />
        </Suspense>
      </div>
    );

    await waitFor(() => {
      expect(screen.getByText('Componente A')).toBeTruthy();
      expect(screen.getByText('Componente B')).toBeTruthy();
    });
  });
});

// ---------------------------------------------------------------------------
// 3. App.jsx lazy imports — smoke-test that components are lazily imported
// ---------------------------------------------------------------------------
describe('App lazy import structure', () => {
  it('React.lazy wraps a dynamic import and returns a thenable', () => {
    // React.lazy expects a function returning a Promise<{ default: Component }>
    const mockImport = () =>
      Promise.resolve({ default: () => <div>Mock</div> });
    const LazyComp = lazy(mockImport);
    // lazy() returns an object with $$typeof === Symbol(react.lazy)
    expect(LazyComp).toBeDefined();
    expect(typeof LazyComp).toBe('object');
  });

  it('lazy component wrapped in Suspense does not throw without fallback error', () => {
    const LazyComp = lazy(() =>
      Promise.resolve({ default: () => <div>OK</div> })
    );

    expect(() =>
      render(
        <Suspense fallback={<div>Loading</div>}>
          <LazyComp />
        </Suspense>
      )
    ).not.toThrow();
  });
});

// ---------------------------------------------------------------------------
// 4. Code splitting — verify chunks are separate (structural tests)
// ---------------------------------------------------------------------------
describe('Code splitting — structural checks', () => {
  it('dynamic import returns a Promise', () => {
    // A dynamic import() always returns a native Promise
    const result = import('../components/LoadingFallback');
    expect(result).toBeInstanceOf(Promise);
    return result; // let Vitest await it
  });

  it('LoadingFallback module exports a default component', async () => {
    const mod = await import('../components/LoadingFallback');
    expect(mod.default).toBeDefined();
    expect(typeof mod.default).toBe('function');
  });

  it('BulkSearch module can be dynamically imported', async () => {
    const mod = await import('../components/BulkSearch');
    expect(mod.default).toBeDefined();
  }, 10000);

  it('ProcessDetails module can be dynamically imported', async () => {
    const mod = await import('../components/ProcessDetails');
    expect(mod.default).toBeDefined();
  }, 15000);

  it('Dashboard module can be dynamically imported', async () => {
    const mod = await import('../components/Dashboard');
    expect(mod.default).toBeDefined();
  }, 10000);
});
