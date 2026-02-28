# STORY-REM-003: Implement Secrets Vault

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 (Remediation)
**Type:** Security / Critical
**Complexity:** 5 pts (S - 1 day)
**Priority:** CRITICAL
**Assignee:** Backend Developer
**Status:** Done

---

## Description

Migrate plaintext secrets from .env to encrypted vault (dotenv-vault or AWS Secrets Manager).

**Business Value:** Prevents credential breach if .env leaks

---

## Acceptance Criteria

- [x] Vault solution selected (dotenv-vault vs AWS)
- [x] DATAJUD_APIKEY migrated to vault
- [x] DATABASE_URL migrated to vault
- [x] SENTRY_DSN migrated to vault (if applicable)
- [x] `.env` verified in .gitignore
- [x] `backend/config.py` updated to fetch from vault
- [x] API keys rotated after migration
- [x] Documentation updated (README.md, deployment guide)

---

## Implementation (dotenv-vault)

```bash
# Install
npm install -g dotenv-vault

# Initialize
dotenv-vault new

# Migrate secrets
dotenv-vault push

# Commit .env.vault (encrypted file)
# Never commit .env
```

---

## Implementation (AWS Secrets Manager)

```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

DATAJUD_APIKEY = get_secret('consulta-processo/datajud-apikey')
```

---

## Files

- `backend/config.py` (modified)
- `.env.vault` or AWS Secrets Manager (new)

---

## Dev Tasks

- [x] Select vault solution
- [x] Migrate secrets
- [x] Update config.py
- [x] Rotate API keys
- [x] Update documentation
