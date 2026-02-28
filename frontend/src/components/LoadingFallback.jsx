/**
 * LoadingFallback — REM-037
 * Accessible Suspense fallback component for lazy-loaded routes/tabs.
 *
 * Used as the fallback prop in <Suspense> boundaries wrapping
 * React.lazy() components. Meets WCAG AA requirements:
 * - role="status" (live region, polite)
 * - aria-label describing the loading state
 * - Visible spinner animation
 */

function LoadingFallback({ message = 'Carregando...' }) {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen"
      role="status"
      aria-label={message}
      aria-live="polite"
    >
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" aria-hidden="true" />
      <span className="sr-only">{message}</span>
    </div>
  );
}

export default LoadingFallback;
