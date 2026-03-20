# Secrets Management Guide

## Overview

This project uses centralized secrets management via `backend/secrets_manager.py` to keep sensitive credentials secure and prevent accidental commits of plaintext secrets to version control.

## Security Policy

### DO NOT
- ❌ Commit `.env` files to git (use `.gitignore`)
- ❌ Hardcode secrets in code
- ❌ Share secrets via chat, email, or unencrypted channels
- ❌ Log sensitive values in production
- ❌ Use weak/default credentials

### DO
- ✅ Store secrets in `.env` file (git-ignored)
- ✅ Use `.env.example` as template (no real values)
- ✅ Rotate credentials regularly
- ✅ Use environment variables for secrets
- ✅ Use SecretsManager for programmatic access

## Configuration

### 1. Setup Local Development

```bash
# Copy template
cp .env.example .env

# Fill in your actual values
# Required:
DATAJUD_API_KEY=your_actual_key_here
SENTRY_DSN=your_sentry_dsn_or_empty
```

### 2. Required Secrets

| Secret | Source | Required |
|--------|--------|----------|
| `DATAJUD_API_KEY` | DataJud CNJ API | ✅ YES |
| `DATABASE_URL` | Local SQLite | ⚠️ Optional (has default) |
| `SENTRY_DSN` | Sentry.io | ❌ NO (can be empty) |

### 3. Getting Secrets

#### DataJud API Key
1. Visit: https://www.cnj.jus.br/systpres/?pagina=datajud
2. Register for API access
3. Copy the base64-encoded key
4. Add to `.env`: `DATAJUD_API_KEY=your_key`

#### Sentry DSN (Optional)
1. Create account at https://sentry.io/
2. Create project for this app
3. Copy DSN from settings
4. Add to `.env`: `SENTRY_DSN=your_dsn`

## Usage

### In Backend Code

```python
# backend/secrets_manager.py provides multiple interfaces

# Option 1: Direct function
from backend.secrets_manager import get_secret

api_key = get_secret('DATAJUD_API_KEY')
db_url = get_secret('DATABASE_URL', default='sqlite:///./consulta_processual.db')

# Option 2: Manager instance
from backend.secrets_manager import get_secrets_manager

manager = get_secrets_manager()
api_key = manager.get_secret('DATAJUD_API_KEY')

# Option 3: Configuration
from backend.config import settings

# Settings automatically loaded from .env via python-dotenv
api_key = settings.DATAJUD_API_KEY
```

### Validation

```python
from backend.secrets_manager import validate_all_secrets

# Audit all required secrets
validation = validate_all_secrets()
# Output:
# {
#   'DATAJUD_API_KEY': True,
#   'DATABASE_URL': True,
#   'SENTRY_DSN': False
# }
```

### Run Audit

```bash
python -m backend.secrets_manager

# Output:
# === SECRETS CONFIGURATION AUDIT ===
# 
# Secrets found: 2/3
# 
# Backend: env
# Status: READY
```

## Migration from Plaintext

### Before (INSECURE)
```python
# backend/config.py
DATAJUD_API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
```

### After (SECURE)
```python
# backend/config.py - empty, loaded from .env

# backend/services/datajud.py
from backend.secrets_manager import get_secret

api_key = get_secret('DATAJUD_API_KEY')
```

## Production Deployment

### Option 1: Environment Variables (Recommended for small deployments)
```bash
# Set environment variables on server
export DATAJUD_API_KEY=your_production_key
export DATABASE_URL=postgresql://prod-db
export SENTRY_DSN=your_production_sentry_dsn

# Application reads from environment
python -m backend.main
```

### Option 2: AWS Secrets Manager (Recommended for enterprise)

Backend already supports AWS Secrets Manager:

```python
# Set backend in config
manager = get_secrets_manager(backend='aws')

# Prerequisites:
# 1. Secrets created in AWS Secrets Manager:
#    - consulta-processo/datajud-apikey
#    - consulta-processo/database-url
#    - consulta-processo/sentry-dsn

# 2. IAM role has access to secrets

# 3. AWS credentials configured on instance
```

### Option 3: HashiCorp Vault (Future)

Will be implemented in future sprints.

## Rotation

### Rotate API Keys

1. **Generate new key** in DataJud dashboard
2. **Update .env locally**: `DATAJUD_API_KEY=new_key`
3. **Test locally**: `pytest` or manual testing
4. **Update server**: Restart application or update environment variable
5. **Revoke old key** in DataJud dashboard
6. **Document**: Note rotation date in CHANGELOG

### Rotate Sentry DSN

1. Generate new DSN in Sentry project settings
2. Update `.env`: `SENTRY_DSN=new_dsn`
3. Redeploy application
4. Delete old DSN in Sentry

## Troubleshooting

### Q: Secret not found?
```python
from backend.secrets_manager import validate_all_secrets
validation = validate_all_secrets()
# Check which secrets are missing
```

### Q: How to debug secrets loading?
```bash
# Run audit
python -m backend.secrets_manager

# Check .env file exists
ls -la .env

# Verify Pydantic is loading settings
python -c "from backend.config import settings; print(settings.DATAJUD_API_KEY[:10]+'***')"
```

### Q: Secrets work locally but not on server?
- Check environment variables set on server
- Verify .env not deployed to server (should use env vars instead)
- Check IAM permissions if using AWS Secrets Manager
- Look at application logs for loading errors

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [python-dotenv Documentation](https://python-dotenv.readthedocs.io/)
- [12 Factor App - Secrets](https://12factor.net/config)
- [OWASP - Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

## Story: STORY-REM-003

**Epic:** EPIC-BROWNFIELD-REMEDIATION  
**Debit ID:** SEC-ARCH-001  
**Status:** ✅ COMPLETE

This document was created as part of STORY-REM-003 implementation.
