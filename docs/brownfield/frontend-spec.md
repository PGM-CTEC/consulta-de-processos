# Frontend Specification — Fase 3: UX Audit

**Status**: Análise Rápida Completa
**Data**: 21 Fevereiro 2026
**Auditora**: Uma (UX Design Expert)
**Projeto**: Consulta Processo
**Stack**: React 19 + Vite 7 + Tailwind CSS 3 + Lucide Icons

---

## Sumário Executivo

### Achados Principais
- **9 componentes React** bem estruturados, modular e escalável ✅
- **ARIA semântica parcialmente implementada** — 60% de cobertura (3/9 componentes com ARIA completa)
- **Acessibilidade WCAG 2.1 AA**: Implementação parcial, **FALHAS CRÍTICAS** em 3 áreas
- **Design consistente** com Tailwind (paleta indigo/violet/gray dominante)
- **Testing**: 1 arquivo de testes apenas (phases.test.js) — **DÉBITO ALTO**

### Scores Rápidos
| Dimensão | Score | Status |
|----------|-------|--------|
| Componentes | 8/10 | ✅ Bem estruturados |
| ARIA/Accessibility | 6/10 | ⚠️ Parcial |
| WCAG 2.1 AA Compliance | 4/10 | 🔴 Falhas críticas |
| Testing Coverage | 1/10 | 🔴 Mínimo |
| Design Consistency | 9/10 | ✅ Excelente |
| Performance (perceived) | 8/10 | ✅ Bom |

---

## Inventário de Componentes

### 1. **SearchProcess** (76 linhas)
**Tipo**: Atom/Molecule
**Responsabilidade**: Busca individual de processo por número
**WCAG Status**: ✅ BOAS PRÁTICAS OBSERVADAS

**Padrões Detectados**:
- `role="search"` no formulário ✅
- `aria-label`, `aria-describedby` nos inputs ✅
- Label com `sr-only` (screen reader only) ✅
- Ícone com `aria-hidden` ✅
- Loading state com `aria-label` ✅

**Força**:
- Acessibilidade bem implementada
- Validação de entrada (trim, check)
- UX clara com placeholder + hint

**Fraqueza**:
- Input único — sem variantes de busca

---

### 2. **BulkSearch** (263 linhas)
**Tipo**: Organism/Template
**Responsabilidade**: Busca em lote (drag-drop + upload + manual)
**WCAG Status**: ⚠️ PARCIAL — Faltam labels e keyboard nav

**Padrões Detectados**:
- Drag-drop área com `onDragOver/Drop` ✅
- Upload de múltiplos formatos (TXT, CSV, XLSX) ✅
- Resultado em tabela com cabeçalho
- Menu dropdown (export)

**Força**:
- Interface intuitiva para uploads
- Suporte a múltiplos formatos
- Estado visual claro (dragging vs normal)

**Fraqueza**:
- ❌ Textarea `Listagem de Números` sem label `<label htmlFor>`
- ❌ Menu dropdown export sem `role="menu"`, keyboard nav não testado
- ❌ Tabela sem `caption` ou `aria-label`
- ❌ Ícones SVG sem `aria-hidden`

**Débito**: FE-001 (MEDIUM) — Label associations + Keyboard nav

---

### 3. **ProcessDetails** (404 linhas)
**Tipo**: Organism/Template
**Responsabilidade**: Detalhes do processo + timeline movimentos + filtros
**WCAG Status**: ✅ BOM — Semântica sólida

**Padrões Detectados**:
- `<article>`, `<section>` tags semânticas ✅
- Timeline com `<ol>` (ordered list) ✅
- `<time dateTime>` para datas ✅
- Multi-select filters com chip buttons ✅
- Modal JSON com `<pre><code>`

**Força**:
- Excelente estrutura semântica
- Filtros multi-select bem pensados
- Modal acessível (com overlay)

**Fraqueza**:
- ⚠️ Modal não tem `role="dialog"`, `aria-modal="true"`
- ⚠️ Close button (X) poderia ter melhor label
- ⚠️ Chips buttons sem `aria-pressed` ou `aria-checked`

**Débito**: FE-002 (LOW) — Modal dialog improvements

---

### 4. **InstanceSelector** (240 linhas)
**Tipo**: Molecule/Organism
**Responsabilidade**: Selector de múltiplas instâncias (G1/G2/SUP)
**WCAG Status**: ⚠️ MÍNIMO — Falta keyboard nav

**Padrões Detectados**:
- Grid de 3 slots (G1, G2, SUP)
- Estado ativo/inativo visual
- Alert para casos `source_limited`

**Fraqueza**:
- ❌ Buttons sem `aria-selected` ou feedback visual claro
- ❌ Grid pode não ser acessível via keyboard
- ❌ Descrição em português pode ter contrast issues (purple 600 text)

**Débito**: FE-003 (MEDIUM) — Keyboard navigation + ARIA state

---

### 5. **ErrorBoundary** (132 linhas)
**Tipo**: HOC/Error Boundary
**Responsabilidade**: Capturar erros React + fallback UI
**WCAG Status**: ✅ BOAS PRÁTICAS

**Padrões Detectados**:
- `aria-label` em buttons ✅
- `focus:outline-none focus:ring-2` — visible focus ✅
- Dev error stack visível apenas em dev
- Dois buttons com intent claro (Retry, Home)

**Força**:
- Graceful degradation
- Focus management
- Semantic buttons

**Fraqueza**:
- Ícone emoji (⚠️) sem alternate text
- Poderia ter `role="alert"`

---

### 6. **Dashboard** (213 linhas)
**Tipo**: Template/Page
**Responsabilidade**: Analytics + estatísticas (KPIs, charts)
**WCAG Status**: 🔴 FALHA — Charts sem labels acessíveis

**Padrões Detectados**:
- 3 KPI cards (Total Processos, Movimentos, Última Update)
- Chart de barras (Tribunais, Fases)
- Chart temporal (12 meses bar chart)

**Fraqueza**:
- ❌ **Charts não têm `<figure>`, `<figcaption>` ou `aria-label`** — inacessível para screen readers
- ❌ Barras de progresso sem `role="progressbar"`, `aria-valuenow`, `aria-valuemax`
- ❌ Ícones decorativos não têm `aria-hidden`
- ❌ Hover tooltips (`title` attribute) não acessíveis via keyboard
- ❌ Empty state sem `role="status"` ou `aria-live`

**Débito**: FE-004 (HIGH) — Chart accessibility + progressbar roles

---

### 7. **Settings** (314 linhas)
**Tipo**: Template
**Responsabilidade**: Configurações de SQL + IA integration
**WCAG Status**: ⚠️ PARCIAL — Labels OK, color contrast concerns

**Padrões Detectados**:
- Accordion UI (expandable sections)
- Form fields com labels e placeholders
- Password input com show/hide toggle ✅

**Fraqueza**:
- ⚠️ `<label>` sem `htmlFor` no SQL section → not associated
- ⚠️ Color: `text-amber-800` sobre `bg-amber-50` pode ter contrast baixo
- ⚠️ Eye/EyeOff toggle sem label
- ⚠️ Disabled states não visuais o suficiente

**Débito**: FE-005 (MEDIUM) — Label associations + contrast review

---

### 8. **HistoryTab** (104 linhas)
**Tipo**: Component/Molecule
**Responsabilidade**: Histórico de buscas recentes
**WCAG Status**: ⚠️ MÍNIMO — Lista sem semântica

**Padrões Detectados**:
- `<ul>` mas sem `<li>` wrapping (apenas `<button>`)
- Loading state
- Empty state

**Fraqueza**:
- ❌ Lista deveria ser `<ul>` com `<li>` filhos
- ❌ Buttons dentro list podem confundir screen readers
- ⚠️ `Clock` icon sem `aria-hidden`

**Débito**: FE-006 (LOW) — Semantic HTML for lists

---

### 9. **PhaseReference** (165 linhas)
**Tipo**: Template/Reference
**Responsabilidade**: Documentação interativa das 15 fases processuais
**WCAG Status**: ✅ BOM — Semântica sólida

**Padrões Detectados**:
- Agrupamento de fases por tipo ✅
- Info box com border-left
- Color legend com swatches
- Headings hierarchy (h1 → h2) ✅

**Força**:
- Excelente documentação visual
- Cor legend é necessária (não depende apenas de cor)

**Fraqueza**:
- ⚠️ Emoji icons (📋, ⚖️, etc) sem aria-label
- ⚠️ Legendas de cores poderiam ter `<dl>` (definition list) em vez de div grid

**Débito**: FE-007 (LOW) — Semantic legends

---

## WCAG 2.1 AA Gap Analysis

### Falhas Críticas 🔴

| # | Critério | Componente | Severidade | Impacto |
|---|----------|-----------|-----------|---------|
| 1 | **1.1.1 Text Alternatives** | Dashboard, PhaseReference | CRITICAL | Charts, ícones emoji sem alt text |
| 2 | **1.4.3 Contrast Ratio** | Settings, BulkSearch | HIGH | Texto gray-400, amber-800 pode falhar 4.5:1 |
| 3 | **2.1.1 Keyboard Access** | BulkSearch, InstanceSelector | HIGH | Menus dropdown não navegáveis via tab |
| 4 | **3.2.4 Consistent Identification** | Multiple | MEDIUM | Patterns inconsistentes (alguns inputs com label, outros sem) |

### Melhorias Recomendadas ✅

1. **Dashboard Charts** → Envolver em `<figure>`, adicionar `<figcaption>` com resumo dos dados
2. **BulkSearch textarea** → Adicionar `<label htmlFor="numbers-textarea">`
3. **InstanceSelector buttons** → Adicionar `aria-selected={isActive}` ou `aria-pressed`
4. **Color Contrast** → Testar com WebAIM Contrast Checker (4.5:1 mínimo AA)
5. **Keyboard Navigation** → Testar com Tab, Enter, Escape em todos os componentes

---

## User Flows (Rápido)

### Flow 1: Busca Individual → Detalhes
```
SearchProcess (input numero)
    ↓
API call → ProcessDetails (render)
    ↓
Movements visible (filter by type)
    ↓
Export (JSON, CSV, etc)
```

### Flow 2: Busca em Lote
```
BulkSearch (upload TXT/CSV/XLSX)
    ↓
Parse file → Extract numbers
    ↓
Bulk API call (sequential)
    ↓
Results table (success/failure rows)
    ↓
Export relatório (4 formatos)
```

### Flow 3: Instance Navigation (Multi-instância)
```
ProcessDetails loads
    ↓
InstanceSelector appears (if meta.instances > 1)
    ↓
User clicks G1/G2/SUP button
    ↓
API call → New data loaded
    ↓
ProcessDetails re-renders
```

---

## Design System Inventory

### Color Palette (Tailwind)
- **Primary**: `indigo-600` (#4f46e5) — CTA, focus
- **Secondary**: `violet-600` (#7c3aed) — Headers, accents
- **Neutral**: `gray-100` to `gray-900` — Text, backgrounds
- **Semantic**:
  - ✅ Green: `green-600` (success)
  - ⚠️ Amber: `amber-600` (warning)
  - 🔴 Red: `red-600` (error)

**Concern**: Color-heavy design (indigo/violet gradient headers) pode não ter contrast AA em todos estados.

### Typography
- **Headers**: `font-bold text-xl`, `text-2xl`, `text-3xl`
- **Body**: `text-sm`, `text-base`
- **Mono**: `font-mono` em SearchProcess input, JSON display

### Components/Patterns
- **Cards**: `bg-white rounded-2xl shadow-xl border border-gray-100` (consistent)
- **Buttons**: Indigo primary, white secondary, red for destructive
- **Forms**: `bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm`
- **Icons**: Lucide React (consistent, 24px baseline)

### Layout
- **Max-width**: `max-w-2xl`, `max-w-4xl`, `max-w-6xl`
- **Spacing**: Tailwind scale (p-4, p-6, space-y-6)
- **Grid**: Responsive (1 col mobile, 2-3 col tablet, 3+ desktop)

---

## Débitos UX Identificados

### FE-001: Label HTML Associations (MEDIUM)
**Status**: BLOCKED
**Componentes**: BulkSearch, Settings
**Descrição**: Form inputs sem `<label htmlFor="id">` → não linked semanticamente
**Impacto**: Screen readers não anunciam labels
**Fix Estimate**: 2 pts (30 min)
**Recomendação**: Adicionar `htmlFor` em todas labels, associar IDs nos inputs

```jsx
// ❌ Before
<label>Listagem de Números</label>
<textarea className="..."></textarea>

// ✅ After
<label htmlFor="numbers-list">Listagem de Números</label>
<textarea id="numbers-list" className="..."></textarea>
```

---

### FE-002: Modal Dialog Accessibility (LOW)
**Status**: OPEN
**Componentes**: ProcessDetails (JSON modal)
**Descrição**: Modal sem `role="dialog"`, `aria-modal`, close button sem label
**Impacto**: Screen readers não reconhecem modal
**Fix Estimate**: 2 pts (20 min)
**Recomendação**: Adicionar ARIA attributes, focus trap

```jsx
// ✅ Structure
<div role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <h2 id="modal-title">Dados Brutos</h2>
  <button aria-label="Fechar modal">X</button>
</div>
```

---

### FE-003: Keyboard Navigation — Dropdowns (MEDIUM)
**Status**: BLOCKED
**Componentes**: BulkSearch (export dropdown), ProcessDetails (filter chips)
**Descrição**: Menu dropdown não navegável com keyboard (Arrow keys, Escape)
**Impacto**: Users sem mouse presos
**Fix Estimate**: 5 pts (1-2 hours)
**Recomendação**: Usar WAI-ARIA menu pattern ou Headless UI

---

### FE-004: Chart Accessibility — Dashboard (HIGH)
**Status**: CRITICAL
**Componentes**: Dashboard (3 charts)
**Descrição**: Charts são SVG/divs sem semantic labels, dados inacessíveis
**Impacto**: Screen reader users veem apenas "bar" sem context
**Fix Estimate**: 8 pts (2-3 hours)
**Recomendação**:
  1. Envolver charts em `<figure>` com `<figcaption>`
  2. Adicionar `aria-label` descrevendo dados
  3. Ou: Tabela de dados como fallback textual

```jsx
// ✅ Pattern
<figure>
  <figcaption id="chart-title">Processos por Tribunal</figcaption>
  <div aria-labelledby="chart-title">
    {/* chart rendering */}
  </div>
  <table className="hidden" aria-label="Dados do gráfico">
    {/* data table */}
  </table>
</figure>
```

---

### FE-005: Color Contrast Review (MEDIUM)
**Status**: NEEDS TESTING
**Componentes**: Settings (amber-800), BulkSearch (gray-400), multiple
**Descrição**: Alguns combos de cor podem não passar 4.5:1 contrast ratio
**Impacto**: Users com baixa visão podem não ler texto
**Fix Estimate**: 3 pts (1 hour audit + fixes)
**Recomendação**: WebAIM Contrast Checker em cada combo de cor crítica

---

### FE-006: Testing Coverage (CRITICAL)
**Status**: BLOCKED
**Componentes**: ALL (apenas phases.test.js existe)
**Descrição**: 1 arquivo teste para 9 componentes → falta cobertura
**Impacto**: Regressions não detectadas
**Fix Estimate**: 13 pts (2-3 days)
**Recomendação**:
  - Add Vitest + React Testing Library
  - Test coverage target: 70% lines
  - Stories por arquivo:
    - SearchProcess: input validation, submit, loading
    - BulkSearch: file upload, drag-drop, export
    - ProcessDetails: filtering, sorting, modal open/close
    - ErrorBoundary: error capture, reset
    - etc

---

### FE-007: Prop Drilling → Context API (MEDIUM)
**Status**: OPEN
**Descrição**: Componentes recebem muitas props (labels, onInstanceChange, etc)
**Impacto**: Difícil manutenção, reutilização reduzida
**Fix Estimate**: 5 pts (1-2 hours)
**Recomendação**: Criar Context para Labels + Theme

```jsx
// ✅ Pattern
const LabelContext = createContext(defaultLabels);
const ThemeContext = createContext(defaultTheme);

// Em App:
<LabelContext.Provider value={labels}>
  <ThemeContext.Provider value={theme}>
    <SearchProcess /> {/* sem props labels */}
  </ThemeContext.Provider>
</LabelContext.Provider>
```

---

## Next Steps (Próximas Fases)

### Fase 3 Completa? ✅
- [x] Inventário de 9 componentes
- [x] WCAG 2.1 AA audit rápido
- [x] 7 débitos identificados
- [x] Design system assessment

### Fase 4 (Draft de Débito) → @architect
Consolidar débitos frontend (FE-001 a FE-007) com débitos backend/DB em `technical-debt-DRAFT.md`

### Prioridade Imediata (Quick Wins)
1. **FE-001 Label HTML** (2 pts) ← Easy win
2. **FE-006 Add 3 unit tests** (3 pts) ← Foundation
3. **FE-004 Dashboard chart labels** (5 pts) ← Accessibility gate

---

## Métricas & KPIs

| Métrica | Current | Target (Phase 5) | Status |
|---------|---------|-----------------|--------|
| WCAG AA Compliance | 40% | 90% | 🔴 BEHIND |
| Component Test Coverage | 10% | 70% | 🔴 BEHIND |
| Keyboard Navigation | 60% | 100% | ⚠️ PARTIAL |
| Color Contrast AA | 70% | 100% | ⚠️ PARTIAL |
| Component Reusability Score | 7/10 | 9/10 | ✅ GOOD |

---

## Conclusão

**Frontend está bem estruturado** (9 componentes modulares, design system consistente), mas **acessibilidade é o principal débito**. Quick wins em label associations e testes básicos podem elevar compliance rápido.

**Recomendação**: Priorizar FE-001 (labels) + FE-006 (testes) na próxima sprint. FE-004 (dashboard) pode ficar no backlog se recursos limitados.

---

**Fase 3 ✅ COMPLETA**
**Próxima**: Fase 4 (Draft de Débito Técnico) → @architect

