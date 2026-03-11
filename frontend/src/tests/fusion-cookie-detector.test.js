import { describe, it, expect, vi, beforeEach } from 'vitest';
import { detectFusionCookieAuto, formatDetectionError } from '../utils/fusion-cookie-detector';

describe('detectFusionCookieAuto', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve retornar sucesso com JSESSIONID quando detectado', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            success: true,
            jsessionid: 'ABC123...',
            message: 'Cookie PAV detectado automaticamente!'
          })
      })
    );

    const result = await detectFusionCookieAuto();
    expect(result.success).toBe(true);
    expect(result.jsessionid).toBeDefined();
    expect(result.message).toBeDefined();
  });

  it('deve retornar erro quando PAV indisponível', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 503,
        json: () =>
          Promise.resolve({
            success: false,
            error: 'PAV indisponível'
          })
      })
    );

    const result = await detectFusionCookieAuto();
    expect(result.success).toBe(false);
    expect(result.error).toContain('indisponível');
    expect(result.statusCode).toBe(503);
  });

  it('deve fazer retry em timeout', async () => {
    let callCount = 0;
    global.fetch = vi.fn(() => {
      callCount++;
      if (callCount === 1) {
        return Promise.reject(new Error('timeout'));
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            success: true,
            jsessionid: 'ABC123...'
          })
      });
    });

    const result = await detectFusionCookieAuto({ retries: 2 });
    expect(result.success).toBe(true);
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it('deve retornar erro após máximo de tentativas', async () => {
    global.fetch = vi.fn(() =>
      Promise.reject(new Error('Network error'))
    );

    const result = await detectFusionCookieAuto({ retries: 2 });
    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

});

describe('formatDetectionError', () => {
  it('deve formatar erro de timeout', () => {
    const result = {
      isTimeoutError: true,
      error: 'Timeout'
    };
    const message = formatDetectionError(result);
    expect(message).toContain('Timeout');
    expect(message).toContain('lento');
  });

  it('deve formatar erro 503 (indisponível)', () => {
    const result = {
      statusCode: 503,
      error: 'Service Unavailable'
    };
    const message = formatDetectionError(result);
    expect(message).toContain('indisponível');
    expect(message).toContain('🔴');
  });

  it('deve formatar erro 400 (cookie não encontrado)', () => {
    const result = {
      statusCode: 400,
      error: 'Cookie not found'
    };
    const message = formatDetectionError(result);
    expect(message).toContain('Cookie não encontrado');
    expect(message).toContain('⚠️');
  });

  it('deve formatar erro genérico', () => {
    const result = {
      statusCode: 500,
      error: 'Internal server error'
    };
    const message = formatDetectionError(result);
    expect(message).toContain('Erro');
    expect(message).toContain('❌');
  });
});
