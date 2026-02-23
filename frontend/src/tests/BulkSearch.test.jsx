/**
 * Tests for BulkSearch Component - Frontend Testing Phase 8
 * Story: REM-018 - Frontend Unit Tests (Target: 60%+ Coverage)
 *
 * Test Categories:
 * - Initial rendering
 * - Number input handling
 * - Search functionality
 * - File upload (TXT, CSV, XLSX)
 * - Drag & Drop
 * - Results display
 * - Export functionality
 * - Loading and error states
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BulkSearch from '../components/BulkSearch';
import * as api from '../services/api';
import * as exportHelpers from '../utils/exportHelpers';

// Mock the API module
vi.mock('../services/api');

// Mock the phase utils
vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn(() => 'bg-blue-100 text-blue-800'),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
}));

// Mock the export helpers
vi.mock('../utils/exportHelpers', () => ({
    exporters: {
        csv: vi.fn(),
        xlsx: vi.fn(),
        txt: vi.fn(),
        md: vi.fn(),
    },
}));

// Mock FileReader
global.FileReader = class {
    readAsText(file) {
        this.onload({ target: { result: file.content } });
    }
    readAsBinaryString(file) {
        this.onload({ target: { result: file.content } });
    }
};

describe('BulkSearch Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Initial Rendering', () => {
        it('TC-1: renders main title', () => {
            render(<BulkSearch />);

            expect(screen.getByText(/Busca em Lote/i)).toBeInTheDocument();
        });

        it('TC-2: renders drag and drop zone', () => {
            render(<BulkSearch />);

            expect(
                screen.getByText(/Clique ou arraste um arquivo para importar/i)
            ).toBeInTheDocument();
        });

        it('TC-3: renders textarea for number input', () => {
            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            expect(textarea).toBeInTheDocument();
        });

        it('TC-4: renders search button', () => {
            render(<BulkSearch />);

            expect(screen.getByRole('button', { name: /Iniciar Consulta em Lote/i })).toBeInTheDocument();
        });

        it('TC-5: search button is disabled initially', () => {
            render(<BulkSearch />);

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            expect(searchButton).toBeDisabled();
        });
    });

    describe('Number Input Handling', () => {
        it('TC-6: updates textarea value on input', async () => {
            const user = userEvent.setup();
            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            expect(textarea).toHaveValue('0001745-64.1989.8.19.0002');
        });

        it('TC-7: enables search button when numbers are entered', async () => {
            const user = userEvent.setup();
            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });

            await user.type(textarea, '0001745-64.1989.8.19.0002');

            expect(searchButton).toBeEnabled();
        });

        it('TC-8: handles multiple numbers input', async () => {
            const user = userEvent.setup();
            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(
                textarea,
                '0001745-64.1989.8.19.0002\n0002345-12.2020.8.19.0001'
            );

            expect(textarea.value.split('\n')).toHaveLength(2);
        });
    });

    describe('Search Functionality', () => {
        it('TC-9: calls bulkSearch API on button click', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue({ results: [], failures: [] });

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(api.bulkSearch).toHaveBeenCalledWith(['0001745-64.1989.8.19.0002']);
            });
        });

        it('TC-10: shows loading state during search', async () => {
            const user = userEvent.setup();
            let resolveSearch;
            api.bulkSearch.mockImplementation(
                () =>
                    new Promise((resolve) => {
                        resolveSearch = resolve;
                    })
            );

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText(/Processando Lote/i)).toBeInTheDocument();
            });

            resolveSearch && resolveSearch({ results: [], failures: [] });
        });

        it('TC-11: displays results after successful search', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue({
                results: [
                    {
                        number: '0001745-64.1989.8.19.0002',
                        tribunal_name: 'TJRJ',
                        court_unit: 'Vara 1',
                        phase: '01',
                        class_nature: 'conhecimento',
                    },
                ],
                failures: [],
            });

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText('Resultados da Consulta')).toBeInTheDocument();
            });

            // Number might appear multiple times in the table
            const processNumbers = screen.getAllByText('0001745-64.1989.8.19.0002');
            expect(processNumbers.length).toBeGreaterThan(0);
        });

        it('TC-12: displays error message on search failure', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockRejectedValue(new Error('API Error'));

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText(/Falha ao processar a busca em lote/i)).toBeInTheDocument();
            });
        });

        it('TC-13: filters empty lines from input', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue({ results: [], failures: [] });

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002\n\n0002345-12.2020.8.19.0001');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(api.bulkSearch).toHaveBeenCalledWith([
                    '0001745-64.1989.8.19.0002',
                    '0002345-12.2020.8.19.0001',
                ]);
            });
        });
    });

    describe('Results Display', () => {
        const mockResults = {
            results: [
                {
                    number: '0001745-64.1989.8.19.0002',
                    tribunal_name: 'TJRJ',
                    court_unit: 'Vara 1',
                    phase: '01',
                    class_nature: 'conhecimento',
                },
                {
                    number: '0002345-12.2020.8.19.0001',
                    tribunal_name: 'TJRJ',
                    court_unit: 'Vara 2',
                    phase: '10',
                    class_nature: 'execucao',
                },
            ],
            failures: ['0003456-78.2021.8.19.0003'],
        };

        it('TC-14: displays results table with correct counts', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue(mockResults);

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText(/2 processados/i)).toBeInTheDocument();
            });

            expect(screen.getByText(/1 falhas/i)).toBeInTheDocument();
        });

        it('TC-15: displays tribunal names in results', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue(mockResults);

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                const tjrjElements = screen.getAllByText('TJRJ');
                expect(tjrjElements.length).toBeGreaterThan(0);
            });
        });

        it('TC-16: displays failure rows in red', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue(mockResults);

            const { container } = render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText('0003456-78.2021.8.19.0003')).toBeInTheDocument();
            });

            const failureRow = container.querySelector('.bg-red-50\\/20');
            expect(failureRow).toBeInTheDocument();
        });
    });

    describe('Export Functionality', () => {
        const mockResults = {
            results: [
                {
                    number: '0001745-64.1989.8.19.0002',
                    tribunal_name: 'TJRJ',
                },
            ],
            failures: [],
        };

        it('TC-17: shows export menu on button click', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue(mockResults);

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText('Resultados da Consulta')).toBeInTheDocument();
            });

            const exportButton = screen.getByRole('button', { name: /Exportar Relatório/i });
            await user.click(exportButton);

            await waitFor(() => {
                expect(screen.getByText(/Excel \/ CSV \(\.csv\)/i)).toBeInTheDocument();
            });
        });

        it('TC-18: calls CSV export function', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue(mockResults);

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText('Resultados da Consulta')).toBeInTheDocument();
            });

            const exportButton = screen.getByRole('button', { name: /Exportar Relatório/i });
            await user.click(exportButton);

            await waitFor(() => {
                expect(screen.getByText(/Excel \/ CSV/i)).toBeInTheDocument();
            });

            const csvButton = screen.getByText(/Excel \/ CSV/i);
            await user.click(csvButton);

            expect(exportHelpers.exporters.csv).toHaveBeenCalledWith(mockResults.results);
        });

        it('TC-19: closes export menu after selection', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue(mockResults);

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText('Resultados da Consulta')).toBeInTheDocument();
            });

            const exportButton = screen.getByRole('button', { name: /Exportar Relatório/i });
            await user.click(exportButton);

            await waitFor(() => {
                expect(screen.getByText(/Excel \/ CSV/i)).toBeInTheDocument();
            });

            const csvButton = screen.getByText(/Excel \/ CSV/i);
            await user.click(csvButton);

            await waitFor(() => {
                expect(screen.queryByText(/Planilha Excel/i)).not.toBeInTheDocument();
            });
        });
    });

    describe('Drag and Drop', () => {
        it('TC-20: changes style on drag over', async () => {
            const { container } = render(<BulkSearch />);

            const dropZone = container.querySelector('.border-dashed');

            const event = new Event('dragover', { bubbles: true });
            event.preventDefault = vi.fn();
            dropZone.dispatchEvent(event);

            await waitFor(() => {
                expect(dropZone).toHaveClass('border-violet-500');
            });
        });

        it('TC-21: resets style on drag leave', async () => {
            const { container } = render(<BulkSearch />);

            const dropZone = container.querySelector('.border-dashed');

            // First trigger dragover
            const dragOverEvent = new Event('dragover', { bubbles: true });
            dragOverEvent.preventDefault = vi.fn();
            dropZone.dispatchEvent(dragOverEvent);

            // Then trigger dragleave
            const dragLeaveEvent = new Event('dragleave', { bubbles: true });
            dropZone.dispatchEvent(dragLeaveEvent);

            await waitFor(() => {
                expect(dropZone).toHaveClass('border-gray-200');
            });
        });
    });

    describe('Button States', () => {
        it('TC-22: disables button during search', async () => {
            const user = userEvent.setup();
            let resolveSearch;
            api.bulkSearch.mockImplementation(
                () =>
                    new Promise((resolve) => {
                        resolveSearch = resolve;
                    })
            );

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(searchButton).toBeDisabled();
            });

            resolveSearch && resolveSearch({ results: [], failures: [] });
        });

        it('TC-23: button remains disabled with only whitespace', async () => {
            const user = userEvent.setup();
            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '   \n   ');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            expect(searchButton).toBeDisabled();
        });
    });

    describe('Edge Cases', () => {
        it('TC-24: handles empty results gracefully', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue({ results: [], failures: [] });

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText(/0 processados/i)).toBeInTheDocument();
            });
        });

        it('TC-25: handles all failures result', async () => {
            const user = userEvent.setup();
            api.bulkSearch.mockResolvedValue({
                results: [],
                failures: ['0001745-64.1989.8.19.0002', '0002345-12.2020.8.19.0001'],
            });

            render(<BulkSearch />);

            const textarea = screen.getByPlaceholderText(/Um número por linha/i);
            await user.type(textarea, '0001745-64.1989.8.19.0002\n0002345-12.2020.8.19.0001');

            const searchButton = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
            await user.click(searchButton);

            await waitFor(() => {
                expect(screen.getByText(/2 falhas/i)).toBeInTheDocument();
            });
        });
    });
});
