# 🚀 Consulta Processual - Guia de Uso Rápido

## 📦 3 Formas de Usar

### 🟢 Opção 1: Launcher Simples (Recomendado)

**Windows:**
```
Clique duas vezes em: "Iniciar Consulta Processual.bat"
```

**Linux/Mac:**
```bash
python launcher.py
```

✅ **Vantagens:**
- Não precisa configurar nada
- Instala dependências automaticamente
- Abre navegador automaticamente
- Mais rápido que gerar .exe

---

### 🔵 Opção 2: Gerar Executável (.exe)

**Gerar o executável:**
```
Clique duas vezes em: "gerar_exe.bat"
```

Ou via linha de comando:
```bash
pip install pyinstaller
pyinstaller launcher.spec
```

**Executável gerado em:**
```
dist/Consulta Processual/Consulta Processual.exe
```

✅ **Vantagens:**
- Parece mais profissional
- Pode criar atalho na área de trabalho
- Distribuição mais fácil para usuários finais

⚠️ **Importante:**
- O .exe **NÃO** é standalone completo
- Ainda precisa de Python e Node.js instalados
- Precisa da pasta completa do projeto junto

---

### 🟡 Opção 3: Manual (Para desenvolvedores)

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8010
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Abrir navegador:**
```
http://localhost:5173
```

---

## ⚙️ Como Funciona o Launcher

```
┌─────────────────────────────────────────────┐
│  1. Verifica Python 3.8+                   │
│  2. Verifica Node.js                        │
│  3. Instala pip packages (backend)          │
│  4. Instala npm packages (frontend)         │
│  5. Inicia FastAPI (backend - porta 8010)  │
│  6. Inicia Vite (frontend - porta 5173)    │
│  7. Abre navegador automaticamente          │
│  8. Monitora processos                      │
└─────────────────────────────────────────────┘
```

**Tempo de execução:**
- Primeira vez: ~2-5 minutos (instala tudo)
- Próximas vezes: ~10 segundos

---

## 📋 Pré-requisitos

| Software | Versão | Download |
|----------|--------|----------|
| Python | 3.8+ | https://python.org/downloads/ |
| Node.js | 16+ LTS | https://nodejs.org/ |
| pip | (vem com Python) | - |
| npm | (vem com Node.js) | - |

**Instalação Python:**
- ✅ Marque "Add Python to PATH"
- ✅ Selecione "Install for all users"

**Instalação Node.js:**
- ✅ Use a versão LTS (Long Term Support)
- ✅ Instale com as opções padrão

---

## 🎯 Primeiro Uso

### Passo 1: Verificar Instalações

**Windows:**
```cmd
python --version
node --version
```

**Deve retornar:**
```
Python 3.8.x (ou superior)
v16.x.x (ou superior)
```

### Passo 2: Executar Launcher

**Clique em:** `Iniciar Consulta Processual.bat`

**Você verá:**
```
============================================================
     CONSULTA PROCESSUAL - Sistema DataJud
============================================================

[1/6] Verificando Python...
✓ Python 3.13.9 encontrado

[2/6] Verificando Node.js...
✓ Node.js v20.11.0 encontrado

[3/6] Instalando dependências do backend...
✓ Dependências do backend instaladas

[4/6] Instalando dependências do frontend...
✓ Dependências do frontend instaladas

[5/6] Iniciando servidor backend...
✓ Backend rodando em http://127.0.0.1:8010

[6/6] Iniciando servidor frontend...
✓ Frontend rodando em http://localhost:5173

============================================================
✓ APLICAÇÃO INICIADA COM SUCESSO!
============================================================

Abrindo navegador em: http://localhost:5173
```

### Passo 3: Usar a Aplicação

O navegador abrirá automaticamente em:
```
http://localhost:5173
```

---

## 🛑 Como Encerrar

- **Opção 1:** Feche a janela do console
- **Opção 2:** Pressione `Ctrl+C` no console
- **Opção 3 (Windows):** Clique no X da janela

**O que acontece:**
```
Encerrando aplicação...
  Parando backend...
  Parando frontend...

✓ Aplicação encerrada com sucesso!
```

---

## 🐛 Solução de Problemas

### ❌ "Python não encontrado"

**Solução:**
1. Instale Python de https://python.org/downloads/
2. **IMPORTANTE:** Marque "Add Python to PATH"
3. Reinicie o terminal
4. Teste: `python --version`

### ❌ "Node.js não encontrado"

**Solução:**
1. Instale Node.js de https://nodejs.org/
2. Use a versão LTS (recomendada)
3. Reinicie o terminal
4. Teste: `node --version`

### ❌ "Porta já em uso"

**Causa:** Já existe uma instância rodando

**Solução Windows:**
```cmd
netstat -ano | findstr "8010"
netstat -ano | findstr "5173"
taskkill /PID [número_do_processo] /F
```

**Solução Linux/Mac:**
```bash
lsof -i :8010
lsof -i :5173
kill [PID]
```

### ❌ "Erro ao instalar dependências"

**Solução:**
```bash
# Backend
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules
npm cache clean --force
npm install
```

### ❌ "Frontend não abre no navegador"

**Solução:**
1. Aguarde 10-15 segundos após iniciar
2. Abra manualmente: http://localhost:5173
3. Verifique se a porta 5173 está livre

### ❌ "Backend com erro de importação"

**Solução:**
```bash
cd backend
pip install pydantic-settings
pip install --upgrade fastapi uvicorn
```

---

## 📊 Estrutura de Arquivos

```
Consulta processo/
│
├── 📄 Iniciar Consulta Processual.bat  ← CLIQUE AQUI (Windows)
├── 📄 launcher.py                       ← Script principal
├── 📄 gerar_exe.bat                     ← Gerar executável
├── 📄 launcher.spec                     ← Config PyInstaller
│
├── 📁 backend/                          ← API FastAPI
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── 📁 frontend/                         ← Interface React
│   ├── package.json
│   ├── src/
│   └── ...
│
└── 📁 dist/                             ← Executável (após gerar)
    └── Consulta Processual.exe
```

---

## 🔧 Configurações Avançadas

### Mudar Portas

Edite `launcher.py`:
```python
BACKEND_PORT = 8010   # Mude aqui
FRONTEND_PORT = 5173  # Mude aqui
```

### Desabilitar Abertura Automática do Navegador

Edite `launcher.py`, método `open_browser()`:
```python
def open_browser(self):
    print(f"\nAplicação disponível em: {FRONTEND_URL}")
    # webbrowser.open(FRONTEND_URL)  # Comente esta linha
```

### Executar em Modo Desenvolvimento

```bash
# Backend com reload automático
cd backend
uvicorn main:app --reload --port 8010

# Frontend com HMR
cd frontend
npm run dev
```

---

## 📦 Distribuição para Outros Computadores

### Opção A: Copiar Pasta Completa

1. Copie toda a pasta `Consulta processo`
2. Certifique-se que Python e Node.js estão instalados
3. Execute `Iniciar Consulta Processual.bat`

### Opção B: Gerar Instalador (Avançado)

Use **Inno Setup** ou **NSIS**:

1. Gere o .exe com `gerar_exe.bat`
2. Crie script de instalador (.iss para Inno Setup)
3. Inclua Python e Node.js no instalador
4. Compile o instalador

---

## 🎨 Personalização

### Adicionar Ícone Customizado

1. Crie um arquivo `icon.ico` (256x256)
2. Coloque na raiz do projeto
3. Regenere o .exe com `gerar_exe.bat`

### Mudar Título da Janela

Edite `launcher.py`:
```python
def print_header(self):
    print("=" * 60)
    print("     SEU TÍTULO AQUI")  # Mude aqui
    print("=" * 60)
```

---

## 📚 Mais Informações

- **Guia de Testes:** `TESTING.md`
- **Gerar .exe detalhado:** `GERAR_EXE.md`
- **Início Rápido:** `INICIAR_AQUI.txt`
- **Backend API:** `backend/README.md`
- **Frontend UI:** `frontend/README.md`

---

## ✅ Checklist de Validação

Antes de distribuir, verifique:

- [ ] Python 3.8+ instalado
- [ ] Node.js instalado
- [ ] `launcher.py` funciona corretamente
- [ ] `Iniciar Consulta Processual.bat` abre a aplicação
- [ ] Backend responde em http://127.0.0.1:8010/docs
- [ ] Frontend carrega em http://localhost:5173
- [ ] Navegador abre automaticamente
- [ ] Testes passando: `pytest backend/tests/ -v`
- [ ] Sem erros no console do navegador

---

**🎉 Pronto! Sua aplicação está pronta para uso!**
