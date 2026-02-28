import { useState, useMemo, useCallback } from 'react';

/**
 * usePagination — manages pagination state for a list of items.
 *
 * @param {Array}  items           - Full array of items to paginate
 * @param {number} defaultPageSize - Initial page size (default 25)
 * @returns {{ page, pageSize, setPageSize, totalPages, paginatedItems, goTo, goNext, goPrev, goFirst, goLast, totalItems }}
 */
export function usePagination(items = [], defaultPageSize = 25) {
    const [page, setPage] = useState(1);
    const [pageSize, setPageSizeState] = useState(defaultPageSize);

    const totalItems = items.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));

    const paginatedItems = useMemo(() => {
        const start = (page - 1) * pageSize;
        return items.slice(start, start + pageSize);
    }, [items, page, pageSize]);

    const goTo = useCallback(
        (p) => setPage(Math.max(1, Math.min(p, totalPages))),
        [totalPages]
    );

    const goNext = useCallback(() => goTo(page + 1), [goTo, page]);
    const goPrev = useCallback(() => goTo(page - 1), [goTo, page]);
    const goFirst = useCallback(() => goTo(1), [goTo]);
    const goLast = useCallback(() => goTo(totalPages), [goTo, totalPages]);

    const setPageSize = useCallback(
        (size) => {
            const s = Number(size);
            setPageSizeState(s);
            // Keep the user roughly on the same position
            setPage(1);
        },
        []
    );

    const startItem = totalItems === 0 ? 0 : (page - 1) * pageSize + 1;
    const endItem = Math.min(page * pageSize, totalItems);

    return {
        page,
        pageSize,
        setPageSize,
        totalPages,
        totalItems,
        paginatedItems,
        goTo,
        goNext,
        goPrev,
        goFirst,
        goLast,
        startItem,
        endItem,
    };
}
