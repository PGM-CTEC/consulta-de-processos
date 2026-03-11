# Auto-Detecção de Cookie PAV via Backend Proxy - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Permitir ao usuário detectar automaticamente o cookie JSESSIONID do PAV Fusion clicando um botão, sem precisar copiar/colar manualmente.

**Architecture:** Backend (`/fusion/detect-cookie`) conecta à instância PAV Rio, extrai o novo JSESSIONID da resposta, valida a sessão, e persiste em `.pav_session`. Frontend mostra botão "🔗 Detectar Automaticamente" que dispara essa detecção e exibe status em tempo real.

**Tech Stack:** FastAPI (backend), httpx (HTTP client), React (frontend), Vite

---

## Task 1: Adicionar endpoint de detecção no backend

**Files:**
- Modify: `backend/main.py`
- Test: `backend/tests/test_fusion_detect.py` (novo)

**Step 1: Criar arquivo de testes**

Criar `backend/tests/test_fusion_detect.py`:

```python
import pytest
from unittest.mock import patch, AsyncMock
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.mark.asyncio
async def test_detect_cookie_success():
    """Testa detecção bem-sucedida de cookie PAV"""
    with patch('httpx.AsyncClient.get') as mock_get:
        # Simula resposta do PAV com JSESSIONID
        mock_response = AsyncMock()
        mock_response.cookies = {'JSESSIONID': 'ABC123XYZ789'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = client.post('/fusion/detect-cookie')
        assert response.status_code == 200
        assert 'JSESSIONID' in response.json()
        assert response.json()['success'] is True

@pytest.mark.asyncio
async def test_detect_cookie_pav_unavailable():
    """Testa quando PAV está indisponível"""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = Exception("Connection refused")

        response = client.post('/fusion/detect-cookie')
        assert response.status_code == 503
        assert 'PAV indisponível' in response.json()['error']

@pytest.mark.asyncio
async def test_detect_cookie_invalid_response():
    """Testa quando PAV não retorna JSESSIONID"""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.cookies = {}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = client.post('/fusion/detect-cookie')
        assert response.status_code == 400
        assert 'cookie não encontrado' in response.json()['error']
```

**Step 2: Rodar testes para confirmar que falham**

```bash
cd backend
pytest tests/test_fusion_detect.py -v
```

Esperado: **FAIL** - endpoint `/fusion/detect-cookie` não existe

**Step 3: Implementar o endpoint no backend**

Adicionar no `backend/main.py` (antes do `if __name__`):

```python
import httpx
from pathlib import Path

PAV_BASE_URL = os.getenv('PAV_URL', 'https://pav.procuradoria.rio')
SESSION_FILE = Path('.pav_session')

@app.post('/fusion/detect-cookie')
async def detect_fusion_cookie():
    """
    Detecta automaticamente o cookie JSESSIONID do PAV Fusion
    conectando à instância PGM Rio e extraindo a sessão.
    """
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            # Tenta acessar um endpoint do PAV que gera JSESSIONID
            response = await client.get(
                f'{PAV_BASE_URL}/portal/action/Login/view/normal',
                follow_redirects=True
            )

            # Extrai JSESSIONID dos cookies
            jsessionid = response.cookies.get('JSESSIONID')
            if not jsessionid:
                return {
                    'success': False,
                    'error': 'Cookie JSESSIONID não encontrado na resposta do PAV'
                }, 400

            # Valida a sessão fazendo um teste rápido
            try:
                validation_response = await client.get(
                    f'{PAV_BASE_URL}/services/arquivos/search?numero=0000000',
                    cookies={'JSESSIONID': jsessionid},
                    timeout=5.0
                )

                if validation_response.status_code in [200, 400, 401]:
                    # 200 = sucesso, 400/401 = cookie válido mas sem permissão
                    # (indica que o PAV reconheceu a sessão)

                    # Salva o cookie em .pav_session
                    SESSION_FILE.write_text(jsessionid)

                    return {
                        'success': True,
                        'message': 'Cookie PAV detectado automaticamente!',
                        'jsessionid': jsessionid[:10] + '...'  # Mostra apenas parte
                    }
                else:
                    return {
                        'success': False,
                        'error': f'PAV retornou status {validation_response.status_code}'
                    }, 400

            except Exception as validate_error:
                return {
                    'success': False,
                    'error': f'Erro ao validar sessão: {str(validate_error)}'
                }, 400

    except httpx.ConnectError:
        return {
            'success': False,
            'error': 'PAV indisponível - verifique a conexão ou tente mais tarde'
        }, 503
    except httpx.TimeoutException:
        return {
            'success': False,
            'error': 'Timeout ao conectar ao PAV - servidor lento ou indisponível'
        }, 503
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro inesperado: {str(e)}'
        }, 500
```

**Step 4: Rodar testes para confirmar que passam**

```bash
pytest tests/test_fusion_detect.py -v
```

Esperado: **PASS** - todos os testes passam

**Step 5: Commit**

```bash
git add backend/main.py backend/tests/test_fusion_detect.py
git commit -m "feat: adicionar endpoint /fusion/detect-cookie para auto-detecção de JSESSIONID"
```

---

## Task 2: Adicionar função helper no frontend para chamar o endpoint

**Files:**
- Create: `frontend/src/utils/fusion-cookie-detector.js`
- Test: `frontend/src/tests/fusion-cookie-detector.test.js` (novo)

**Step 1: Criar arquivo de testes**

Criar `frontend/src/tests/fusion-cookie-detector.test.js`:

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { detectFusionCookieAuto } from '../utils/fusion-cookie-detector';

describe('detectFusionCookieAuto', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve retornar sucesso com JSESSIONID quando detectado', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
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
});
```

**Step 2: Rodar testes para confirmar que falham**

```bash
cd frontend
npm run test -- fusion-cookie-detector.test.js
```

Esperado: **FAIL** - função `detectFusionCookieAuto` não existe

**Step 3: Implementar a função helper**

Criar `frontend/src/utils/fusion-cookie-detector.js`:

```javascript
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
```

**Step 4: Rodar testes para confirmar que passam**

```bash
npm run test -- fusion-cookie-detector.test.js
```

Esperado: **PASS** - todos os testes passam

**Step 5: Commit**

```bash
git add frontend/src/utils/fusion-cookie-detector.js frontend/src/tests/fusion-cookie-detector.test.js
git commit -m "feat: adicionar helper detectFusionCookieAuto no frontend"
```

---

## Task 3: Integrar o botão "Detectar Automaticamente" no Settings.jsx

**Files:**
- Modify: `frontend/src/components/Settings.jsx`

**Step 1: Analisar o Settings.jsx atual**

```bash
head -100 frontend/src/components/Settings.jsx
```

Localize a seção que renderiza o input de cookie (provavelmente perto de "bookmarklet" ou "PAV")

**Step 2: Adicionar imports no topo**

No `Settings.jsx`, adicione após os imports existentes:

```javascript
import { detectFusionCookieAuto, formatDetectionError } from '../utils/fusion-cookie-detector';
```

**Step 3: Adicionar estado para a detecção**

Dentro do componente Settings (após outros `useState`):

```javascript
const [isDetecting, setIsDetecting] = useState(false);
const [detectionMessage, setDetectionMessage] = useState(null);
const [detectionStatus, setDetectionStatus] = useState(null); // 'success', 'error', 'pending'
```

**Step 4: Implementar handler de clique**

Adicione esta função dentro do componente:

```javascript
const handleDetectCookie = async () => {
  setIsDetecting(true);
  setDetectionMessage(null);
  setDetectionStatus('pending');

  const result = await detectFusionCookieAuto({
    retries: 3,
    timeout: 10000
  });

  if (result.success) {
    setDetectionStatus('success');
    setDetectionMessage(
      `✅ ${result.message}\nCookie: ${result.jsessionid}`
    );
    // Simula atualização visual (em um app real, você atualizaria o estado de status)
    setTimeout(() => {
      setDetectionStatus(null);
    }, 5000);
  } else {
    setDetectionStatus('error');
    setDetectionMessage(formatDetectionError(result));
  }

  setIsDetecting(false);
};
```

**Step 5: Adicionar o botão no JSX (perto do input de cookie)**

Localize a seção de configuração do cookie e adicione:

```jsx
<div className="fusion-cookie-section" style={{ marginBottom: '20px' }}>
  <h3>🔐 Autenticação PAV Fusion</h3>

  {/* Botão de Detecção Automática */}
  <button
    onClick={handleDetectCookie}
    disabled={isDetecting}
    style={{
      marginBottom: '10px',
      padding: '10px 16px',
      backgroundColor: isDetecting ? '#ccc' : '#2563eb',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: isDetecting ? 'not-allowed' : 'pointer',
      fontSize: '14px',
      fontWeight: 500
    }}
  >
    {isDetecting ? '⏳ Detectando...' : '🔗 Detectar Automaticamente'}
  </button>

  {/* Mensagem de Status */}
  {detectionMessage && (
    <div
      style={{
        marginBottom: '10px',
        padding: '12px',
        backgroundColor:
          detectionStatus === 'success' ? '#d1fae5' :
          detectionStatus === 'error' ? '#fee2e2' : '#fef3c7',
        color:
          detectionStatus === 'success' ? '#065f46' :
          detectionStatus === 'error' ? '#7f1d1d' : '#92400e',
        borderRadius: '4px',
        fontSize: '13px',
        whiteSpace: 'pre-wrap',
        fontFamily: 'monospace'
      }}
    >
      {detectionMessage}
    </div>
  )}

  {/* Input manual (fallback) */}
  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 500 }}>
    Ou cole o JSESSIONID manualmente:
  </label>
  <input
    type="password"
    placeholder="JSESSIONID=ABC123XYZ..."
    style={{
      width: '100%',
      padding: '8px',
      border: '1px solid #ddd',
      borderRadius: '4px',
      fontSize: '13px'
    }}
  />
</div>
```

**Step 6: Rodar a aplicação e testar no navegador**

```bash
npm run dev
```

Abra http://localhost:5173, vá para Configurações, e clique em "🔗 Detectar Automaticamente"

Esperado:
- Spinner enquanto processa
- ✅ Mensagem de sucesso se cookie detectado
- ❌ Mensagem de erro com dica se falhar

**Step 7: Commit**

```bash
git add frontend/src/components/Settings.jsx
git commit -m "feat: adicionar botão 'Detectar Automaticamente' em Configurações"
```

---

## Task 4: Testar a integração end-to-end

**Step 1: Verificar se .env tem as variáveis necessárias**

```bash
cat .env | grep -i pav
```

Deve ter algo como:
```
PAV_URL=https://pav.procuradoria.rio
```

Se não tiver, adicione em `.env`

**Step 2: Rodar backend em background**

```bash
cd backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
```

**Step 3: Rodar frontend**

```bash
cd frontend
npm run dev
```

**Step 4: Testar manualmente**

1. Abra http://localhost:5173
2. Vá para ⚙️ Configurações
3. Clique em "🔗 Detectar Automaticamente"
4. Observe o resultado:
   - ✅ Se sucesso: mostra cookie detectado
   - ❌ Se PAV indisponível: mostra erro apropriado
   - ⏱️ Se timeout: volta com sugestão

**Step 5: Rodar todos os testes**

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm run test
```

Esperado: **PASS** em todos

**Step 6: Commit final**

```bash
git add -A
git commit -m "test: validar integração end-to-end de detecção automática de cookie"
```

---

## Task 5: Documentar a feature em CLAUDE.md

**Files:**
- Modify: `.claude/CLAUDE.md` (adicionar seção)

**Step 1: Adicionar documentação**

No `.claude/CLAUDE.md`, adicione uma nova seção:

```markdown
## Auto-Detecção de Cookie PAV Fusion

### Funcionalidade
Usuários podem clicar em "🔗 Detectar Automaticamente" nas Configurações para que o backend se conecte ao PAV Rio e extraia o JSESSIONID automaticamente, sem necessidade de copiar/colar manualmente.

### Arquitetura
- **Backend:** `POST /fusion/detect-cookie` (httpx) → PAV Rio → extrai JSESSIONID → valida → persiste em `.pav_session`
- **Frontend:** Botão em Settings → chamada a `detectFusionCookieAuto()` → exibe status
- **Fallback:** Input manual de texto com validação

### Variáveis de Ambiente
```
PAV_URL=https://pav.procuradoria.rio
```

### Como Testar
1. Clique em "🔗 Detectar Automaticamente" em Configurações
2. Observe o status (sucesso, erro, timeout)
3. Verifique se arquivo `.pav_session` foi criado com o novo cookie

### Tratamento de Erros
- **503 PAV indisponível:** Guia usuário a tentar mais tarde ou fazer login manual
- **400 Cookie não encontrado:** Sugere verificar se está logado no PAV
- **Timeout:** Indica PAV lento, oferece retry automático (máx 3 tentativas)
```

**Step 2: Commit**

```bash
git add .claude/CLAUDE.md
git commit -m "docs: adicionar documentação de auto-detecção de cookie PAV"
```

---

## Summary

✅ **Plan Complete**

Suas mudanças:
1. ✅ Endpoint `/fusion/detect-cookie` com testes
2. ✅ Helper `detectFusionCookieAuto()` com retry inteligente
3. ✅ Botão "Detectar Automaticamente" integrado em Settings
4. ✅ Tratamento de erros com mensagens user-friendly
5. ✅ Documentação atualizada

**Próximas Steps:**
- Backend conecta a `https://pav.procuradoria.rio/portal/action/Login/view/normal`
- Extrai `JSESSIONID` da resposta
- Valida fazendo teste com endpoint de search
- Persiste em `.pav_session`
