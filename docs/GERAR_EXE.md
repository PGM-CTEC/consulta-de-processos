# Como Gerar o Executável (.exe)

Este guia mostra como criar um arquivo `.exe` standalone para distribuir a aplicação Consulta Processual.

## ⚠️ Pré-requisitos

1. **Python 3.8+** instalado
2. **Node.js** instalado
3. **PyInstaller** instalado

## 📦 Passo 1: Instalar PyInstaller

```bash
pip install pyinstaller
```

## 🔨 Passo 2: Gerar o Executável

Execute um dos comandos abaixo na raiz do projeto:

### Opção A: Executável com Console (Recomendado para debug)

```bash
pyinstaller --onefile --icon=icon.ico --name="Consulta Processual" launcher.py
```

### Opção B: Executável sem Console (Modo Windows)

```bash
pyinstaller --onefile --noconsole --icon=icon.ico --name="Consulta Processual" launcher.py
```

### Opção C: Com todos os arquivos incluídos

```bash
pyinstaller --onefile ^
    --icon=icon.ico ^
    --name="Consulta Processual" ^
    --add-data "backend;backend" ^
    --add-data "frontend;frontend" ^
    launcher.py
```

## 📂 Localização do .exe

Após a compilação, o executável estará em:

```
dist/Consulta Processual/Consulta Processual.exe
```

## 🚀 Como Usar o Executável

1. **Copie** a pasta completa do projeto para o destino
2. **Execute** `Consulta Processual.exe`
3. Aguarde a instalação automática das dependências (primeira execução)
4. O navegador abrirá automaticamente em `http://localhost:5173`

## ⚡ Execução Mais Rápida (Sem Gerar .exe)

Se você só quer usar a aplicação localmente sem gerar um .exe, basta:

1. **Windows:** Clique duas vezes em `Iniciar Consulta Processual.bat`
2. **Linux/Mac:** Execute `python launcher.py`

## 📝 Notas Importantes

### Primeira Execução
- Na primeira vez, o launcher instalará:
  - Dependências Python (backend)
  - Dependências Node.js (frontend)
- Isso pode levar alguns minutos

### Requisitos no Computador de Destino
Mesmo com o .exe, o computador precisa ter:
- ✅ **Python 3.8+** (para rodar o backend FastAPI)
- ✅ **Node.js** (para rodar o frontend Vite)

### Alternativa: Docker (Recomendado para Produção)

Para uma distribuição mais profissional, considere usar Docker:

```dockerfile
# Dockerfile já está configurado no projeto
docker-compose up
```

Isso elimina a necessidade de instalar Python e Node.js separadamente.

## 🐛 Troubleshooting

### Erro: "Python não encontrado"
- Instale Python de https://www.python.org/downloads/
- Marque a opção "Add Python to PATH" durante a instalação

### Erro: "Node.js não encontrado"
- Instale Node.js de https://nodejs.org/
- Reinicie o terminal após a instalação

### Erro: "PyInstaller não encontrado"
```bash
pip install --upgrade pyinstaller
```

### O .exe não funciona
- Verifique se todos os arquivos do projeto estão na mesma pasta
- Execute com console (`--noconsole` removido) para ver erros
- Certifique-se que Python e Node.js estão instalados

## 📊 Tamanho do Executável

- **Executável sozinho:** ~10-15 MB
- **Com dependências Python:** ~50-100 MB
- **Projeto completo:** ~200-300 MB (inclui node_modules)

## 🔐 Assinatura Digital (Opcional)

Para distribuição profissional, assine o executável:

```bash
signtool sign /f certificado.pfx /p senha /t http://timestamp.digicert.com "Consulta Processual.exe"
```

## 📦 Criar Instalador (Avançado)

Use **Inno Setup** ou **NSIS** para criar um instalador profissional:

```bash
# Instalar Inno Setup
# Criar script .iss
# Compilar instalador
```

---

**Dica:** Para uso pessoal, o arquivo `.bat` é mais simples e rápido que gerar um .exe!
