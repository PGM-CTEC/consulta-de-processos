import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { Button } from './ui/button';

const PAGE_SIZE_OPTIONS = [10, 25, 50];

/**
 * Pagination — accessible pagination UI component.
 *
 * Props:
 *  page         {number}   - Current page (1-based)
 *  pageSize     {number}   - Items per page
 *  totalPages   {number}   - Total number of pages
 *  totalItems   {number}   - Total number of items
 *  startItem    {number}   - Index of first visible item (1-based)
 *  endItem      {number}   - Index of last visible item (1-based)
 *  onPageChange {function} - Called with (newPage)
 *  onPageSize   {function} - Called with (newPageSize)
 */
const Pagination = ({
    page,
    pageSize,
    totalPages,
    totalItems,
    startItem,
    endItem,
    onPageChange,
    onPageSize,
}) => {
    if (totalItems === 0) return null;

    const showFirstLast = totalPages > 5;

    return (
        <nav
            aria-label="Paginação"
            className="flex flex-col sm:flex-row items-center justify-between gap-3 px-4 py-3 border-t border-gray-100 bg-gray-50/50"
        >
            {/* Item count info */}
            <p className="text-sm text-gray-600 whitespace-nowrap">
                Exibindo{' '}
                <span className="font-semibold text-gray-900">{startItem}</span>
                {' '}–{' '}
                <span className="font-semibold text-gray-900">{endItem}</span>
                {' '}de{' '}
                <span className="font-semibold text-gray-900">{totalItems}</span>
                {' '}resultados
            </p>

            <div className="flex items-center gap-3">
                {/* Page size selector */}
                <div className="flex items-center gap-2">
                    <label
                        htmlFor="page-size-select"
                        className="text-sm text-gray-600 whitespace-nowrap"
                    >
                        Por página:
                    </label>
                    <select
                        id="page-size-select"
                        value={pageSize}
                        onChange={(e) => onPageSize(Number(e.target.value))}
                        className="text-sm border border-gray-200 rounded-md px-2 py-1 bg-white focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                        aria-label="Itens por página"
                    >
                        {PAGE_SIZE_OPTIONS.map((size) => (
                            <option key={size} value={size}>
                                {size}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Navigation buttons */}
                <ol className="flex items-center gap-1 list-none m-0 p-0" role="list">
                    {showFirstLast && (
                        <li>
                            <Button
                                variant="ghost"
                                onClick={() => onPageChange(1)}
                                disabled={page === 1}
                                aria-label="Primeira página"
                                className="h-8 w-8 p-0"
                            >
                                <ChevronsLeft className="h-4 w-4" />
                            </Button>
                        </li>
                    )}

                    <li>
                        <Button
                            variant="ghost"
                            onClick={() => onPageChange(page - 1)}
                            disabled={page === 1}
                            aria-label="Página anterior"
                            className="h-8 w-8 p-0"
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </Button>
                    </li>

                    <li>
                        <span
                            aria-current="page"
                            aria-label={`Página ${page} de ${totalPages}`}
                            className="text-sm font-semibold text-gray-700 px-3 py-1 rounded-md bg-white border border-gray-200 whitespace-nowrap"
                        >
                            {page} / {totalPages}
                        </span>
                    </li>

                    <li>
                        <Button
                            variant="ghost"
                            onClick={() => onPageChange(page + 1)}
                            disabled={page === totalPages}
                            aria-label="Próxima página"
                            className="h-8 w-8 p-0"
                        >
                            <ChevronRight className="h-4 w-4" />
                        </Button>
                    </li>

                    {showFirstLast && (
                        <li>
                            <Button
                                variant="ghost"
                                onClick={() => onPageChange(totalPages)}
                                disabled={page === totalPages}
                                aria-label="Última página"
                                className="h-8 w-8 p-0"
                            >
                                <ChevronsRight className="h-4 w-4" />
                            </Button>
                        </li>
                    )}
                </ol>
            </div>
        </nav>
    );
};

export default Pagination;
