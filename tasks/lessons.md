# Lessons Learned - Consulta Processo

## Backend

### 1. Dependências do Ambiente Virtual (.venv)

- **Problema**: O backend falhava ao iniciar com `ModuleNotFoundError: No module named 'pythonjsonlogger'`.
- **Causa**: O pacote `python-json-logger` estava no `requirements.txt` mas não foi instalado no ambiente virtual local.
- **Solução**: Executar `pip install python-json-logger` no ambiente correto.

### 2. Contexto de Execução e Imports Relativos

- **Problema**: `ImportError: attempted relative import with no known parent package`.
- **Causa**: Tentar rodar o `uvicorn` de dentro da pasta `backend` (`python -m uvicorn main:app`) quando o código usa imports relativos como `from .database import ...`.
- **Solução**: O servidor deve ser executado a partir da raiz do projeto como um módulo: `python -m uvicorn backend.main:app`. Isso permite que o Python resolva o ponto (`.`) em relação ao pacote `backend`.

### 3. Integração com DataJud

- **Problema**: Mensagem de "API KEY pública do datajud não disponibilizada".
- **Causa**: A chave pública do CNJ não estava configurada nas variáveis de ambiente nem no código.
- **Solução**: Hardcoded a chave pública `cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==` em `backend/config.py` e adicionei ao `.env` para garantir disponibilidade imediata sem exigir configuração manual do usuário.
