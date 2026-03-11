/**
 * Detecta automaticamente o cookie JSESSIONID do PAV Fusion
 * chamando o backend que se conecta ao PAV Rio
 *
 * @param {Object} options - Opções
 * @param {number} options.retries - Número de tentativas em caso de erro (padrão: 2)
 * @param {number} options.timeout - Timeout em ms (padrão: 15000)
 * @returns {Promise<Object>} {success, jsessionid, message/error}
 */
export async function detectFusionCookieAuto(options = {}) {
  const { retries = 2, timeout = 15000 } = options;

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch('/fusion/detect-cookie', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || `Erro ${response.status}: ${response.statusText}`,
          statusCode: response.status,
          attempt
        };
      }

      return {
        ...data,
        attempt
      };
    } catch (error) {
      const isLastAttempt = attempt === retries;
      const isTimeoutError = error.name === 'AbortError';

      if (isLastAttempt) {
        return {
          success: false,
          error: isTimeoutError
            ? 'Timeout ao detectar cookie (PAV lento ou indisponível)'
            : error.message,
          attempt,
          isTimeoutError
        };
      }

      // Retry com backoff exponencial: 1s, 2s, 4s...
      await new Promise(resolve =>
        setTimeout(resolve, Math.pow(2, attempt - 1) * 1000)
      );
    }
  }
}

/**
 * Formata mensagem de erro amigável ao usuário
 * @param {Object} result - Resultado de detectFusionCookieAuto
 * @returns {string} Mensagem formatada
 */
export function formatDetectionError(result) {
  if (result.isTimeoutError) {
    return '⏱️ Timeout: PAV está lento ou indisponível. Tente mais tarde.';
  }

  if (result.statusCode === 503) {
    return '🔴 PAV está indisponível no momento. Tente fazer login manualmente.';
  }

  if (result.statusCode === 400) {
    return '⚠️ Cookie não encontrado. Verifique se está logado no PAV.';
  }

  return `❌ Erro: ${result.error}`;
}
