/**
 * Keyboard Navigation Tests — REM-030
 *
 * Validates keyboard accessibility improvements:
 * - ESC closes export dropdown in BulkSearch
 * - Export button has aria-expanded, aria-haspopup attributes
 * - Dropdown container has role="menu", items have role="menuitem"
 * - All interactive elements are native <button> elements
 * - Tab navigation reaches focusable elements
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BulkSearch from '../components/BulkSearch';
import * as api from '../services/api';

// Mock all required modules exactly as BulkSearch.test.jsx does
vi.mock('../services/api');

vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn(() => 'bg-blue-100 text-blue-800'),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
}));

vi.mock('../utils/exportHelpers', () => ({
    exporters: {
        csv: vi.fn(),
        xlsx: vi.fn(),
        txt: vi.fn(),
        md: vi.fn(),
    },
}));

// Mock xlsx to avoid binary parsing issues
vi.mock('xlsx', () => ({
    read: vi.fn(() => ({ SheetNames: [], Sheets: {} })),
    utils: {
        sheet_to_json: vi.fn(() => []),
        book_new: vi.fn(() => ({})),
        json_to_sheet: vi.fn(() => ({})),
        book_append_sheet: vi.fn(),
    },
    writeFile: vi.fn(),
}));

// Mock FileReader (browser global — required by BulkSearch file upload logic)
window.FileReader = class {
    readAsText(file) {
        this.onload({ target: { result: file.content || '' } });
    }
    readAsBinaryString(file) {
        this.onload({ target: { result: file.content || '' } });
    }
};

// Helper: mock results that expose export button
const MOCK_RESULTS = {
    results: [
        {
            number: '0001234-56.2023.8.26.0001',
            court: 'TJSP - Tribunal de Justica de Sao Paulo',
            tribunal_name: 'TJSP',
            orgao_julgador: '1a Vara Civel',
            fase_atual: 'Conhecimento',
            status: 'success',
        },
    ],
    failures: [],
};

// Helper: render BulkSearch with results visible
async function renderWithResults() {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) });
    api.bulkSubmit.mockResolvedValue({ job_id: 'test-job-123' });
    api.getBulkJob.mockResolvedValue({ status: 'done', ...MOCK_RESULTS });
    render(<BulkSearch />);

    const textarea = screen.getByPlaceholderText(/Um número por linha/i);
    await user.type(textarea, '0001234-56.2023.8.26.0001');

    const searchBtn = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
    await user.click(searchBtn);

    await act(async () => { await vi.advanceTimersByTimeAsync(2100); });

    await waitFor(() => {
        expect(screen.getByText('Resultados da Consulta')).toBeInTheDocument();
    });

    return { user };
}

describe('Keyboard Navigation — REM-030', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    describe('BulkSearch — Initial Render (no results)', () => {
        it('all interactive elements are native <button> elements', () => {
            render(<BulkSearch />);
            const buttons = screen.getAllByRole('button');
            buttons.forEach((btn) => {
                expect(btn.tagName.toLowerCase()).toBe('button');
            });
        });

        it('page has at least one focusable element', () => {
            render(<BulkSearch />);
            const focusable = document.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            expect(focusable.length).toBeGreaterThan(0);
        });

        it('interactive elements are reachable via Tab', async () => {
            const user = userEvent.setup();
            render(<BulkSearch />);
            await user.tab();
            expect(document.activeElement).not.toBe(document.body);
        });
    });

    describe('BulkSearch Export Dropdown — ARIA attributes', () => {
        it('export button has aria-haspopup="menu"', async () => {
            await renderWithResults();
            const exportBtn = screen.getByRole('button', { name: /Exportar Relatório/i });
            expect(exportBtn.getAttribute('aria-haspopup')).toBe('menu');
        });

        it('export button starts with aria-expanded="false"', async () => {
            await renderWithResults();
            const exportBtn = screen.getByRole('button', { name: /Exportar Relatório/i });
            expect(exportBtn.getAttribute('aria-expanded')).toBe('false');
        });

        it('export button aria-expanded becomes "true" when menu opens', async () => {
            const { user } = await renderWithResults();
            const exportBtn = screen.getByRole('button', { name: /Exportar Relatório/i });
            await user.click(exportBtn);
            expect(exportBtn.getAttribute('aria-expanded')).toBe('true');
        });

        it('dropdown container has role="menu" when open', async () => {
            const { user } = await renderWithResults();
            const exportBtn = screen.getByRole('button', { name: /Exportar Relatório/i });
            await user.click(exportBtn);

            const menu = document.querySelector('[role="menu"]');
            expect(menu).not.toBeNull();
        });

        it('dropdown items have role="menuitem"', async () => {
            const { user } = await renderWithResults();
            const exportBtn = screen.getByRole('button', { name: /Exportar Relatório/i });
            await user.click(exportBtn);

            const menuItems = screen.getAllByRole('menuitem');
            expect(menuItems.length).toBeGreaterThan(0);
        });

        it('ESC key closes the export dropdown', async () => {
            const { user } = await renderWithResults();
            const exportBtn = screen.getByRole('button', { name: /Exportar Relatório/i });

            // Open the dropdown
            await user.click(exportBtn);
            expect(exportBtn.getAttribute('aria-expanded')).toBe('true');

            // Press ESC to close
            fireEvent.keyDown(document, { key: 'Escape' });
            expect(exportBtn.getAttribute('aria-expanded')).toBe('false');
        });

        it('export button has aria-label attribute', async () => {
            await renderWithResults();
            const exportBtn = screen.getByRole('button', { name: /Exportar Relatório/i });
            expect(exportBtn.getAttribute('aria-label')).toBeTruthy();
        });
    });
});
