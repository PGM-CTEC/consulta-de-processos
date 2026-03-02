# Design: Reestruturação de Layout, Acessibilidade e Dark Mode

**Data:** 2026-03-02
**Status:** Aprovado

---

## Resumo

Quatro mudanças coordenadas no frontend para simplificar a navegação, melhorar a acessibilidade e adicionar suporte a tema claro/escuro.

---

## 1. Navegação — Reestruturação das Abas

### Estado atual (6 abas)
```
[ Consulta Individual ] [ Busca em Lote ] [ Analytics/BI ] [ Histórico ] [ Performance ] [ Configurações ]
```

### Estado após mudança (4 abas + toggle)
```
[ Consulta Individual ] [ Busca em Lote ] [ Analytics/BI ] [ Histórico ]   ☀️/🌙
```

**Mudanças:**
- Aba **Performance** removida da nav e da renderização condicional em `App.jsx`
- Aba **Configurações** removida da nav (componente `Settings.jsx` permanece, mas é acessado via drawer)
- Toggle ☀️/🌙 adicionado no canto direito do header, dentro da barra de navegação existente
- `activeTab` deixa de aceitar valores `'settings'` e `'performance'`

**Arquivos afetados:** `App.jsx`

---

## 2. Configurações de Dados SQL → Drawer no Analytics/BI

### Comportamento
- Cabeçalho do `Dashboard.jsx` ganha ícone de engrenagem ⚙️ à direita do botão "Atualizar"
- Clique abre um drawer deslizante pela direita com o conteúdo de `Settings.jsx`
- Overlay semitransparente no fundo; fechar com ✕, Escape ou clique no overlay

### Estrutura do Drawer
```
┌─────────────────────────────────┐
│ ⚙ Configurações de Dados    ✕  │
├─────────────────────────────────┤
│ ▼ Extração de Dados SQL         │
│   Driver / Host / Porta ...     │
│   Query SQL                     │
│   [ Testar Conexão ]            │
│   [ Iniciar Importação ]        │
└─────────────────────────────────┘
```

### Acessibilidade
- `<dialog>` nativo com `aria-modal="true"`, `role="dialog"`, `aria-labelledby`
- Foco aprisionado dentro do drawer enquanto aberto (focus trap)
- Fechamento via Escape

**Novo componente:** `SettingsDrawer.jsx`
**Arquivos afetados:** `Dashboard.jsx`, `Settings.jsx` (adaptado para uso sem aba)

---

## 3. Modal das 15 Fases Processuais

### Comportamento
- Botão **"? Ver fases"** aparece em:
  - `SearchProcess.jsx` — abaixo do campo de busca
  - `BulkSearch.jsx` — no cabeçalho da seção de resultados
- Clique abre modal centralizado com as 15 fases agrupadas

### Estrutura do Modal
```
┌──────────────────────────────────────────┐
│  Classificação de Fases Processuais   ✕  │
├──────────────────────────────────────────┤
│  CONHECIMENTO (01–09)                    │
│  01 Conhecimento — Antes da Sentença  🔵 │
│  02 Sentença sem Trânsito em Julgado  🔵 │
│  ... (mais 7 fases)                      │
├──────────────────────────────────────────┤
│  EXECUÇÃO (10–12, 14)                    │
│  10 Execução                          🟠 │
│  11 Execução Suspensa                 🟠 │
│  12 Execução Suspensa Parcialmente    🟠 │
│  14 Conversão em Renda                🟣 │
├──────────────────────────────────────────┤
│  OUTRAS (13, 15)                         │
│  13 Suspenso / Sobrestado             🟡 │
│  15 Arquivado Definitivamente         ⬜ │
└──────────────────────────────────────────┘
```

### Implementação
- Novo componente `PhasesReferenceModal.jsx` (reutiliza `PhaseReference.jsx` existente)
- Renderizado uma vez em `App.jsx`, controlado por estado `showPhasesModal`
- Cores de `phaseColors.js` (já existente)
- `aria-modal="true"`, foco aprisionado, fechamento por ✕ ou Escape

**Novo componente:** `PhasesReferenceModal.jsx`
**Arquivos afetados:** `App.jsx`, `SearchProcess.jsx`, `BulkSearch.jsx`

---

## 4. Dark Mode + Acessibilidade

### Estratégia: Tailwind `dark:` class

**Configuração:**
- `tailwind.config.js`: adicionar `darkMode: 'class'`
- Classe `dark` aplicada em `document.documentElement` via hook

**Novo hook:** `frontend/src/hooks/useTheme.js`
```js
// Lê settingsStore.theme, aplica/remove classe 'dark' no <html>
// Retorna { theme, toggleTheme }
```

**Toggle no header:**
- Botão ícone ☀️ (modo claro) / 🌙 (modo escuro) no canto direito da barra de nav
- `aria-label="Alternar tema"`, `aria-pressed={isDark}`
- Preferência persiste via `settingsStore` (já usa `localStorage`)

**Aplicação de `dark:` nos componentes:**

| Componente | Mudança principal |
|-----------|-----------------|
| `App.jsx` | `bg-gray-50 dark:bg-gray-900` no wrapper principal |
| Header/nav | `bg-white dark:bg-gray-800`, texto e bordas |
| `SearchProcess.jsx` | Cards e inputs com variantes dark |
| `BulkSearch.jsx` | Tabela e cards com variantes dark |
| `Dashboard.jsx` | Cards de métricas e gráficos |
| `HistoryTab.jsx` | Lista e cards |
| `ProcessDetails.jsx` | Campos e seções |
| `Settings.jsx` | Formulário e inputs |
| `PhasesReferenceModal.jsx` | Modal e badges |
| `SettingsDrawer.jsx` | Drawer e overlay |

**Acessibilidade adicional:**
- Todos os modais e drawers com focus trap e fechamento por Escape
- Toggle de tema com `aria-pressed`
- Contraste mínimo WCAG AA mantido em ambos os temas

---

## Arquivos Novos

| Arquivo | Propósito |
|---------|-----------|
| `frontend/src/hooks/useTheme.js` | Hook de tema (lê store, aplica classe no DOM) |
| `frontend/src/components/PhasesReferenceModal.jsx` | Modal das 15 fases |
| `frontend/src/components/SettingsDrawer.jsx` | Drawer de configurações SQL |

## Arquivos Modificados

| Arquivo | Mudança |
|---------|---------|
| `tailwind.config.js` | `darkMode: 'class'` |
| `App.jsx` | Remove abas, adiciona toggle, renderiza modais globais |
| `Dashboard.jsx` | Adiciona botão ⚙️, integra `SettingsDrawer` |
| `SearchProcess.jsx` | Adiciona botão "? Ver fases", dark mode |
| `BulkSearch.jsx` | Adiciona botão "? Ver fases", dark mode |
| `HistoryTab.jsx` | Dark mode |
| `ProcessDetails.jsx` | Dark mode |
| `Settings.jsx` | Adaptação para uso dentro do drawer |
| `settingsStore.js` | Já tem campo `theme` — sem mudança na estrutura |
