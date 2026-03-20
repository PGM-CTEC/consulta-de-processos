# Story BR-001: Implement Structured Local Logging

**Story ID:** BR-001
**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** 1 (Critical)
**Priority:** CRITICAL
**Status:** Ready
**Type:** Feature / Operations
**Complexity:** 5 points
**Estimated Effort:** 4-6 hours (1-2 dias)

---

## Description

### Problem
O projeto "Consulta Processo" não possui error logging estruturado. Quando erros ocorrem:
- **Falta contexto** (apenas mensagem genérica)
- **Difícil debugar** (sem stack traces estruturados)
- **Sem histórico** (logs não persistem ou são difíceis de encontrar)
- **Impossível filtrar** (sem ferramenta para buscar erros específicos)

### Solution
Implementar **logging estruturado local** com:
- JSON logs com contexto completo (timestamp, level, processo number, stack trace, request data)
- Rotação automática de logs (por tamanho e data)
- CLI tool para visualizar e filtrar logs
- Suporte a múltiplos níveis (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Business Value
- **No External Dependencies:** Zero custo SaaS
- **Local Control:** Dados de erro nunca saem do servidor
- **Easy Debugging:** Contexto estruturado em JSON
- **Compliance:** LGPD compliant (sem envio de dados externos)
- **Scalability:** Logs locais vs dependência de SaaS

---

## Acceptance Criteria

### Given
- O projeto está em desenvolvimento/staging
- Backend usa FastAPI, Frontend usa React
- Logs devem ser armazenados localmente

### When
- Um erro não capturado ocorre no backend (FastAPI)
- Uma exceção não capturada ocorre no frontend (React)
- Um erro é logado manualmente via `logger.error()`
- Uma sessão de usuário resulta em erro

### Then
- ✅ Erro seja escrito em arquivo JSON local (backend.log, frontend.log)
- ✅ Stack trace completo em JSON (filename, line number, function, args)
- ✅ Context seja capturado (timestamp, level, processo number, request URL)
- ✅ Logs rotacionem automaticamente (por tamanho 10MB e data)
- ✅ CLI tool `logs-view` funcione para filtrar/buscar logs
- ✅ Exemplo: `logs-view --level ERROR --process 123456789` retorna erros específicos
- ✅ Performance impact <10ms por log (local write)
- ✅ Sem dados sensíveis (CPF, API keys) nos logs (redaction)

---

## Scope

### In Scope ✅

1. **Backend Logging Setup (Python/FastAPI)**
   - Install `python-json-logger` package
   - Configure JSON formatter em `backend/main.py`
   - Setup `RotatingFileHandler` (10MB size, daily rotation)
   - Exception handling middleware com contexto
   - Custom logger para DataJud API calls
   - Custom logger para database operations

2. **Frontend Logging Setup (JavaScript/React)**
   - Configure custom logger em `frontend/src/main.jsx`
   - ErrorBoundary para capturar erros de componentes
   - Axios interceptor com logging
   - Unhandled promise rejection handler
   - Local storage para buffer de logs

3. **CLI Tool (`logs-view`)**
   - Python script `backend/scripts/logs-view.py`
   - Filtros: `--level`, `--process`, `--service`, `--time-range`
   - Output formatters: JSON, table, summary
   - Search capability (regex support)
   - Log tail/follow mode

4. **Testing & Validation**
   - Test backend errors (DataJud 404, DB error, custom)
   - Test frontend errors (component error, async error, API error)
   - Verify log files created and formatted correctly
   - Performance baseline (<10ms per log write)
   - Log rotation verification (size and time-based)

### Out of Scope ❌

- Centralized log aggregation (ELK, Splunk) - Future migration
- Real-time alerting system - Future iteration
- Advanced analytics on logs - Future iteration
- Log encryption at rest - Future iteration
- Distributed tracing across services - Future iteration
- Frontend local storage overflow handling - Future iteration

---

## Dependencies

### Prerequisite Stories
- None (independent)

### Blocking This Story
- None

### This Story Blocks
- None (independent logging system, foundation for monitoring)

### External Dependencies
- ✅ Python 3.8+ (already in backend)
- ✅ Node.js 18+ (already in frontend)
- ✅ Local filesystem access (for log storage)

---

## Technical Notes

### Local Logging Architecture

```
Backend (FastAPI)
    ↓ python-json-logger
    ↓ RotatingFileHandler (10MB, daily)
    ↓ JSON formatted logs + context
    ↓
Local File: logs/backend.log
    ├─ Index: timestamp, level, service
    ├─ Context: process_number, tribunal, request_id
    └─ Data: stack trace, args, kwargs

Frontend (React)
    ↓ Custom logger + ErrorBoundary
    ↓ Browser console + local storage
    ↓ Fetch to backend endpoint /api/logs
    ↓
Local File: logs/frontend.log
    ├─ Index: timestamp, level, component
    └─ Context: user action, URL, error details

CLI Tool: logs-view
    ↓ Queries log files
    ↓ Filters by level, process, service, time
    ↓ Output: JSON, table, summary
```

### Backend Implementation Snippet

```python
# backend/main.py
import logging
import json
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler

# Configure JSON logging
logger = logging.getLogger("backend")
logger.setLevel(logging.DEBUG)

# Rotating file handler (10MB, 7 backups)
file_handler = RotatingFileHandler(
    "logs/backend.log",
    maxBytes=10_000_000,
    backupCount=7
)
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s %(process_number)s %(tribunal)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Exception handler in FastAPI
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        extra={
            "process_number": getattr(request.state, "process_number", None),
            "tribunal": getattr(request.state, "tribunal", None),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True
    )
    raise exc
```

### Frontend Implementation Snippet

```javascript
// frontend/src/utils/logger.js
export class Logger {
    constructor(service) {
        this.service = service;
        this.logs = [];
    }

    log(level, message, context = {}) {
        const entry = {
            timestamp: new Date().toISOString(),
            level,
            service: this.service,
            message,
            ...context,
        };

        console.log(JSON.stringify(entry));
        this.logs.push(entry);

        // Send to backend when buffer reaches 10 entries
        if (this.logs.length >= 10) {
            this.flush();
        }
    }

    error(message, context) { this.log('ERROR', message, context); }
    warn(message, context) { this.log('WARN', message, context); }
    info(message, context) { this.log('INFO', message, context); }

    async flush() {
        if (this.logs.length === 0) return;
        await fetch('/api/logs', {
            method: 'POST',
            body: JSON.stringify(this.logs),
        });
        this.logs = [];
    }
}

// frontend/src/components/ErrorBoundary.jsx
class ErrorBoundary extends React.Component {
    componentDidCatch(error, errorInfo) {
        logger.error('Component error', {
            component: errorInfo.componentStack,
            error: error.toString(),
        });
    }
}
```

### Configuration (backend/config.py)

```python
class Settings(BaseSettings):
    LOG_LEVEL: str = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "logs/backend.log"
    LOG_MAX_BYTES: int = 10_000_000  # 10MB
    LOG_BACKUP_COUNT: int = 7  # Keep 7 backup files
```

### Sensitive Data Redaction

**Backend & Frontend:**
```python
# backend/utils/redact.py
import re

PATTERNS = {
    'cpf': r'\d{3}\.\d{3}\.\d{3}-\d{2}',
    'api_key': r'[a-zA-Z0-9]{40,}',
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
}

def redact_value(value):
    for pattern_name, pattern in PATTERNS.items():
        value = re.sub(pattern, f'[REDACTED-{pattern_name.upper()}]', value)
    return value

def redact_log(log_dict):
    for key, value in log_dict.items():
        if isinstance(value, str):
            log_dict[key] = redact_value(value)
    return log_dict
```

---

## Files Affected

### Modified
- `backend/requirements.txt` - Add `python-json-logger`
- `backend/config.py` - Add LOG_* settings
- `backend/main.py` - Initialize JSON logger, register exception handler
- `backend/services/process_service.py` - Add logging context (process number, tribunal)
- `backend/services/datajud.py` - Add API call logging
- `frontend/package.json` - No new packages (uses native APIs)
- `frontend/src/main.jsx` - Initialize logger, wrap App in ErrorBoundary
- `frontend/src/components/ErrorBoundary.jsx` - Add error logging
- `frontend/src/services/api.js` - Add Axios interceptor for logging
- `README.md` - Document local logging setup

### Created
- `backend/scripts/logs-view.py` - CLI tool for viewing/filtering logs (NEW)
- `backend/utils/logger.py` - Logger configuration (NEW)
- `backend/utils/redact.py` - Sensitive data redaction (NEW)
- `frontend/src/utils/logger.js` - Frontend logger utility (NEW)
- `docs/operations/logging-setup-guide.md` - Setup instructions (NEW)
- `backend/tests/test_logging.py` - Logging integration tests (NEW)

---

## Definition of Done

### Development
- [ ] `python-json-logger` instalado em backend
- [ ] JSON logger configurado em `backend/main.py`
- [ ] RotatingFileHandler setup (10MB, daily rotation)
- [ ] Exception handler middleware implementado
- [ ] Frontend logger utility criado (`frontend/src/utils/logger.js`)
- [ ] Custom context adicionado (process numbers, tribunal, request_id)
- [ ] Sensitive data redaction implementado e testado
- [ ] ErrorBoundary component criado e testado

### Backend Logger Implementation
- [ ] Logger initialized em `backend/main.py`
- [ ] JSON formatter aplicado corretamente
- [ ] Logs directory criado (`logs/`)
- [ ] Exception handler captura contexto completo
- [ ] ProcessService logging adicionado
- [ ] DataJud API logging adicionado
- [ ] Database operation logging adicionado

### Frontend Logger Implementation
- [ ] Logger utility em `frontend/src/utils/logger.js`
- [ ] ErrorBoundary integrado e funcional
- [ ] Axios interceptor com logging
- [ ] Unhandled promise rejection handler
- [ ] Log buffer flushing para backend funcional

### CLI Tool Implementation
- [ ] `backend/scripts/logs-view.py` criado
- [ ] Filtros funcionais: `--level`, `--process`, `--service`, `--time-range`
- [ ] Output formatters: JSON (default), table, summary
- [ ] Search/regex capability funcional
- [ ] Help documentation completa

### Testing & Validation
- [ ] Backend error scenarios testados (DataJud 404, DB error, custom)
- [ ] Frontend error scenarios testados (component error, async error)
- [ ] Log files criados com formato JSON correto
- [ ] Log rotation funciona (por tamanho 10MB e data)
- [ ] CLI tool retorna dados corretos
- [ ] Performance baseline <10ms per log write verificado
- [ ] Sensitive data redacted corretamente (CPF, API keys, emails)

### Documentation & Training
- [ ] `docs/operations/logging-setup-guide.md` escrito
- [ ] README.md atualizado com instruções de logging
- [ ] CLI tool help funcional (`logs-view --help`)
- [ ] Exemplos de uso documentados

### Code Quality
- [ ] Sem hardcoded paths (usar config)
- [ ] Erro handling robusto (não quebra app)
- [ ] Logging não impacta performance (<10ms)
- [ ] Testes unitários passando
- [ ] Lint/type checking passando

### Deployment
- [ ] `logs/` directory configurado em .gitignore
- [ ] Backend config com LOG_* settings funcional
- [ ] Frontend logger sem dependências externas
- [ ] Rollback plan trivial (remover imports, disable em config)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Sensitive data leakage in logs** | MEDIUM | HIGH | Implement redaction patterns, sanitize inputs |
| **Log rotation failure (disk full)** | LOW | MEDIUM | Monitor disk space, set alerts on log size |
| **Performance impact on backend** | LOW | MEDIUM | Async logging, test <10ms per write |
| **Frontend log buffer overflow** | LOW | LOW | Auto-flush on buffer full, graceful overflow |
| **Corrupted log files** | LOW | MEDIUM | Use JSON format (atomic writes), validation on read |

---

## Acceptance Testing Scenarios

### Scenario 1: Backend Error Logging (DataJud 404)
```bash
# Send invalid process number
curl http://localhost:8011/processes/00000000000000000000

# Check backend.log for entry:
cat logs/backend.log | tail -1

# Expected JSON entry:
# {
#   "timestamp": "2026-02-21T10:30:45.123Z",
#   "level": "ERROR",
#   "message": "Unhandled exception",
#   "path": "/processes/00000000000000000000",
#   "process_number": null,
#   "error_type": "InvalidProcessNumberException"
# }
```

### Scenario 2: Frontend Error Logging (Component Crash)
```bash
# Add test error button to BulkSearch component
# Click button to trigger error
# Check browser console for JSON log entry
# Check that logs/frontend.log contains the error (after buffer flush)

# Expected frontend log entry:
# {
#   "timestamp": "2026-02-21T10:31:20.456Z",
#   "level": "ERROR",
#   "service": "frontend",
#   "message": "Component error",
#   "component": "BulkSearch"
# }
```

### Scenario 3: CLI Tool Filtering
```bash
# Query logs for ERROR level only
python backend/scripts/logs-view.py --level ERROR

# Expected output: All ERROR and above messages from logs/backend.log
# Format: table or JSON depending on --format flag

# Query logs for specific process number
python backend/scripts/logs-view.py --process 1234567890 --level ERROR

# Expected output: Errors related to that process only
```

### Scenario 4: Log Rotation (Size-based)
```bash
# Generate large logs to trigger rotation
for i in {1..1000}; do
  curl http://localhost:8011/processes/invalid$i
done

# Check logs directory
ls -lah logs/

# Expected: backend.log + backend.log.1, backend.log.2, etc.
# First file = current, others = rotated backups (max 7)
```

### Scenario 5: Log Rotation (Time-based)
```bash
# Let the system run for a day
# Check logs directory at midnight

# Expected: backend.log.2026-02-21 created for previous day's logs
# Current backend.log starts fresh for new day
```

### Scenario 6: Sensitive Data Redaction
```bash
# Log a request with CPF and API key
curl http://localhost:8011/processes/123 -H "X-API-Key: sk_test_1234567890abcdef"

# Check logs/backend.log
cat logs/backend.log | grep -i "api" | head -1

# Expected: API key redacted as [REDACTED-api_key]
# CPF redacted as [REDACTED-cpf] if present
```

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Log Coverage** | 100% of unhandled exceptions | Line count in backend.log + frontend.log |
| **Write Performance** | <10ms per log entry | time.time() measurements in tests |
| **Log Rotation** | Automatic on 10MB or daily | ls -lah logs/ inspection + verify max 7 backups |
| **Data Sanitization** | 0 sensitive data in logs | grep -i "cpf\|api_key\|email" logs/backend.log (should be empty) |
| **CLI Tool Coverage** | 4+ filter options working | Test: `logs-view --level --process --service --time-range` |

---

## Change Log

- **2026-02-21:** Story created by @architect (Aria) from PLAN-001 (Sentry-based approach)
- **2026-02-21:** Refactored by @dev to structured local logging approach (user preference: no external SaaS)
- Implementation: JSON logging with RotatingFileHandler, CLI tool for viewing/filtering
- Status: Ready for @dev implementation

---

## Related Documents

- **Implementation Plan:** `docs/brownfield/plans/PLAN-001-error-monitoring.md` (originally Sentry, refactored to local logging)
- **System Architecture:** `docs/brownfield/system-architecture.md` (Section: Cross-Cutting Concerns - Logging)
- **Setup Guide:** `docs/operations/logging-setup-guide.md` (to be created)
- **CLI Tool Docs:** `backend/scripts/logs-view.py --help`

---

**Story Owner:** @dev
**Story Reviewer:** @qa
**Architect:** @architect (Aria)
**Created:** 2026-02-21
**Target Sprint:** 1 (Critical)
