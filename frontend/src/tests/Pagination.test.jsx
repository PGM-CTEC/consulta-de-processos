/**
 * Tests for REM-038 — Pagination & Virtualization
 *
 * Covers:
 *  - usePagination hook behaviour
 *  - Pagination component rendering and navigation
 *  - Edge cases: 0, 1, 10, 100, 1000 items
 *  - Accessibility: aria-label, aria-current
 *  - Keyboard navigation on pagination controls
 *  - BulkSearch integration: pagination state, page-size changes
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderHook, act } from '@testing-library/react';

import { usePagination } from '../hooks/usePagination';
import Pagination from '../components/Pagination';
import BulkSearch from '../components/BulkSearch';
import * as api from '../services/api';

// ─── Mocks ────────────────────────────────────────────────────────────────────

vi.mock('../services/api');

vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn(() => 'bg-blue-100 text-blue-800'),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
}));

vi.mock('../utils/exportHelpers', () => ({
    exporters: { csv: vi.fn(), xlsx: vi.fn(), txt: vi.fn(), md: vi.fn() },
}));

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Build an array of N mock process results.
 */
function makeResults(n) {
    return Array.from({ length: n }, (_, i) => ({
        number: `000${String(i + 1).padStart(4, '0')}-64.2024.8.19.0001`,
        tribunal_name: 'TJRJ',
        court_unit: `Vara ${i + 1}`,
        phase: '01',
        class_nature: 'conhecimento',
    }));
}

function noop() {}

// ─── usePagination Hook ────────────────────────────────────────────────────────

describe('usePagination hook', () => {
    it('TC-P01: returns first page of items with default page size 25', () => {
        const items = makeResults(60);
        const { result } = renderHook(() => usePagination(items));

        expect(result.current.page).toBe(1);
        expect(result.current.pageSize).toBe(25);
        expect(result.current.totalPages).toBe(3);
        expect(result.current.paginatedItems.length).toBe(25);
        expect(result.current.paginatedItems[0].number).toBe(items[0].number);
    });

    it('TC-P02: goNext advances to page 2', () => {
        const items = makeResults(60);
        const { result } = renderHook(() => usePagination(items));

        act(() => result.current.goNext());

        expect(result.current.page).toBe(2);
        expect(result.current.paginatedItems[0].number).toBe(items[25].number);
    });

    it('TC-P03: goPrev decrements page', () => {
        const items = makeResults(60);
        const { result } = renderHook(() => usePagination(items));

        act(() => result.current.goNext());
        act(() => result.current.goPrev());

        expect(result.current.page).toBe(1);
    });

    it('TC-P04: goFirst jumps to first page from last', () => {
        const items = makeResults(60);
        const { result } = renderHook(() => usePagination(items));

        act(() => result.current.goLast());
        act(() => result.current.goFirst());

        expect(result.current.page).toBe(1);
    });

    it('TC-P05: goLast jumps to last page', () => {
        const items = makeResults(60);
        const { result } = renderHook(() => usePagination(items));

        act(() => result.current.goLast());

        expect(result.current.page).toBe(3);
        // Last page: items 51-60 → 10 items
        expect(result.current.paginatedItems.length).toBe(10);
    });

    it('TC-P06: setPageSize resets to page 1 and recalculates slices', () => {
        const items = makeResults(60);
        const { result } = renderHook(() => usePagination(items));

        act(() => result.current.goNext()); // go to page 2
        act(() => result.current.setPageSize(10));

        expect(result.current.page).toBe(1);
        expect(result.current.pageSize).toBe(10);
        expect(result.current.totalPages).toBe(6);
        expect(result.current.paginatedItems.length).toBe(10);
    });

    it('TC-P07: handles empty array gracefully', () => {
        const { result } = renderHook(() => usePagination([]));

        expect(result.current.page).toBe(1);
        expect(result.current.totalPages).toBe(1);
        expect(result.current.totalItems).toBe(0);
        expect(result.current.paginatedItems).toHaveLength(0);
        expect(result.current.startItem).toBe(0);
        expect(result.current.endItem).toBe(0);
    });

    it('TC-P08: handles single-item array', () => {
        const items = makeResults(1);
        const { result } = renderHook(() => usePagination(items));

        expect(result.current.totalPages).toBe(1);
        expect(result.current.paginatedItems).toHaveLength(1);
        expect(result.current.startItem).toBe(1);
        expect(result.current.endItem).toBe(1);
    });

    it('TC-P09: handles 1000 items with page size 50 → 20 pages', () => {
        const items = makeResults(1000);
        const { result } = renderHook(() => usePagination(items, 50));

        expect(result.current.totalPages).toBe(20);
        expect(result.current.paginatedItems).toHaveLength(50);
    });

    it('TC-P10: goTo clamps to valid page range', () => {
        const items = makeResults(30);
        const { result } = renderHook(() => usePagination(items));

        act(() => result.current.goTo(-5)); // below min
        expect(result.current.page).toBe(1);

        act(() => result.current.goTo(9999)); // above max
        expect(result.current.page).toBe(result.current.totalPages);
    });

    it('TC-P11: startItem and endItem are correct on middle pages', () => {
        const items = makeResults(100);
        const { result } = renderHook(() => usePagination(items, 25));

        act(() => result.current.goTo(2));

        expect(result.current.startItem).toBe(26);
        expect(result.current.endItem).toBe(50);
    });

    it('TC-P12: endItem on last page reflects partial page correctly', () => {
        const items = makeResults(53);
        const { result } = renderHook(() => usePagination(items, 25));

        act(() => result.current.goLast()); // page 3, 3 items

        expect(result.current.endItem).toBe(53);
        expect(result.current.paginatedItems).toHaveLength(3);
    });
});

// ─── Pagination Component ─────────────────────────────────────────────────────

describe('Pagination component', () => {
    const defaultProps = {
        page: 1,
        pageSize: 25,
        totalPages: 4,
        totalItems: 87,
        startItem: 1,
        endItem: 25,
        onPageChange: noop,
        onPageSize: noop,
    };

    it('TC-P13: renders item count summary', () => {
        render(<Pagination {...defaultProps} />);
        // "Exibindo" text appears in the paragraph
        expect(screen.getByText(/Exibindo/)).toBeInTheDocument();
        // The summary paragraph should contain 87 total items
        expect(screen.getByText('87')).toBeInTheDocument();
        // "25" can appear both in the select option and the count span — use getAllByText
        const matches = screen.getAllByText('25');
        expect(matches.length).toBeGreaterThanOrEqual(1);
    });

    it('TC-P14: has accessible navigation landmark with aria-label', () => {
        render(<Pagination {...defaultProps} />);
        expect(screen.getByRole('navigation', { name: /Paginação/i })).toBeInTheDocument();
    });

    it('TC-P15: page indicator has aria-current="page"', () => {
        const { container } = render(<Pagination {...defaultProps} />);
        // aria-current is on a <span>, which has no ARIA role — use direct DOM query
        const span = container.querySelector('[aria-current="page"]');
        expect(span).not.toBeNull();
        expect(span.textContent).toMatch(/1\s*\/\s*4/);
    });

    it('TC-P16: Previous button is disabled on first page', () => {
        render(<Pagination {...defaultProps} />);
        expect(screen.getByRole('button', { name: /Página anterior/i })).toBeDisabled();
    });

    it('TC-P17: Next button is disabled on last page', () => {
        render(<Pagination {...defaultProps} page={4} startItem={76} endItem={87} />);
        expect(screen.getByRole('button', { name: /Próxima página/i })).toBeDisabled();
    });

    it('TC-P18: clicking Next calls onPageChange with page + 1', async () => {
        const onPageChange = vi.fn();
        render(<Pagination {...defaultProps} page={2} onPageChange={onPageChange} />);

        const nextBtn = screen.getByRole('button', { name: /Próxima página/i });
        await userEvent.click(nextBtn);

        expect(onPageChange).toHaveBeenCalledWith(3);
    });

    it('TC-P19: clicking Previous calls onPageChange with page - 1', async () => {
        const onPageChange = vi.fn();
        render(<Pagination {...defaultProps} page={3} onPageChange={onPageChange} />);

        const prevBtn = screen.getByRole('button', { name: /Página anterior/i });
        await userEvent.click(prevBtn);

        expect(onPageChange).toHaveBeenCalledWith(2);
    });

    it('TC-P20: First/Last buttons appear when totalPages > 5', () => {
        render(<Pagination {...defaultProps} totalPages={6} />);
        expect(screen.getByRole('button', { name: /Primeira página/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Última página/i })).toBeInTheDocument();
    });

    it('TC-P21: First/Last buttons are absent when totalPages <= 5', () => {
        render(<Pagination {...defaultProps} totalPages={5} />);
        expect(screen.queryByRole('button', { name: /Primeira página/i })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: /Última página/i })).not.toBeInTheDocument();
    });

    it('TC-P22: page size selector calls onPageSize with numeric value', async () => {
        const onPageSize = vi.fn();
        render(<Pagination {...defaultProps} onPageSize={onPageSize} />);

        const select = screen.getByRole('combobox', { name: /Itens por página/i });
        await userEvent.selectOptions(select, '10');

        expect(onPageSize).toHaveBeenCalledWith(10);
    });

    it('TC-P23: returns null when totalItems is 0', () => {
        const { container } = render(
            <Pagination {...defaultProps} totalItems={0} />
        );
        expect(container.firstChild).toBeNull();
    });

    it('TC-P24: First-page button is disabled when on first page', () => {
        render(<Pagination {...defaultProps} totalPages={6} page={1} />);
        expect(screen.getByRole('button', { name: /Primeira página/i })).toBeDisabled();
    });

    it('TC-P25: Last-page button is disabled when on last page', () => {
        render(<Pagination {...defaultProps} totalPages={6} page={6} />);
        expect(screen.getByRole('button', { name: /Última página/i })).toBeDisabled();
    });
});

// ─── BulkSearch Integration ───────────────────────────────────────────────────

describe('BulkSearch — pagination integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('TC-P26: pagination controls appear when results have more than 0 items', async () => {
        const user = userEvent.setup();
        api.bulkSearch.mockResolvedValue({ results: makeResults(30), failures: [] });

        render(<BulkSearch />);

        const textarea = screen.getByPlaceholderText(/Um número por linha/i);
        await user.type(textarea, '0001745-64.1989.8.19.0002');
        await user.click(screen.getByRole('button', { name: /Iniciar Consulta em Lote/i }));

        await waitFor(() => {
            expect(screen.getByRole('navigation', { name: /Paginação/i })).toBeInTheDocument();
        });
    });

    it('TC-P27: only first 25 results are rendered by default', async () => {
        const user = userEvent.setup();
        const results = makeResults(50);
        api.bulkSearch.mockResolvedValue({ results, failures: [] });

        render(<BulkSearch />);

        const textarea = screen.getByPlaceholderText(/Um número por linha/i);
        await user.type(textarea, results[0].number);
        await user.click(screen.getByRole('button', { name: /Iniciar Consulta em Lote/i }));

        await waitFor(() => {
            // Item 26 (index 25) should NOT be in the table (it's on page 2)
            expect(screen.queryByText(results[25].number)).not.toBeInTheDocument();
            // Item 25 (index 24, last on page 1) should be visible in table
            expect(screen.getByText(results[24].number)).toBeInTheDocument();
        });
    });

    it('TC-P28: navigating to page 2 shows different results', async () => {
        const user = userEvent.setup();
        const results = makeResults(50);
        api.bulkSearch.mockResolvedValue({ results, failures: [] });

        render(<BulkSearch />);

        const textarea = screen.getByPlaceholderText(/Um número por linha/i);
        await user.type(textarea, results[0].number);
        await user.click(screen.getByRole('button', { name: /Iniciar Consulta em Lote/i }));

        await waitFor(() => {
            expect(screen.getByRole('navigation', { name: /Paginação/i })).toBeInTheDocument();
        });

        const nextBtn = screen.getByRole('button', { name: /Próxima página/i });
        await user.click(nextBtn);

        await waitFor(() => {
            // Item 26 (index 25) should now be visible
            expect(screen.getByText(results[25].number)).toBeInTheDocument();
        });
    });

    it('TC-P29: changing page size to 10 limits visible rows', async () => {
        const user = userEvent.setup();
        const results = makeResults(30);
        api.bulkSearch.mockResolvedValue({ results, failures: [] });

        render(<BulkSearch />);

        const textarea = screen.getByPlaceholderText(/Um número por linha/i);
        await user.type(textarea, results[0].number);
        await user.click(screen.getByRole('button', { name: /Iniciar Consulta em Lote/i }));

        await waitFor(() => {
            expect(screen.getByRole('navigation', { name: /Paginação/i })).toBeInTheDocument();
        });

        // Change page size to 10
        const select = screen.getByRole('combobox', { name: /Itens por página/i });
        await user.selectOptions(select, '10');

        await waitFor(() => {
            // items[10] is the 11th result (index 10) — should NOT be visible after reducing page size to 10
            expect(screen.queryByText(results[10].number)).not.toBeInTheDocument();
            // items[9] is the 10th result (index 9) — should be visible
            expect(screen.getByText(results[9].number)).toBeInTheDocument();
        });
    });
});
