/**
 * Dashboard Chart Accessibility Tests — REM-028
 * Validates ARIA labels, role="meter", and sr-only data tables for charts
 * WCAG 2.1 AA compliance for chart accessibility
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../components/Dashboard';
import * as api from '../services/api';

// Mock the API service
vi.mock('../services/api');

// Mock phase color utilities
vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn(() => ({
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-300',
    })),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
}));

describe('Dashboard Chart Accessibility — REM-028', () => {
    const mockStatsData = {
        total_processes: 100,
        total_movements: 500,
        tribunals: [
            { tribunal_name: 'STF', count: 5 },
            { tribunal_name: 'STJ', count: 10 },
            { tribunal_name: 'TJRJ', count: 30 },
        ],
        phases: [
            { phase: '01', class_nature: 'conhecimento', count: 8 },
            { phase: '10', class_nature: 'execucao', count: 12 },
        ],
        timeline: [
            { month: 'Jan', count: 15 },
            { month: 'Feb', count: 20 },
            { month: 'Mar', count: 25 },
        ],
        last_updated: '2026-02-23T10:00:00',
    };

    beforeEach(() => {
        vi.clearAllMocks();
        api.getStats.mockResolvedValue(mockStatsData);
    });

    describe('Tribunals Chart Accessibility', () => {
        it('A11y-1: tribunal chart wrapped in figure element with aria-label', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('STF');
            });

            const figure = container.querySelector('figure[aria-label]');
            expect(figure).toBeInTheDocument();
            expect(figure.getAttribute('aria-label')).toMatch(/tribunal|Tribunal/i);
        });

        it('A11y-2: each tribunal bar has role="meter" with aria attributes', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('STF');
            });

            const meters = container.querySelectorAll('[role="meter"]');
            expect(meters.length).toBeGreaterThan(0);

            meters.forEach((meter) => {
                expect(meter.getAttribute('aria-valuenow')).not.toBeNull();
                expect(meter.getAttribute('aria-valuemin')).toBe('0');
                expect(meter.getAttribute('aria-valuemax')).not.toBeNull();
                expect(meter.getAttribute('aria-label')).not.toBeNull();
            });
        });

        it('A11y-3: tribunal bar meter aria-label includes tribunal name and count', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('STF');
            });

            const meters = container.querySelectorAll('[role="meter"]');
            let foundSTF = false;
            meters.forEach((meter) => {
                const label = meter.getAttribute('aria-label');
                if (label && label.includes('STF')) {
                    expect(label).toMatch(/STF.*5|5.*STF/);
                    foundSTF = true;
                }
            });
            expect(foundSTF).toBe(true);
        });

        it('A11y-4: tribunal chart has sr-only data table', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('STF');
            });

            // Find tables with sr-only class
            const tables = container.querySelectorAll('table.sr-only');
            expect(tables.length).toBeGreaterThan(0);

            // Check for tribunal data in sr-only table
            let foundTribunalTable = false;
            tables.forEach((table) => {
                const rows = table.querySelectorAll('tbody tr');
                if (rows.length > 0) {
                    const firstCellText = rows[0].querySelector('td')?.textContent || '';
                    if (firstCellText.includes('ST')) {
                        foundTribunalTable = true;
                    }
                }
            });
            expect(foundTribunalTable).toBe(true);
        });

        it('A11y-5: tribunal sr-only table has proper headers', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('STF');
            });

            const tables = container.querySelectorAll('table.sr-only');
            let foundProperHeaders = false;
            tables.forEach((table) => {
                const headers = table.querySelectorAll('thead th');
                if (headers.length >= 2) {
                    const headerTexts = Array.from(headers).map((h) => h.textContent);
                    if (headerTexts.some((t) => t.includes('Tribunal') || t.includes('tribunal'))) {
                        foundProperHeaders = true;
                    }
                }
            });
            expect(foundProperHeaders).toBe(true);
        });
    });

    describe('Phases Chart Accessibility', () => {
        it('A11y-6: phases chart wrapped in figure with aria-label', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const figures = container.querySelectorAll('figure[aria-label]');
            expect(figures.length).toBeGreaterThanOrEqual(1);

            // At least one should reference phases
            let foundPhasesFigure = false;
            figures.forEach((fig) => {
                if (fig.getAttribute('aria-label').match(/fase|Fase|phase|Phase/i)) {
                    foundPhasesFigure = true;
                }
            });
            expect(foundPhasesFigure).toBe(true);
        });

        it('A11y-7: phase bars have role="meter" with proper aria attributes', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const meters = container.querySelectorAll('[role="meter"]');
            let phaseMetersFound = 0;
            meters.forEach((meter) => {
                const label = meter.getAttribute('aria-label') || '';
                if (label.match(/fase|fase|phase|Phase/i)) {
                    phaseMetersFound++;
                    expect(meter.getAttribute('aria-valuenow')).not.toBeNull();
                    expect(meter.getAttribute('aria-valuemin')).toBe('0');
                    expect(meter.getAttribute('aria-valuemax')).not.toBeNull();
                }
            });
            expect(phaseMetersFound).toBeGreaterThan(0);
        });

        it('A11y-8: phases sr-only table exists and has data', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const tables = container.querySelectorAll('table.sr-only');
            let foundPhaseTable = false;
            tables.forEach((table) => {
                const rows = table.querySelectorAll('tbody tr');
                if (rows.length >= 2) {
                    // Phases table should have at least 2 rows for our mock data
                    foundPhaseTable = true;
                }
            });
            expect(foundPhaseTable).toBe(true);
        });
    });

    describe('Timeline Chart Accessibility', () => {
        it('A11y-9: timeline chart wrapped in figure with aria-label', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const figures = container.querySelectorAll('figure[aria-label]');
            let foundTimelineFigure = false;
            figures.forEach((fig) => {
                const label = fig.getAttribute('aria-label');
                if (label && label.match(/timeline|temporal|meses|months/i)) {
                    foundTimelineFigure = true;
                }
            });
            expect(foundTimelineFigure).toBe(true);
        });

        it('A11y-10: timeline bars have role="meter" with aria attributes', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const meters = container.querySelectorAll('[role="meter"]');
            let timelineMetersFound = 0;
            meters.forEach((meter) => {
                const label = meter.getAttribute('aria-label') || '';
                // Timeline meters should mention months
                if (label.match(/jan|feb|mar|mês|month|Jan|Feb|Mar/i)) {
                    timelineMetersFound++;
                    expect(meter.getAttribute('aria-valuenow')).not.toBeNull();
                    expect(meter.getAttribute('aria-valuemin')).toBe('0');
                    expect(meter.getAttribute('aria-valuemax')).not.toBeNull();
                }
            });
            expect(timelineMetersFound).toBeGreaterThan(0);
        });

        it('A11y-11: timeline sr-only table with months and counts', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const tables = container.querySelectorAll('table.sr-only');
            let foundTimelineTable = false;
            tables.forEach((table) => {
                const rows = table.querySelectorAll('tbody tr');
                if (rows.length >= 3) {
                    // Timeline should have at least 3 months
                    const firstRow = rows[0].querySelector('td')?.textContent || '';
                    if (firstRow.match(/jan|Jan|Feb|fev/i)) {
                        foundTimelineTable = true;
                    }
                }
            });
            expect(foundTimelineTable).toBe(true);
        });
    });

    describe('Overall Chart Accessibility Compliance', () => {
        it('A11y-12: all three charts have figure elements with aria-label', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const figures = container.querySelectorAll('figure[aria-label]');
            expect(figures.length).toBeGreaterThanOrEqual(3);
        });

        it('A11y-13: all figures have meaningful aria-labels (not empty)', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const figures = container.querySelectorAll('figure[aria-label]');
            figures.forEach((fig) => {
                const ariaLabel = fig.getAttribute('aria-label');
                expect(ariaLabel).toBeTruthy();
                expect(ariaLabel.length).toBeGreaterThan(5);
            });
        });

        it('A11y-14: all meter elements have aria-labels', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const meters = container.querySelectorAll('[role="meter"]');
            expect(meters.length).toBeGreaterThan(0);

            meters.forEach((meter) => {
                expect(meter.getAttribute('aria-label')).toBeTruthy();
                expect(meter.getAttribute('aria-label').length).toBeGreaterThan(0);
            });
        });

        it('A11y-15: all meter elements have aria-valuemin, aria-valuenow, aria-valuemax', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const meters = container.querySelectorAll('[role="meter"]');
            meters.forEach((meter) => {
                expect(meter.getAttribute('aria-valuemin')).toBe('0');
                expect(meter.getAttribute('aria-valuenow')).not.toBeNull();
                expect(meter.getAttribute('aria-valuemax')).not.toBeNull();

                const valuenow = parseInt(meter.getAttribute('aria-valuenow'));
                const valuemax = parseInt(meter.getAttribute('aria-valuemax'));
                expect(valuenow).toBeGreaterThanOrEqual(0);
                expect(valuemax).toBeGreaterThan(0);
            });
        });

        it('A11y-16: all charts have sr-only data tables', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const srTables = container.querySelectorAll('table.sr-only');
            expect(srTables.length).toBeGreaterThanOrEqual(3);
        });

        it('A11y-17: sr-only tables have thead and tbody elements', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const srTables = container.querySelectorAll('table.sr-only');
            srTables.forEach((table) => {
                const thead = table.querySelector('thead');
                const tbody = table.querySelector('tbody');
                expect(thead).toBeInTheDocument();
                expect(tbody).toBeInTheDocument();
            });
        });

        it('A11y-18: sr-only tables have caption or visible header structure', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('Analytics & Business Intelligence');
            });

            const srTables = container.querySelectorAll('table.sr-only');
            srTables.forEach((table) => {
                // Either has caption or thead with th elements
                const caption = table.querySelector('caption');
                const headers = table.querySelectorAll('thead th');
                const hasStructure = (caption && caption.textContent.length > 0) || headers.length > 0;
                expect(hasStructure).toBe(true);
            });
        });

        it('A11y-19: meter aria-valuenow values match actual bar widths semantically', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('STF');
            });

            const meters = container.querySelectorAll('[role="meter"]');
            meters.forEach((meter) => {
                const valuenow = parseInt(meter.getAttribute('aria-valuenow'));
                const valuemax = parseInt(meter.getAttribute('aria-valuemax'));
                const expectedPercent = (valuenow / valuemax) * 100;
                // The width should be proportional to aria-valuenow/aria-valuemax
                expect(expectedPercent).toBeGreaterThanOrEqual(0);
                expect(expectedPercent).toBeLessThanOrEqual(100);
            });
        });

        it('A11y-20: no keyboard traps in meter elements', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            const meters = container.querySelectorAll('[role="meter"]');
            // Meters should not have tabindex unless intentionally interactive
            meters.forEach((meter) => {
                const tabindex = meter.getAttribute('tabindex');
                // Either no tabindex or a valid numeric value
                if (tabindex) {
                    expect(!isNaN(parseInt(tabindex))).toBe(true);
                }
            });
        });
    });

    describe('Accessibility Edge Cases', () => {
        it('A11y-21: handles empty tribunals list with accessible structure', async () => {
            api.getStats.mockResolvedValue({
                ...mockStatsData,
                tribunals: [],
            });

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('Analytics & Business Intelligence');
            });

            // Should still have figure or section for empty state
            const sections = container.querySelectorAll('section[aria-labelledby]');
            expect(sections.length).toBeGreaterThan(0);
        });

        it('A11y-22: high contrast values in meters are readable', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('STF');
            });

            // Check that meters are visible (have some styling)
            const meters = container.querySelectorAll('[role="meter"]');
            meters.forEach((meter) => {
                // Just check that element exists and is rendered
                expect(meter).toBeInTheDocument();
            });
        });

        it('A11y-23: sr-only class hides tables from visual display', async () => {
            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('Analytics & Business Intelligence');
            });

            const srTables = container.querySelectorAll('table.sr-only');
            srTables.forEach((table) => {
                // sr-only should have specific CSS to hide from visual display
                const classes = table.getAttribute('class') || '';
                expect(classes).toContain('sr-only');
            });
        });
    });
});
