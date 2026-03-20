# Authentication Decision Document — REM-027

**Data:** 2026-02-27
**Autor:** @dev
**Status:** DECIDED — NO-GO (Defer)

---

## Requirements

- **Application type:** INTERNAL TOOL (PGM-Rio — Procuradoria Geral do Município)
- **Expected users:** 1-50 (advogados e servidores internos)
- **Network protection:** Acesso via rede interna / VPN corporativa
- **User management needed:** NO (para o escopo atual)
- **Public internet exposure:** NO

---

## Decision: NO-GO (Defer Authentication)

### Rationale

O sistema é uma ferramenta interna da PGM-Rio, acessada exclusivamente por usuários
autenticados na rede da prefeitura. O controle de acesso é feito no nível de infraestrutura
(VPN, firewall, proxy reverso). Implementar autenticação na aplicação seria over-engineering
para o escopo atual.

### Condições para Revisão

Esta decisão deve ser revisitada se:
1. O sistema for exposto à internet pública
2. Houver necessidade de rastreabilidade por usuário (LGPD — Audit Trail já usa `user_id=null`)
3. Diferentes níveis de permissão forem requeridos

---

## Security Implications

- **IP whitelisting** deve ser configurado no proxy reverso (nginx/load balancer)
- **VPN** obrigatória para acesso externo
- O campo `user_id` no `AuditLog` (REM-026) está preparado para receber JWT claims no futuro
- Rate limiting já implementado via `slowapi` (config: `RATE_LIMIT_ENABLED`)

---

## Recommended Approach (Quando Necessário)

Se NO-GO for revertido, abordagem recomendada:
- **FastAPI-Users** (batteries-included, JWT + OAuth2)
- User model: `username`, `email`, `password_hash` (bcrypt), `is_active`, `role`
- Token expiration: 8h access token, 7d refresh token
- Integration: passar `user_id` para `AuditLog` via middleware

---

## Config Atual

```python
# backend/config.py
REQUIRE_AUTH: bool = False   # Alterar para True quando implementar
VALID_API_KEYS: str = ""     # API keys simples como stepping stone
```
