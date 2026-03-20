/**
 * User-friendly error messages for common error scenarios.
 * Replaces technical messages with actionable, friendly text.
 */

export const ERROR_MESSAGES = {
  // Process search errors
  PROCESS_NOT_FOUND: 'Processo não encontrado. Verifique o número e tente novamente.',
  INVALID_PROCESS_NUMBER: 'Número de processo inválido. Use o formato: 0000000-00.0000.0.00.0000',
  SEARCH_FAILED: 'Não foi possível realizar a busca. Verifique sua conexão e tente novamente.',

  // Bulk search errors
  BULK_UPLOAD_FAILED: 'Falha ao processar o arquivo. Verifique se está no formato .txt, .csv ou .xlsx.',
  BULK_SEARCH_FAILED: 'A busca em lote falhou. Tente novamente em alguns instantes.',
  EMPTY_FILE: 'O arquivo enviado não contém números de processo.',
  FILE_TOO_LARGE: 'O arquivo é muito grande. O limite máximo é 10MB.',

  // Export errors
  EXPORT_FAILED: 'Falha ao gerar o relatório. Tente novamente.',

  // API / connection errors
  API_UNAVAILABLE: 'Serviço temporariamente indisponível. Aguarde alguns minutos e tente novamente.',
  NETWORK_ERROR: 'Erro de conexão. Verifique sua internet e tente novamente.',
  TIMEOUT: 'A consulta demorou muito. Tente com menos processos de uma vez.',
  RATE_LIMITED: 'Muitas requisições em pouco tempo. Aguarde um momento e tente novamente.',

  // Generic
  UNKNOWN_ERROR: 'Ocorreu um erro inesperado. Se o problema persistir, entre em contato com o suporte.',
};

/**
 * Get a user-friendly error message from an API error
 * @param {Error|object} error - The error object
 * @returns {string} User-friendly error message
 */
export function getFriendlyErrorMessage(error) {
  if (!error) return ERROR_MESSAGES.UNKNOWN_ERROR;

  const status = error?.response?.status || error?.status;
  const message = error?.message || '';

  if (status === 404) return ERROR_MESSAGES.PROCESS_NOT_FOUND;
  if (status === 422) return ERROR_MESSAGES.INVALID_PROCESS_NUMBER;
  if (status === 429) return ERROR_MESSAGES.RATE_LIMITED;
  if (status >= 500) return ERROR_MESSAGES.API_UNAVAILABLE;
  if (message.includes('timeout')) return ERROR_MESSAGES.TIMEOUT;
  if (message.includes('network') || message.includes('Network')) return ERROR_MESSAGES.NETWORK_ERROR;

  return ERROR_MESSAGES.UNKNOWN_ERROR;
}

export default { ERROR_MESSAGES, getFriendlyErrorMessage };
