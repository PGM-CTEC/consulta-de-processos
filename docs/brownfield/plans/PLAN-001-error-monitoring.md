# Implementation Plan: Error Monitoring Integration (Sentry)

**Plan ID:** PLAN-001
**Sprint:** 1 (Critical)
**Effort:** M (3-5 dias)
**Priority:** CRITICAL
**Owner:** @dev
**Architect:** @architect (Aria)
**Created:** 2026-02-21

---

## 1. Overview

### 1.1 Objective
Implementar error monitoring centralizado usando Sentry para capturar e rastrear erros em produção (backend + frontend), permitindo detecção proativa de issues e redução de MTTR (Mean Time To Recovery).

### 1.2 Business Value
- **Operational Excellence:** Visibilidade de 0% → 100% de erros em produção
- **MTTR:** Redução de horas/dias → minutos para detecção de issues
- **User Experience:** Identificação proativa de problemas antes de usuários reportarem
- **Cost Avoidance:** Prevenção de cascading failures via alertas early-warning

### 1.3 Success Criteria
- [ ] Sentry SDK integrado no backend (Python)
- [ ] Sentry SDK integrado no frontend (JavaScript)
- [ ] Erros capturados automaticamente em ambas as camadas
- [ ] Alertas configurados para CRITICAL errors (Slack/Email)
- [ ] Dashboard Sentry acessível com métricas
- [ ] Breadcrumbs contextuais em errors
- [ ] Performance monitoring ativo (opcional, Phase 2)

---

## 2. Technical Approach

### 2.1 Sentry Architecture

```mermaid
graph TB
    Frontend[React App]
    Backend[FastAPI App]

    subgraph "Sentry Cloud"
        SentryAPI[Sentry API]
        Dashboard[Sentry Dashboard]
        Alerts[Alert Rules]
    end

    Frontend -->|@sentry/react SDK| SentryAPI
    Backend -->|sentry-sdk Python| SentryAPI
    SentryAPI --> Dashboard
    SentryAPI --> Alerts
    Alerts -->|Webhook| Slack[Slack Channel]
    Alerts -->|Email| Team[Dev Team]

    style Frontend fill:#e1f5ff
    style Backend fill:#fff4e1
    style SentryAPI fill:#ffe1e1
```

### 2.2 Implementation Strategy

**Backend:**
- SDK: `sentry-sdk[fastapi]` (latest)
- Integration: ASGI middleware + FastAPI integration
- Capture: Unhandled exceptions + custom error tracking
- Context: User info, request data, environment

**Frontend:**
- SDK: `@sentry/react` + `@sentry/browser`
- Integration: ErrorBoundary + React Router
- Capture: Unhandled exceptions + async errors
- Context: User actions, route changes, API calls

---

## 3. Implementation Phases

### Phase 1: Setup Sentry Account & Projects (30 min)

**Tasks:**
1. [ ] Criar conta Sentry (free tier ou paid)
2. [ ] Criar projeto "consulta-processo-backend"
3. [ ] Criar projeto "consulta-processo-frontend"
4. [ ] Obter DSN keys (Backend DSN, Frontend DSN)
5. [ ] Configurar Team Settings (add developers)

**Deliverable:** DSN keys prontos para uso

---

### Phase 2: Backend Integration (2-3 horas)

**Tasks:**

#### 2.1 Install SDK
```bash
cd backend
pip install sentry-sdk[fastapi]
echo "sentry-sdk[fastapi]" >> requirements.txt
```

#### 2.2 Configure Sentry in `backend/config.py`
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Sentry Configuration
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"  # development, staging, production
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0  # 1.0 = 100% (reduce in prod: 0.1)
    SENTRY_ENABLE: bool = True
```

#### 2.3 Initialize in `backend/main.py`
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from .config import settings

# Initialize Sentry BEFORE creating FastAPI app
if settings.SENTRY_ENABLE and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        # Send 100% of errors
        before_send=lambda event, hint: event,
    )
    logger.info(f"Sentry initialized (env: {settings.SENTRY_ENVIRONMENT})")

app = FastAPI(...)
```

#### 2.4 Add Custom Error Tracking in `services/process_service.py`
```python
import sentry_sdk

async def get_or_update_process(self, number: str):
    try:
        # ... existing code ...
    except DataJudAPIException as e:
        # Capture custom context
        sentry_sdk.set_context("datajud", {
            "process_number": number,
            "error_message": e.message,
            "tribunal_alias": self.client._get_tribunal_alias(number)
        })
        sentry_sdk.capture_exception(e)
        raise
```

#### 2.5 Test Backend Integration
```bash
# Trigger test error
curl http://localhost:8011/processes/00000000000000000000
# Check Sentry dashboard for error
```

**Files Modified:**
- `backend/requirements.txt` (add sentry-sdk[fastapi])
- `backend/config.py` (add SENTRY_* settings)
- `backend/main.py` (initialize Sentry)
- `backend/services/process_service.py` (custom context)
- `backend/.env` (add SENTRY_DSN, SENTRY_ENVIRONMENT)

**Acceptance Criteria:**
- [ ] Backend errors aparecem no Sentry dashboard
- [ ] Stack traces completas visíveis
- [ ] Context (process number, tribunal) capturado
- [ ] Request data (headers, body) anexado

---

### Phase 3: Frontend Integration (2-3 horas)

**Tasks:**

#### 3.1 Install SDK
```bash
cd frontend
npm install --save @sentry/react @sentry/browser
```

#### 3.2 Configure in `frontend/src/main.jsx`
```javascript
import * as Sentry from "@sentry/react";

// Initialize Sentry BEFORE rendering React
if (import.meta.env.VITE_SENTRY_DSN && import.meta.env.VITE_SENTRY_ENABLE === 'true') {
    Sentry.init({
        dsn: import.meta.env.VITE_SENTRY_DSN,
        environment: import.meta.env.VITE_ENVIRONMENT || 'development',
        integrations: [
            Sentry.browserTracingIntegration(),
            Sentry.replayIntegration(),
        ],
        tracesSampleRate: 1.0, // 100% in dev, reduce to 0.1 in prod
        replaysSessionSampleRate: 0.1, // 10% of sessions
        replaysOnErrorSampleRate: 1.0, // 100% when error occurs
    });
    console.log('[Sentry] Initialized');
}

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <Sentry.ErrorBoundary fallback={<ErrorFallback />}>
            <App />
        </Sentry.ErrorBoundary>
    </React.StrictMode>
);
```

#### 3.3 Create Error Fallback Component
```javascript
// frontend/src/components/ErrorFallback.jsx
function ErrorFallback({ error, resetError }) {
    return (
        <div role="alert" className="error-fallback">
            <h2>Oops! Algo deu errado</h2>
            <p>Nosso time foi notificado. Por favor, tente novamente.</p>
            <button onClick={resetError}>Tentar Novamente</button>
            {import.meta.env.DEV && <pre>{error.message}</pre>}
        </div>
    );
}
```

#### 3.4 Add Custom Context in `services/api.js`
```javascript
import * as Sentry from "@sentry/react";

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Add context to Sentry
        Sentry.setContext("api_error", {
            url: error.config?.url,
            method: error.config?.method,
            status: error.response?.status,
            data: error.response?.data,
        });
        Sentry.captureException(error);

        return Promise.reject(error);
    }
);
```

#### 3.5 Update `.env.development`
```env
VITE_SENTRY_DSN=https://your-frontend-dsn@sentry.io/project-id
VITE_SENTRY_ENABLE=true
VITE_ENVIRONMENT=development
```

#### 3.6 Test Frontend Integration
```javascript
// Add test error button (dev only)
<button onClick={() => { throw new Error("Test Sentry Frontend"); }}>
    Test Error
</button>
```

**Files Modified:**
- `frontend/package.json` (add @sentry/react)
- `frontend/src/main.jsx` (initialize Sentry)
- `frontend/src/components/ErrorFallback.jsx` (new file)
- `frontend/src/services/api.js` (add context)
- `frontend/.env.development` (add SENTRY_DSN)
- `frontend/.env.production` (add SENTRY_DSN - masked)

**Acceptance Criteria:**
- [ ] Frontend errors aparecem no Sentry dashboard
- [ ] Component stack traces visíveis
- [ ] API call context capturado (URL, method, status)
- [ ] Session replay disponível (opcional)

---

### Phase 4: Configure Alerts & Notifications (1 hora)

**Tasks:**

#### 4.1 Create Alert Rules in Sentry Dashboard

**Backend Alert (CRITICAL Errors):**
```yaml
Name: "Backend CRITICAL Errors"
Condition: "Event Level is equal to error OR fatal"
Filter: "environment is production"
Action:
  - Send notification to Slack (#alerts-backend)
  - Send email to team@example.com
Frequency: "Send a notification at most once every 5 minutes"
```

**Frontend Alert (High Volume Errors):**
```yaml
Name: "Frontend Error Spike"
Condition: "Event count is more than 10 in 1 minute"
Filter: "environment is production"
Action:
  - Send notification to Slack (#alerts-frontend)
Frequency: "Send a notification at most once every 15 minutes"
```

#### 4.2 Configure Slack Integration
1. Go to Sentry → Settings → Integrations
2. Add Slack integration
3. Authorize workspace
4. Map alert rules to channels

#### 4.3 Configure Email Notifications
1. Go to Sentry → Settings → Notifications
2. Add team email addresses
3. Configure notification preferences (all errors vs critical only)

**Acceptance Criteria:**
- [ ] Slack recebe notificações de CRITICAL errors
- [ ] Email enviado para team em caso de error spike
- [ ] Notifications não são spam (rate limiting funciona)

---

### Phase 5: Testing & Validation (1-2 horas)

**Tasks:**

#### 5.1 Backend Error Scenarios
```python
# Test 1: DataJud API Error
curl http://localhost:8011/processes/12345678901234567890
# Expected: Sentry captures InvalidProcessNumberException

# Test 2: Database Error
# Manually corrupt DB, trigger query
# Expected: Sentry captures SQLAlchemy error

# Test 3: Unhandled Exception
# Add: raise Exception("Test Sentry") in endpoint
# Expected: Sentry captures with full context
```

#### 5.2 Frontend Error Scenarios
```javascript
// Test 1: Component Error
<button onClick={() => { throw new Error("Test"); }}>Test</button>

// Test 2: Async Error
async function testAsync() {
    throw new Error("Async error");
}

// Test 3: API Error
// Trigger 404 or 500 from backend
// Expected: Sentry captures with API context
```

#### 5.3 Verify Dashboard Metrics
- [ ] Errors aparecem em real-time (<10s latency)
- [ ] Stack traces completas
- [ ] Breadcrumbs mostram user actions
- [ ] Environment tags corretos (dev/staging/prod)
- [ ] Release versions detectadas (se configurado)

#### 5.4 Performance Baseline
- [ ] Overhead de Sentry < 50ms por request
- [ ] Sem impacto perceptível em UX
- [ ] Memory usage estável

**Acceptance Criteria:**
- [ ] 5+ tipos de erros testados e capturados
- [ ] Alertas disparados corretamente
- [ ] Dashboard mostra métricas em tempo real
- [ ] Performance não degradada

---

## 4. Rollback Plan

**If Sentry Causes Issues:**

### 4.1 Disable via Environment Variable
```bash
# Backend
export SENTRY_ENABLE=false

# Frontend
export VITE_SENTRY_ENABLE=false
```

### 4.2 Remove SDK (if necessary)
```bash
# Backend
pip uninstall sentry-sdk

# Frontend
npm uninstall @sentry/react @sentry/browser
```

### 4.3 Revert Code Changes
```bash
git checkout backend/main.py
git checkout frontend/src/main.jsx
```

**Rollback Time:** < 5 minutos

---

## 5. Dependencies

### 5.1 External Dependencies
- [ ] Sentry account criada (free tier: 5k errors/month)
- [ ] DSN keys obtidos
- [ ] Slack workspace access (para integração)

### 5.2 Internal Dependencies
- [ ] `.env` files com SENTRY_DSN configurados
- [ ] Team emails adicionados ao Sentry
- [ ] Production environment definido

### 5.3 Blocking Dependencies
**None** - Pode ser implementado independentemente de outras tasks

---

## 6. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Sentry overhead degrada performance** | LOW | MEDIUM | Monitor metrics, reduce sample rate se necessário |
| **Sensitive data leakada em errors** | MEDIUM | HIGH | Configure `before_send` para scrubbing, redact PII |
| **Alert fatigue (too many notifications)** | MEDIUM | MEDIUM | Start conservative, tune thresholds iteratively |
| **Free tier limit exceeded** | LOW | MEDIUM | Monitor quota, upgrade to paid plan se necessário |
| **SDK bugs causam crashes** | LOW | HIGH | Test thoroughly em staging, enable/disable via env var |

### 6.1 Sensitive Data Scrubbing

**Backend (`before_send` hook):**
```python
def before_send(event, hint):
    # Redact CPF, process numbers, API keys
    if 'request' in event:
        event['request']['data'] = scrub_sensitive(event['request']['data'])
    return event

sentry_sdk.init(dsn=..., before_send=before_send)
```

**Frontend (`beforeSend` hook):**
```javascript
Sentry.init({
    beforeSend(event, hint) {
        // Remove user PII from breadcrumbs
        if (event.breadcrumbs) {
            event.breadcrumbs = event.breadcrumbs.map(scrubBreadcrumb);
        }
        return event;
    }
});
```

---

## 7. Post-Implementation

### 7.1 Documentation
- [ ] Update `README.md` com instruções Sentry
- [ ] Documentar alert rules em `docs/operations/sentry-alerts.md`
- [ ] Add runbook para "Sentry Down" scenario

### 7.2 Team Training
- [ ] Demo Sentry dashboard para team
- [ ] Treinar em como investigar errors
- [ ] Definir SLA para error triage (ex: CRITICAL < 1h)

### 7.3 Monitoring
- [ ] Daily review de Sentry dashboard (primeira semana)
- [ ] Weekly error trend analysis
- [ ] Tune alert thresholds baseado em volume real

---

## 8. Checklist Final

### Pre-Implementation
- [ ] Sentry account criada
- [ ] DSN keys obtidos (backend + frontend)
- [ ] `.env` files preparados
- [ ] Team notificado sobre novo monitoring

### Implementation
- [ ] Backend SDK instalado e configurado
- [ ] Frontend SDK instalado e configurado
- [ ] Custom context adicionado (process numbers, API calls)
- [ ] Error fallback UI implementado (frontend)
- [ ] Alert rules configuradas (Slack + Email)

### Testing
- [ ] 5+ error scenarios testados (backend + frontend)
- [ ] Alerts disparados corretamente
- [ ] Performance baseline validado (< 50ms overhead)
- [ ] Sensitive data scrubbing verificado

### Post-Implementation
- [ ] Documentation atualizada
- [ ] Team treinado
- [ ] Monitoring ativo (daily reviews primeira semana)

---

## 9. Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| **Phase 1: Setup Account** | 30 min | None |
| **Phase 2: Backend Integration** | 2-3 horas | Phase 1 |
| **Phase 3: Frontend Integration** | 2-3 horas | Phase 1 |
| **Phase 4: Alerts Config** | 1 hora | Phase 2, 3 |
| **Phase 5: Testing** | 1-2 horas | Phase 2, 3, 4 |
| **Total** | **7-10 horas** (1-2 dias) | |

**Effort Estimate:** M (3-5 dias including documentation and training)

---

**Plan Status:** ✅ Ready for Implementation
**Next Action:** Assign to @dev for execution
**Architect Approval:** @architect (Aria) - 2026-02-21
