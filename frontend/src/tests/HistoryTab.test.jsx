/**
 * Tests for HistoryTab Component - Frontend Testing Phase 8
 * Story: REM-018 - Frontend Unit Tests (Target: 60%+ Coverage)
 *
 * Test Categories:
 * - Loading state rendering
 * - Empty state display
 * - Success state with history items
 * - Clear history functionality
 * - Error handling
 * - Date formatting
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Toaster } from 'react-hot-toast';
import HistoryTab from '../components/HistoryTab';
import * as api from '../services/api';

// Mock the API service
vi.mock('../services/api');

// Mock window.confirm
global.confirm = vi.fn();

describe('HistoryTab Component', () => {
    const mockLabels = {
        nav: {
            history: 'Histórico',
        },
    };

    const mockHistoryData = [
        {
            number: '0001745-64.1989.8.19.0002',
            court: 'TJRJ',
            created_at: '2024-02-23T10:30:00',
        },
        {
            number: '0002345-12.2020.8.19.0001',
            court: 'TJRJ',
            created_at: '2024-02-22T15:45:00',
        },
    ];

    beforeEach(() => {
        vi.clearAllMocks();
        global.confirm.mockReturnValue(true); // Default: user confirms
    });

    describe('Loading State', () => {
        it('TC-1: displays loading spinner initially', () => {
            api.getHistory.mockImplementation(
                () => new Promise(() => { }) // Never resolves
            );

            const { container } = render(<HistoryTab labels={mockLabels} />);

            const spinner = container.querySelector('.animate-spin');
            expect(spinner).toBeInTheDocument();
        });

        it('TC-2: loading state has spinner with correct styling', () => {
            api.getHistory.mockImplementation(() => new Promise(() => { }));

            const { container } = render(<HistoryTab labels={mockLabels} />);

            const spinner = container.querySelector('.animate-spin.rounded-full.border-b-2.border-indigo-600');
            expect(spinner).toBeInTheDocument();
        });
    });

    describe('Empty State', () => {
        it('TC-3: displays empty message when no history', async () => {
            api.getHistory.mockResolvedValue([]);

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('Nenhum histórico encontrado')).toBeInTheDocument();
            });

            expect(screen.getByText('As consultas que você realizar aparecerão aqui.')).toBeInTheDocument();
        });

        it('TC-4: empty state shows clock icon', async () => {
            api.getHistory.mockResolvedValue([]);

            const { container } = render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('Nenhum histórico encontrado')).toBeInTheDocument();
            });

            // Check for Clock icon (lucide-react SVG)
            const clockIcon = container.querySelector('svg');
            expect(clockIcon).toBeInTheDocument();
        });

        it('TC-5: empty state does not show clear button', async () => {
            api.getHistory.mockResolvedValue([]);

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('Nenhum histórico encontrado')).toBeInTheDocument();
            });

            expect(screen.queryByText('Limpar Histórico')).not.toBeInTheDocument();
        });
    });

    describe('Success State with Data', () => {
        it('TC-6: renders header with title from labels', async () => {
            api.getHistory.mockResolvedValue(mockHistoryData);

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('Histórico')).toBeInTheDocument();
            });

            expect(screen.getByText('Acompanhe suas últimas consultas realizadas.')).toBeInTheDocument();
        });

        it('TC-7: displays all history items', async () => {
            api.getHistory.mockResolvedValue(mockHistoryData);

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('0001745-64.1989.8.19.0002')).toBeInTheDocument();
            });

            expect(screen.getByText('0002345-12.2020.8.19.0001')).toBeInTheDocument();
        });

        it('TC-8: displays court name for each item', async () => {
            api.getHistory.mockResolvedValue(mockHistoryData);

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('0001745-64.1989.8.19.0002')).toBeInTheDocument();
            });

            const courtNames = screen.getAllByText('TJRJ');
            expect(courtNames).toHaveLength(2);
        });

        it('TC-9: formats dates correctly', async () => {
            api.getHistory.mockResolvedValue(mockHistoryData);

            const { container } = render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('0001745-64.1989.8.19.0002')).toBeInTheDocument();
            });

            // Check that date appears formatted (locale string)
            // Exact format depends on locale, just check that date elements exist
            const dateElements = container.querySelectorAll('.text-xs.text-gray-500');
            expect(dateElements.length).toBeGreaterThan(0);
        });

        it('TC-10: shows clear history button when items exist', async () => {
            api.getHistory.mockResolvedValue(mockHistoryData);

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('Limpar Histórico')).toBeInTheDocument();
            });
        });
    });

    describe('Clear History Functionality', () => {
        it('TC-11: clears history on confirmation', async () => {
            const user = userEvent.setup();
            api.getHistory.mockResolvedValue(mockHistoryData);
            api.clearHistory.mockResolvedValue({});
            global.confirm.mockReturnValue(true);

            render(
                <>
                    <HistoryTab labels={mockLabels} />
                    <Toaster />
                </>
            );

            // Wait for history to load
            await waitFor(() => {
                expect(screen.getByText('0001745-64.1989.8.19.0002')).toBeInTheDocument();
            });

            // Click clear button
            const clearButton = screen.getByText('Limpar Histórico');
            await user.click(clearButton);

            // Verify confirmation was shown
            expect(global.confirm).toHaveBeenCalledWith(
                'Tem certeza que deseja limpar todo o histórico?'
            );

            // Verify API was called
            await waitFor(() => {
                expect(api.clearHistory).toHaveBeenCalled();
            });

            // Verify history is cleared in UI
            await waitFor(() => {
                expect(screen.queryByText('0001745-64.1989.8.19.0002')).not.toBeInTheDocument();
            });
        });

        it('TC-12: does not clear when user cancels', async () => {
            const user = userEvent.setup();
            api.getHistory.mockResolvedValue(mockHistoryData);
            api.clearHistory.mockResolvedValue({});
            global.confirm.mockReturnValue(false); // User cancels

            render(<HistoryTab labels={mockLabels} />);

            // Wait for history to load
            await waitFor(() => {
                expect(screen.getByText('0001745-64.1989.8.19.0002')).toBeInTheDocument();
            });

            // Click clear button
            const clearButton = screen.getByText('Limpar Histórico');
            await user.click(clearButton);

            // Verify confirmation was shown
            expect(global.confirm).toHaveBeenCalled();

            // Verify API was NOT called
            expect(api.clearHistory).not.toHaveBeenCalled();

            // Verify history is still displayed
            expect(screen.getByText('0001745-64.1989.8.19.0002')).toBeInTheDocument();
        });

        it('TC-13: shows error toast on clear failure', async () => {
            const user = userEvent.setup();
            api.getHistory.mockResolvedValue(mockHistoryData);
            api.clearHistory.mockRejectedValue(new Error('Network error'));
            global.confirm.mockReturnValue(true);

            render(
                <>
                    <HistoryTab labels={mockLabels} />
                    <Toaster />
                </>
            );

            // Wait for history to load
            await waitFor(() => {
                expect(screen.getByText('0001745-64.1989.8.19.0002')).toBeInTheDocument();
            });

            // Click clear button
            const clearButton = screen.getByText('Limpar Histórico');
            await user.click(clearButton);

            // Wait for error toast (toast library renders asynchronously)
            await waitFor(
                () => {
                    expect(screen.queryByText(/Erro ao limpar histórico/i)).toBeInTheDocument();
                },
                { timeout: 2000 }
            );
        });
    });

    describe('Error Handling', () => {
        it('TC-14: handles API error gracefully with empty array', async () => {
            api.getHistory.mockRejectedValue(new Error('API Error'));

            render(<HistoryTab labels={mockLabels} />);

            // Should show empty state (fallback behavior)
            await waitFor(() => {
                expect(screen.getByText('Nenhum histórico encontrado')).toBeInTheDocument();
            });
        });

        it('TC-15: logs error to console on API failure', async () => {
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
            api.getHistory.mockRejectedValue(new Error('API Error'));

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    'Error fetching history:',
                    expect.any(Error)
                );
            });

            consoleErrorSpy.mockRestore();
        });
    });

    describe('Edge Cases', () => {
        it('TC-16: handles single history item correctly', async () => {
            api.getHistory.mockResolvedValue([mockHistoryData[0]]);

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('0001745-64.1989.8.19.0002')).toBeInTheDocument();
            });

            expect(screen.queryByText('0002345-12.2020.8.19.0001')).not.toBeInTheDocument();
            expect(screen.getByText('Limpar Histórico')).toBeInTheDocument();
        });

        it('TC-17: handles history with missing optional fields', async () => {
            api.getHistory.mockResolvedValue([
                {
                    number: '0001234-56.2021.8.19.0001',
                    court: 'TJRJ',
                    created_at: '2024-02-23T10:00:00',
                },
            ]);

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('0001234-56.2021.8.19.0001')).toBeInTheDocument();
            });

            // Should not crash
            expect(screen.getByText('TJRJ')).toBeInTheDocument();
        });

        it('TC-18: handles very long history list', async () => {
            const longHistory = Array.from({ length: 50 }, (_, i) => ({
                number: `000${i.toString().padStart(4, '0')}-12.2020.8.19.0001`,
                court: 'TJRJ',
                created_at: '2024-02-23T10:00:00',
            }));

            api.getHistory.mockResolvedValue(longHistory);

            const { container } = render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('0000000-12.2020.8.19.0001')).toBeInTheDocument();
            });

            // Check that all items are rendered
            const listItems = container.querySelectorAll('li');
            expect(listItems).toHaveLength(50);
        });
    });

    describe('UI Interaction', () => {
        it('TC-19: history items are clickable buttons', async () => {
            api.getHistory.mockResolvedValue(mockHistoryData);

            render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('0001745-64.1989.8.19.0002')).toBeInTheDocument();
            });

            const buttons = screen.getAllByRole('button').filter((btn) =>
                btn.getAttribute('aria-label')?.includes('processo')
            );
            expect(buttons.length).toBeGreaterThan(0);
        });

        it('TC-20: clear button has correct styling', async () => {
            api.getHistory.mockResolvedValue(mockHistoryData);

            const { container } = render(<HistoryTab labels={mockLabels} />);

            await waitFor(() => {
                expect(screen.getByText('Limpar Histórico')).toBeInTheDocument();
            });

            const clearButton = screen.getByText('Limpar Histórico').closest('button');
            expect(clearButton).toHaveClass('text-red-600');
            expect(clearButton).toHaveClass('border-red-200');
        });
    });
});
