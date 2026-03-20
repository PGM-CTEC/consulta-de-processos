# E2E Tests with Playwright

Testes end-to-end para o sistema de Consulta de Processos utilizando Playwright.

## 📋 Cobertura de Testes

### ✅ Test 1: Single Process Search Flow
**Arquivo:** `single-search-flow.spec.ts`

Testa o fluxo completo de busca individual:
- Navegação até a página de busca
- Preenchimento do número CNJ
- Busca e visualização de detalhes do processo
- Visualização da timeline de movimentações
- Exportação para JSON

**Casos de teste:**
- ✅ Busca bem-sucedida com visualização e export
- ✅ Tratamento de número CNJ inválido
- ✅ Tratamento de erros de API

### ✅ Test 2: Bulk Process Search Flow
**Arquivo:** `bulk-search-flow.spec.ts`

Testa o fluxo de busca em lote:
- Busca manual (textarea com múltiplos números)
- Upload de arquivo CSV
- Visualização de resultados em tabela
- Exportação de resultados para CSV

**Casos de teste:**
- ✅ Busca em lote via input manual
- ✅ Busca em lote via upload de CSV
- ✅ Indicador de progresso durante busca
- ✅ Tratamento de números mistos (válidos/inválidos)

### ✅ Test 3: Dashboard Analytics Flow
**Arquivo:** `dashboard-flow.spec.ts`

Testa o dashboard de analytics:
- Visualização de estatísticas (total de processos, movimentações)
- Visualização de gráficos (tribunais, fases)
- Filtro por tribunal
- Atualização de dados

**Casos de teste:**
- ✅ Exibição completa do dashboard
- ✅ Filtro por tribunal
- ✅ Distribuição por fases
- ✅ Distribuição por tribunais
- ✅ Estado vazio (sem dados)
- ✅ Tratamento de erros de API
- ✅ Atualização de dados

## 🚀 Como Executar

### Pré-requisitos

1. **Backend rodando:**
   ```bash
   cd backend
   python main.py
   ```
   Backend deve estar disponível em `http://localhost:8000`

2. **Dependências instaladas:**
   ```bash
   cd frontend
   npm install
   ```

### Comandos Disponíveis

```bash
# Rodar todos os testes E2E
npm run test:e2e

# Rodar testes com UI interativa
npm run test:e2e:ui

# Rodar testes com browser visível (headed mode)
npm run test:e2e:headed

# Rodar testes em modo debug
npm run test:e2e:debug

# Rodar teste específico
npx playwright test single-search-flow

# Rodar teste específico em modo debug
npx playwright test single-search-flow --debug
```

### Rodar com Backend Mock

Se não quiser rodar o backend real, pode usar mocks:

```bash
# Os testes já incluem mocks para cenários de erro
# Para mockar respostas de sucesso, modifique os testes com page.route()
```

## 📊 Relatórios

### HTML Report

Após rodar os testes, visualize o relatório HTML:

```bash
npx playwright show-report
```

### Screenshots on Failure

Screenshots são capturadas automaticamente quando um teste falha.
Localização: `test-results/`

### Videos

Vídeos são gravados quando testes falham (configurado para `retain-on-failure`).
Localização: `test-results/`

## 🔧 Configuração

### playwright.config.ts

Principais configurações:
- **baseURL:** `http://localhost:5173` (Vite dev server)
- **Timeout:** Testes com timeout generoso para APIs
- **Screenshots:** `only-on-failure`
- **Videos:** `retain-on-failure`
- **Browsers:** Chromium (default), Firefox e WebKit disponíveis

### Modificar Configuração

Para habilitar mais browsers, edite `playwright.config.ts`:

```typescript
projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
],
```

## 🧪 CI/CD Integration

### GitHub Actions

Workflow configurado em `.github/workflows/e2e-tests.yml`

**Triggers:**
- Push para `main` ou `develop`
- Pull requests para `main` ou `develop`

**Artifacts:**
- Relatório HTML (retention: 30 dias)
- Screenshots de falhas (retention: 7 dias)
- Vídeos de falhas (retention: 7 dias)

## 📝 Boas Práticas

### Seletores

Prioridade de seletores:
1. **data-testid** (ideal, mas não implementado ainda)
2. **text content** (mais resiliente)
3. **aria-labels** (acessibilidade)
4. **CSS selectors** (último recurso)

### Timeouts

- Use `{ timeout: 10000 }` para operações de API
- Use `{ timeout: 30000 }` para bulk operations
- Use `page.waitForLoadState('networkidle')` para aguardar requests

### Mock vs Real API

- **Testes de erro:** Use mocks (`page.route()`)
- **Testes de sucesso:** Prefira API real quando possível
- **CI:** Configure ambiente completo (backend + frontend)

## 🐛 Troubleshooting

### Erro: "Browser not found"

```bash
npx playwright install chromium
```

### Erro: "Timeout waiting for element"

- Verifique se backend está rodando
- Aumente timeout nos testes
- Use `--headed` para ver o que está acontecendo

### Erro: "Connection refused"

- Backend não está rodando em `localhost:8000`
- Frontend não está rodando em `localhost:5173`
- Verifique portas em uso: `netstat -ano | findstr :8000`

## 📚 Referências

- [Playwright Documentation](https://playwright.dev)
- [Testing Best Practices](https://playwright.dev/docs/best-practices)
- [STORY-REM-018](../../docs/stories/STORY-REM-018.md) - Epic Story
