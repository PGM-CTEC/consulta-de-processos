import React from 'react';

/**
 * Error Boundary Component
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing the whole app.
 *
 * Note: Error boundaries do NOT catch errors for:
 * - Event handlers (use try-catch instead)
 * - Asynchronous code (e.g., setTimeout or requestAnimationFrame callbacks)
 * - Server side rendering
 * - Errors thrown in the error boundary itself
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // You can also log to an error reporting service here
    // Example: logErrorToService(error, errorInfo);

    this.setState({
      error,
      errorInfo
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // Fallback UI
      const isDevelopment = import.meta.env.DEV;

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
            <div className="text-center mb-6">
              <div className="text-6xl mb-4">⚠️</div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Algo deu errado
              </h1>
              <p className="text-gray-600">
                Ocorreu um erro inesperado na aplicação. Por favor, tente novamente.
              </p>
            </div>

            {/* Error details - only show in development */}
            {isDevelopment && this.state.error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <h2 className="text-lg font-semibold text-red-900 mb-2">
                  Detalhes do Erro (apenas em desenvolvimento):
                </h2>
                <div className="text-sm font-mono text-red-800 mb-2 overflow-auto">
                  <strong>Mensagem:</strong> {this.state.error.toString()}
                </div>
                {this.state.errorInfo && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-red-700 hover:text-red-900">
                      Stack Trace
                    </summary>
                    <pre className="mt-2 text-xs bg-red-100 p-2 rounded overflow-auto max-h-64">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            )}

            {/* Action buttons */}
            <div className="flex gap-4 justify-center">
              <button
                onClick={this.handleReset}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700
                         transition-colors font-medium focus:outline-none focus:ring-2
                         focus:ring-blue-500 focus:ring-offset-2"
                aria-label="Tentar novamente"
              >
                Tentar Novamente
              </button>
              <button
                onClick={this.handleGoHome}
                className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700
                         transition-colors font-medium focus:outline-none focus:ring-2
                         focus:ring-gray-500 focus:ring-offset-2"
                aria-label="Ir para página inicial"
              >
                Ir para Início
              </button>
            </div>

            {/* Additional help */}
            <div className="mt-6 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
              Se o problema persistir, entre em contato com o suporte.
            </div>
          </div>
        </div>
      );
    }

    // No error, render children normally
    return this.props.children;
  }
}

export default ErrorBoundary;
