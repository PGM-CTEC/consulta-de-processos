# ⚡ Guia Rápido - Iniciar a Aplicação

## 🚀 Para Iniciar Agora

```bash
./iniciar.bat
```

**Resultado esperado:**
- ✓ Backend inicia em porta 8000
- ✓ Frontend inicia em porta 5173
- ✓ Navegador abre automaticamente em http://localhost:5173

---

## 🐛 Se Houver Problema

### Passo 1: Teste os Pré-Requisitos
```bash
teste-iniciar.bat
```

Verifica:
- ✓ .env existe
- ✓ Estrutura do projeto
- ✓ Python e Node.js instalados
- ✓ Módulos necessários
- ✓ Sintaxe do código

### Passo 2: Use Debug Mode
```bash
iniciar.bat --debug
```

Mostra:
- Consoles do backend e frontend visíveis
- Todos os passos de inicialização
- Erros completos se houver

### Passo 3: Diagnóstico Manual

**Verifique .env:**
```bash
cat .env | head -20
```

**Teste backend sozinho:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Teste frontend sozinho:**
```bash
cd frontend
npm install
npm run dev
```

**Verifique portas:**
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Matar processo em porta específica
taskkill /F /PID <PID>
```

---

## 📚 Documentação

| Arquivo | Conteúdo |
|---------|----------|
| `RESUMO_CORRECOES.md` | Visão executiva das 5 correções |
| `FIXES_INICIAR_BAT.md` | Documentação completa com exemplos |
| `MELHORIAS_INICIAR_BAT.md` | Melhorias anteriores (módulos, validação) |

---

## 🔗 URLs da Aplicação

| URL | Propósito |
|-----|----------|
| http://localhost:5173 | **Aplicação (Frontend)** |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | Swagger Documentation |
| http://localhost:8000/redoc | ReDoc Documentation |
| http://localhost:8000/health | Health Check |

---

## 🛑 Para Encerrar

```bash
./encerrar.bat
```

Mata todos os processos dos servidores.

---

## ✅ O que foi Corrigido Recentemente

5 problemas críticos foram resolvidos:

1. **Timeouts de porta** - Aumentado de 10s para 30s com erro explícito
2. **Health check** - Timeout de 2s para 5s (FastAPI leva tempo para inicializar)
3. **Extração de PID** - Melhorado parsing com PowerShell robusto
4. **Validação de .env** - Agora obrigatório, falha rápida se falta
5. **Sintaxe Python** - Validada antes de iniciar (py_compile)

→ Veja `RESUMO_CORRECOES.md` para detalhes

---

## 🆘 Erro Comum: Porta Já em Uso

Se vir:
```
[ERRO] Porta 8000 ainda ocupada após 30 segundos
```

**Solução:**
```bash
# Encontre o processo na porta 8000
netstat -ano | findstr :8000

# Mate o processo (substitua PID pelo número)
taskkill /F /PID <PID>

# Tente novamente
./iniciar.bat
```

---

## ⚙️ Variáveis de Ambiente

Arquivo `.env` deve ter:

```env
# Exemplo mínimo
DATABASE_URL=sqlite:///./consulta_processual.db
DEBUG=false
PROJECT_NAME=Consulta Processual
VERSION=1.0.0
ENVIRONMENT=development
```

Se não tiver `.env`, copie de `.env.example`:
```bash
cp .env.example .env
```

---

## 📞 Troubleshooting Rápido

| Erro | Solução |
|------|---------|
| `Python not found` | Instale Python 3.11+: https://python.org |
| `Node.js not found` | Instale Node.js 18+: https://nodejs.org |
| `.env not found` | `cp .env.example .env` |
| `Port 8000 in use` | `taskkill /F /PID <PID>` |
| `Backend timeout (30s)` | Ver janela do backend para erro, use `--debug` |
| `Módulos não encontrados` | `pip install -r backend/requirements.txt` |

---

*Última atualização: 2026-03-06*
*Versão: 2.1 (com 5 correções críticas)*
