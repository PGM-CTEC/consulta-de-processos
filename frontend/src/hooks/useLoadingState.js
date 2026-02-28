import { useState, useCallback, useRef } from 'react';

/**
 * useLoadingState — REM-062
 *
 * Custom hook for consistent loading state management with minimum loading time.
 * Prevents loading spinner flashing by ensuring minimum 300ms display.
 *
 * Usage:
 *   const { isLoading, setLoading } = useLoadingState();
 *
 *   const handleClick = async () => {
 *     setLoading(true);
 *     try {
 *       await apiCall();
 *     } finally {
 *       setLoading(false);
 *     }
 *   };
 *
 * @param {number} minLoadingTime - Minimum time to show loading state (default 300ms)
 * @returns {Object} { isLoading, setLoading }
 */
export function useLoadingState(minLoadingTime = 300) {
  const [isLoading, setIsLoadingState] = useState(false);
  const startTimeRef = useRef(null);

  const setLoading = useCallback((shouldLoad) => {
    if (shouldLoad) {
      startTimeRef.current = Date.now();
      setIsLoadingState(true);
    } else {
      const elapsed = Date.now() - startTimeRef.current;
      const delay = Math.max(0, minLoadingTime - elapsed);

      if (delay > 0) {
        setTimeout(() => setIsLoadingState(false), delay);
      } else {
        setIsLoadingState(false);
      }
    }
  }, [minLoadingTime]);

  return { isLoading, setLoading };
}

export default useLoadingState;
