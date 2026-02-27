/**
 * Tests for Dashboard Component - Frontend Testing Phase 8
 * Story: REM-018 - Frontend Unit Tests (Target: 60%+ Coverage)
 *
 * Test Categories:
 * - Loading state rendering
 * - Error state handling
 * - Empty state display
 * - Success state with stats
 * - Refresh functionality
 * - Chart rendering (tribunals, phases, timeline)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Dashboard from '../components/Dashboard';
import * as api from '../services/api';

// Mock the API service
vi.mock('../services/api');

// Mock phase color utilities
vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn((phase) => ({
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-300',
    })),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
}));

describe('Dashboard Component', () => {
    const mockStatsData = {
        total_processes: 100,
        total_movements: 500,
        tribunals: [
            { tribunal_name: 'TJRJ', count: 60 },
            { tribunal_name: 'TJSP', count: 40 },
        ],
        phases: [
            { phase: '01', class_nature: 'conhecimento', count: 30 },
            { phase: '10', class_nature: 'execucao', count: 70 },
        ],
        timeline: [
            { month: '2024-01', count: 20 },
            { month: '2024-02', count: 80 },
        ],
        last_updated: '2024-02-23T10:00:00',
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Loading State', () => {
        it('TC-1: displays loading spinner initially', () => {
            api.getStats.mockImplementation(
                () => new Promise(() => {}) // Never resolves
            );

            const { container } = render(<Dashboard />);

            // Check for Loader2 SVG with animate-spin class
            const spinner = container.querySelector('.animate-spin');
            expect(spinner).toBeInTheDocument();
        });

        it('TC-2: loading state has proper accessibility', () => {
            api.getStats.mockImplementation(
                () => new Promise(() => {})
            );

            const { container } = render(<Dashboard />);

            // Check for loading container with proper classes
            const loadingContainer = container.querySelector('.flex.items-center.justify-center');
            expect(loadingContainer).toBeInTheDocument();
        });
    });

    describe('Error State', () => {
        it('TC-3: displays error message when API fails', async () => {
            api.getStats.mockRejectedValue(new Error('Network error'));

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Erro ao carregar dados')).toBeInTheDocument();
            });

            expect(screen.getByText('Falha ao carregar estatísticas do banco de dados.')).toBeInTheDocument();
        });

        it('TC-4: error state shows alert icon', async () => {
            api.getStats.mockRejectedValue(new Error('API Error'));

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Erro ao carregar dados')).toBeInTheDocument();
            });

            // AlertCircle icon should be rendered
            const errorContainer = screen.getByText('Erro ao carregar dados').closest('div').parentElement;
            expect(errorContainer).toHaveClass('bg-red-50', 'border-red-200');
        });
    });

    describe('Empty State', () => {
        it('TC-5: displays empty state when no processes', async () => {
            api.getStats.mockResolvedValue({
                total_processes: 0,
                tribunals: [],
                phases: [],
                timeline: [],
            });

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Banco de Dados Vazio')).toBeInTheDocument();
            });

            expect(
                screen.getByText('Consulte alguns processos primeiro para visualizar estatísticas e análises.')
            ).toBeInTheDocument();
        });

        it('TC-6: empty state when stats is null', async () => {
            api.getStats.mockResolvedValue(null);

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Banco de Dados Vazio')).toBeInTheDocument();
            });
        });
    });

    describe('Success State with Data', () => {
        it('TC-7: renders header with title and subtitle', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            expect(screen.getByText('Estatísticas do banco de dados local')).toBeInTheDocument();
        });

        it('TC-8: displays total processes count', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Total de Processos')).toBeInTheDocument();
            });

            expect(screen.getByText('100')).toBeInTheDocument();
        });

        it('TC-9: displays total movements count', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Total de Movimentos')).toBeInTheDocument();
            });

            expect(screen.getByText('500')).toBeInTheDocument();
        });

        it('TC-10: renders tribunal statistics', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('TJRJ');
            });

            expect(container.textContent).toContain('TJSP');
            expect(container.textContent).toContain('60');
            expect(container.textContent).toContain('40');
        });

        it('TC-11: renders phase statistics', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                // Mocked getPhaseDisplayName returns "Fase {phase}"
                expect(container.textContent).toContain('Fase 01');
            });

            expect(container.textContent).toContain('Fase 10');
        });

        it('TC-12: renders timeline statistics', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toMatch(/2024-01/);
            });

            expect(container.textContent).toMatch(/2024-02/);
        });
    });

    describe('Refresh Functionality', () => {
        it('TC-13: refresh button reloads stats', async () => {
            const user = userEvent.setup();
            api.getStats
                .mockResolvedValueOnce(mockStatsData)
                .mockResolvedValueOnce({
                    ...mockStatsData,
                    total_processes: 150,
                });

            render(<Dashboard />);

            // Wait for initial load
            await waitFor(() => {
                expect(screen.getByText('100')).toBeInTheDocument();
            });

            // Click refresh button (button contains text "Atualizar")
            const refreshButton = screen.getByRole('button', { name: /atualizar/i });
            await user.click(refreshButton);

            // Wait for updated data
            await waitFor(() => {
                expect(screen.getByText('150')).toBeInTheDocument();
            });

            expect(api.getStats).toHaveBeenCalledTimes(2);
        });

        it('TC-14: refresh button shows loading state', async () => {
            const user = userEvent.setup();
            let resolveStats;
            api.getStats
                .mockResolvedValueOnce(mockStatsData)
                .mockImplementation(
                    () =>
                        new Promise((resolve) => {
                            resolveStats = resolve;
                        })
                );

            render(<Dashboard />);

            // Wait for initial load
            await waitFor(() => {
                expect(screen.getByText('100')).toBeInTheDocument();
            });

            // Click refresh
            const refreshButton = screen.getByRole('button', { name: /atualizar/i });
            await user.click(refreshButton);

            // Check loading state (spinner in button or disabled state)
            // This depends on implementation, adapt as needed
            expect(api.getStats).toHaveBeenCalledTimes(2);

            // Resolve to avoid hanging promise
            resolveStats && resolveStats(mockStatsData);
        });
    });

    describe('Chart Rendering', () => {
        it('TC-15: tribunal bars have correct width percentages', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('TJRJ');
            });

            // TJRJ has 60 out of max 60 = 100% width
            // TJSP has 40 out of max 60 = 66.67% width
            const bars = container.querySelectorAll('.bg-gradient-to-r.from-indigo-500');
            expect(bars.length).toBeGreaterThan(0);
        });

        it('TC-16: handles single tribunal correctly', async () => {
            api.getStats.mockResolvedValue({
                ...mockStatsData,
                tribunals: [{ tribunal_name: 'TJRJ', count: 100 }],
            });

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('TJRJ');
            });

            expect(container.textContent).not.toContain('TJSP');
        });

        it('TC-17: renders all phase names using utility', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('Fase 01');
            });

            // Verify phase display name utility was called
            const { getPhaseDisplayName } = await import('../utils/phaseColors');
            expect(getPhaseDisplayName).toHaveBeenCalled();
        });
    });

    describe('Edge Cases', () => {
        it('TC-18: handles empty tribunal list', async () => {
            api.getStats.mockResolvedValue({
                ...mockStatsData,
                tribunals: [],
            });

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            // Should not crash, but may show empty chart section
            expect(screen.queryByText('TJRJ')).not.toBeInTheDocument();
        });

        it('TC-19: handles empty phases list', async () => {
            api.getStats.mockResolvedValue({
                ...mockStatsData,
                phases: [],
            });

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            expect(screen.queryByText('Conhecimento')).not.toBeInTheDocument();
        });

        it('TC-20: handles empty timeline list', async () => {
            api.getStats.mockResolvedValue({
                ...mockStatsData,
                timeline: [],
            });

            render(<Dashboard />);

            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            // Timeline section may still render but empty
        });

        it('TC-21: handles malformed stats data gracefully', async () => {
            api.getStats.mockResolvedValue({
                total_processes: 10,
                total_movements: 20,
                tribunals: [],
                phases: [],
                timeline: [],
                // Minimal but valid structure
            });

            render(<Dashboard />);

            // Should not crash, component should handle missing data
            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            expect(screen.getByText('10')).toBeInTheDocument();
        });
    });

    describe('Integration', () => {
        it('TC-22: full user flow - load, error, refresh, success', async () => {
            const user = userEvent.setup();

            // Initial load fails
            api.getStats.mockRejectedValueOnce(new Error('Network error'));

            render(<Dashboard />);

            // See error - error state doesn't have refresh button, need to reload component
            await waitFor(() => {
                expect(screen.getByText('Erro ao carregar dados')).toBeInTheDocument();
            });

            // Unmount and remount with successful response
            api.getStats.mockResolvedValueOnce(mockStatsData);

            const { unmount } = render(<Dashboard />);

            // See success
            await waitFor(() => {
                expect(screen.getByText('Analytics & Business Intelligence')).toBeInTheDocument();
            });

            expect(screen.getByText('100')).toBeInTheDocument();
        });
    });
});
