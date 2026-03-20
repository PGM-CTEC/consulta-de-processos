/**
 * Axe Accessibility Audit — REM-031 AC5
 * Runs Axe DevTools to verify zero contrast violations and other a11y issues
 *
 * WCAG 2.1 AA Requirements verified:
 * - No contrast issues
 * - No structural accessibility issues
 * - Proper ARIA labeling
 * - Keyboard navigation support
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import Dashboard from '../components/Dashboard';
import BulkSearch from '../components/BulkSearch';

// Extend Vitest matchers with jest-axe matchers
expect.extend(toHaveNoViolations);

// Mock API calls to prevent real requests during tests
vi.mock('../services/api', () => ({
  getStats: vi.fn().mockResolvedValue({
    total_processes: 150,
    total_movements: 1250,
    tribunals: [
      { name: 'STJ', count: 50 },
      { name: 'TJSP', count: 45 },
      { name: 'TJRJ', count: 55 },
    ],
    phases: [
      { name: 'Conhecimento', count: 80 },
      { name: 'Execução', count: 70 },
    ],
    timeline: [
      { month: 'Jan', count: 25 },
      { month: 'Feb', count: 35 },
    ],
    success_rate: 95,
    last_updated: new Date().toISOString(),
  }),
  bulkSearch: vi.fn().mockResolvedValue([]),
}));

describe('Axe DevTools Accessibility Audit — REM-031', () => {
  beforeEach(() => {
    // Clear any previous violations
    vi.clearAllMocks();
  });

  describe('Dashboard Component — No Contrast Violations', () => {
    it('Dashboard renders with no Axe violations', { timeout: 15000 }, async () => {
      const { container } = render(<Dashboard />);

      // Allow time for component to mount
      await new Promise(resolve => setTimeout(resolve, 100));

      const results = await axe(container);

      // Verify NO violations at all
      expect(results.violations).toHaveLength(0);
      expect(results).toHaveNoViolations();
    });

    it('Dashboard has no contrast violations specifically', { timeout: 15000 }, async () => {
      const { container } = render(<Dashboard />);

      await new Promise(resolve => setTimeout(resolve, 100));

      const results = await axe(container, {
        rules: {
          // Focus only on color contrast rules
          'color-contrast': { enabled: true },
        },
      });

      const contrastViolations = results.violations.filter(
        v => v.id === 'color-contrast'
      );

      expect(contrastViolations).toHaveLength(0);
    });

    it('Dashboard has no critical/serious a11y violations', { timeout: 15000 }, async () => {
      const { container } = render(<Dashboard />);

      await new Promise(resolve => setTimeout(resolve, 100));

      const results = await axe(container);

      const seriousViolations = results.violations.filter(
        v => v.impact === 'critical' || v.impact === 'serious'
      );

      expect(seriousViolations).toHaveLength(0);
    });
  });

  describe('BulkSearch Component — No Contrast Violations', () => {
    it('BulkSearch renders with no Axe violations', { timeout: 15000 }, async () => {
      const { container } = render(<BulkSearch />);

      await new Promise(resolve => setTimeout(resolve, 100));

      const results = await axe(container);

      if (results.violations.length > 0) {
        console.log('BulkSearch Violations:', JSON.stringify(results.violations, null, 2));
      }

      expect(results.violations).toHaveLength(0);
      expect(results).toHaveNoViolations();
    });

    it('BulkSearch has no contrast violations specifically', { timeout: 15000 }, async () => {
      const { container } = render(<BulkSearch />);

      await new Promise(resolve => setTimeout(resolve, 100));

      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });

      const contrastViolations = results.violations.filter(
        v => v.id === 'color-contrast'
      );

      expect(contrastViolations).toHaveLength(0);
    });

    it('BulkSearch has no critical/serious a11y violations', { timeout: 15000 }, async () => {
      const { container } = render(<BulkSearch />);

      await new Promise(resolve => setTimeout(resolve, 100));

      const results = await axe(container);

      const seriousViolations = results.violations.filter(
        v => v.impact === 'critical' || v.impact === 'serious'
      );

      expect(seriousViolations).toHaveLength(0);
    });
  });

  describe('Accessibility Compliance Summary', () => {
    it('Dashboard and BulkSearch combined have zero a11y violations', { timeout: 20000 }, async () => {
      const dashboardResults = await axe(
        render(<Dashboard />).container
      );
      const bulkSearchResults = await axe(
        render(<BulkSearch />).container
      );

      const allViolations = [
        ...dashboardResults.violations,
        ...bulkSearchResults.violations,
      ];

      expect(allViolations).toHaveLength(0);
    });

    it('All color text ratios meet WCAG 2.1 AA (4.5:1 minimum for normal text)', { timeout: 20000 }, async () => {
      // This is verified by Axe color-contrast rule
      const { container } = render(
        <div>
          <Dashboard />
          <BulkSearch />
        </div>
      );

      await new Promise(resolve => setTimeout(resolve, 100));

      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });

      expect(results.violations).toHaveLength(0);
    });
  });
});
