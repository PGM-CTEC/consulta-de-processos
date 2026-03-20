/**
 * Unified loading state components — REM-024
 * Variantes: spinner (padrão), skeleton, text
 */

export const SkeletonCard = () => (
  <div className="animate-pulse bg-white rounded-lg p-6 shadow">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
  </div>
)

export const SkeletonTable = ({ rows = 5 }) => (
  <div className="space-y-2">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="animate-pulse flex space-x-4">
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/3"></div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/6"></div>
      </div>
    ))}
  </div>
)

export const ErrorState = ({ message, onRetry }) => (
  <div className="flex flex-col items-center justify-center p-8 text-center">
    <div className="text-red-500 text-xl mb-2">&#9888;&#65039;</div>
    <p className="text-gray-700 mb-4">{message}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
      >
        Tentar novamente
      </button>
    )}
  </div>
)

export const LoadingState = ({ variant = 'spinner', message }) => {
  if (variant === 'skeleton') {
    return <SkeletonCard />
  }

  if (variant === 'text') {
    return (
      <div className="text-center p-8 text-gray-600">
        {message || 'Carregando...'}
      </div>
    )
  }

  // Default: spinner
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
      {message && <p className="ml-4 text-gray-600">{message}</p>}
    </div>
  )
}

export default LoadingState
