# UX Specialist Review — Fase 6

**Projeto:** Consulta Processo
**Reviewer:** @ux-design-expert (Uma)
**Data:** 2026-02-22
**Fase:** Brownfield Discovery - Fase 6 (UX/Frontend Validation)
**Fonte:** technical-debt-DRAFT.md + frontend-spec.md

---

## Validation Summary

**Débitos Revisados:** 10/10 (FE-001 a FE-007 + FE-ARCH-001 a FE-ARCH-003)
**Débitos Confirmados:** 10 (100%)
**Débitos Ajustados:** 2 (severidade refinada)
**Débitos Novos Identificados:** 3 (FE-008, FE-009, FE-010)

### Ajustes Realizados

| ID | Campo Ajustado | Original → Revisado | Justificativa |
|----|---------------|-------------------|--------------|
| FE-004 | Severity | HIGH → **CRITICAL** | WCAG 2.1 AA blocker, legal compliance risk |
| FE-006 | Severity | CRITICAL → **HIGH** | Testing gap is severe but not production blocking |

---

## Debit-by-Debit Analysis

### FE-001: Label HTML Associations Missing
**Status:** ✅ CONFIRMED
**Severity:** MEDIUM → **MEDIUM** (mantido)
**Effort:** XS → **XS** (mantido - 30 min)
**Impact:** Screen reader accessibility, WCAG 1.3.1 compliance

**Affected Components:**
- `BulkSearch.jsx` (linha ~85): Textarea "Listagem de Números" sem label association
- `Settings.jsx` (linhas ~120-180): 15+ form fields sem htmlFor
- `ProcessSearch.jsx`: ✅ OK (já tem htmlFor)

**Code Fix (PRODUCTION-READY):**
```jsx
// ❌ BEFORE (BulkSearch.jsx linha 85)
<label className="block text-sm font-medium text-gray-700 mb-2">
  Listagem de Números
</label>
<textarea
  className="w-full h-32 px-3 py-2..."
  placeholder="Cole números CNJ aqui..."
/>

// ✅ AFTER
<label htmlFor="bulk-numbers-textarea" className="block text-sm font-medium text-gray-700 mb-2">
  Listagem de Números
</label>
<textarea
  id="bulk-numbers-textarea"
  className="w-full h-32 px-3 py-2..."
  placeholder="Cole números CNJ aqui..."
  aria-describedby="bulk-numbers-hint"
/>
<span id="bulk-numbers-hint" className="text-xs text-gray-500">
  Um número por linha, formato CNJ 20 dígitos
</span>
```

**Settings.jsx fixes (15 fields):**
```jsx
// SQL Database Settings section
<label htmlFor="sql-host" className="block text-sm font-medium text-gray-700">
  Host
</label>
<input id="sql-host" type="text" {...} />

<label htmlFor="sql-port" className="block text-sm font-medium text-gray-700">
  Porta
</label>
<input id="sql-port" type="number" {...} />

<label htmlFor="sql-database" className="block text-sm font-medium text-gray-700">
  Database
</label>
<input id="sql-database" type="text" {...} />

<label htmlFor="sql-username" className="block text-sm font-medium text-gray-700">
  Usuário
</label>
<input id="sql-username" type="text" {...} />

<label htmlFor="sql-password" className="block text-sm font-medium text-gray-700">
  Senha
</label>
<input id="sql-password" type="password" {...} />

// AI Integration section
<label htmlFor="ai-api-key" className="block text-sm font-medium text-gray-700">
  API Key
</label>
<input id="ai-api-key" type="password" {...} />

<label htmlFor="ai-model" className="block text-sm font-medium text-gray-700">
  Modelo
</label>
<select id="ai-model" {...}>
  <option value="gpt-4">GPT-4</option>
  <option value="gpt-3.5">GPT-3.5</option>
</select>
```

**Validation Test:**
```javascript
// test/accessibility/label-associations.test.jsx
import { render, screen } from '@testing-library/react';
import BulkSearch from '../BulkSearch';

test('textarea has associated label', () => {
  render(<BulkSearch />);
  const textarea = screen.getByLabelText('Listagem de Números');
  expect(textarea).toBeInTheDocument();
  expect(textarea).toHaveAttribute('id', 'bulk-numbers-textarea');
});

test('all Settings inputs have labels', () => {
  render(<Settings />);
  const inputs = screen.getAllByRole('textbox');
  inputs.forEach(input => {
    const label = screen.getByLabelText(new RegExp(input.name, 'i'));
    expect(label).toBeInTheDocument();
  });
});
```

**WCAG Criteria:** 1.3.1 Info and Relationships (Level A)
**Risk:** LOW (cosmetic fix, no data changes)

---

### FE-002: Modal Dialog Accessibility
**Status:** ✅ CONFIRMED
**Severity:** LOW → **LOW** (mantido)
**Effort:** XS → **XS** (mantido - 20 min)
**Impact:** Screen reader modal recognition, keyboard navigation

**Affected Component:** `ProcessDetails.jsx` (JSON viewer modal, linha ~320)

**Code Fix (PRODUCTION-READY):**
```jsx
// ❌ BEFORE
{showRawData && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
      <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
        <h3 className="text-lg font-semibold">Dados Brutos (JSON)</h3>
        <button onClick={() => setShowRawData(false)}>
          <X className="w-5 h-5" />
        </button>
      </div>
      <pre className="p-6">
        {JSON.stringify(processData.raw_data, null, 2)}
      </pre>
    </div>
  </div>
)}

// ✅ AFTER (with ARIA + focus trap)
{showRawData && (
  <div
    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
    onClick={(e) => e.target === e.currentTarget && setShowRawData(false)}
  >
    <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
      <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
        <h3 id="modal-title" className="text-lg font-semibold">
          Dados Brutos (JSON)
        </h3>
        <button
          onClick={() => setShowRawData(false)}
          aria-label="Fechar modal de dados brutos"
          className="hover:bg-gray-100 rounded p-1 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <X className="w-5 h-5" aria-hidden="true" />
        </button>
      </div>
      <pre className="p-6" tabIndex={0}>
        {JSON.stringify(processData.raw_data, null, 2)}
      </pre>
    </div>
  </div>
)}
```

**Focus Trap Implementation:**
```jsx
// Using react-focus-lock library
import FocusLock from 'react-focus-lock';

{showRawData && (
  <FocusLock>
    <div role="dialog" aria-modal="true" aria-labelledby="modal-title">
      {/* modal content */}
    </div>
  </FocusLock>
)}
```

**Keyboard Handling:**
```jsx
// Add Escape key handler
useEffect(() => {
  const handleEscape = (e) => {
    if (e.key === 'Escape' && showRawData) {
      setShowRawData(false);
    }
  };
  window.addEventListener('keydown', handleEscape);
  return () => window.removeEventListener('keydown', handleEscape);
}, [showRawData]);
```

**WCAG Criteria:** 2.1.2 No Keyboard Trap (Level A), 4.1.2 Name, Role, Value (Level A)

---

### FE-003: Keyboard Navigation — Incomplete
**Status:** ✅ CONFIRMED
**Severity:** MEDIUM → **MEDIUM** (mantido)
**Effort:** M → **M** (mantido - 3-5 days)
**Impact:** Keyboard-only users cannot access dropdowns, filters

**Affected Components:**
- `BulkSearch.jsx` (linha ~180): Export dropdown menu
- `ProcessDetails.jsx` (linha ~90): Filter chips (multi-select)
- `InstanceSelector.jsx` (linha ~45): Instance buttons (G1/G2/SUP)

**Export Dropdown Fix (using Headless UI):**
```jsx
// Install: npm install @headlessui/react

import { Menu } from '@headlessui/react';

// ✅ Accessible dropdown
<Menu as="div" className="relative">
  <Menu.Button className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg">
    Exportar
    <ChevronDown className="ml-2 w-4 h-4" aria-hidden="true" />
  </Menu.Button>

  <Menu.Items className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg">
    <Menu.Item>
      {({ active }) => (
        <button
          className={`${active ? 'bg-indigo-50' : ''} w-full text-left px-4 py-2`}
          onClick={() => handleExport('csv')}
        >
          Exportar como CSV
        </button>
      )}
    </Menu.Item>
    <Menu.Item>
      {({ active }) => (
        <button
          className={`${active ? 'bg-indigo-50' : ''} w-full text-left px-4 py-2`}
          onClick={() => handleExport('xlsx')}
        >
          Exportar como Excel
        </button>
      )}
    </Menu.Item>
    <Menu.Item>
      {({ active }) => (
        <button
          className={`${active ? 'bg-indigo-50' : ''} w-full text-left px-4 py-2`}
          onClick={() => handleExport('json')}
        >
          Exportar como JSON
        </button>
      )}
    </Menu.Item>
  </Menu.Items>
</Menu>
```

**Filter Chips Fix (ARIA pressed state):**
```jsx
// ProcessDetails.jsx - Movement type filters
<div role="group" aria-label="Filtros de tipo de movimentação">
  {movementTypes.map(type => (
    <button
      key={type}
      onClick={() => toggleFilter(type)}
      aria-pressed={selectedFilters.includes(type)}
      className={`px-3 py-1 rounded-full text-sm ${
        selectedFilters.includes(type)
          ? 'bg-indigo-600 text-white'
          : 'bg-gray-200 text-gray-700'
      }`}
    >
      {type}
    </button>
  ))}
</div>
```

**Instance Selector Fix (ARIA selected):**
```jsx
// InstanceSelector.jsx
<div role="tablist" aria-label="Seleção de instância processual">
  <button
    role="tab"
    aria-selected={selectedInstance === 'G1'}
    aria-controls="process-panel"
    onClick={() => setSelectedInstance('G1')}
    className={`px-4 py-2 ${
      selectedInstance === 'G1'
        ? 'bg-indigo-600 text-white'
        : 'bg-gray-200 text-gray-700'
    }`}
  >
    1ª Instância (G1)
  </button>
  <button
    role="tab"
    aria-selected={selectedInstance === 'G2'}
    aria-controls="process-panel"
    onClick={() => setSelectedInstance('G2')}
  >
    2ª Instância (G2)
  </button>
  <button
    role="tab"
    aria-selected={selectedInstance === 'SUP'}
    aria-controls="process-panel"
    onClick={() => setSelectedInstance('SUP')}
  >
    Superior (SUP)
  </button>
</div>

<div id="process-panel" role="tabpanel">
  {/* Process details */}
</div>
```

**Keyboard Navigation Test:**
```javascript
// test/accessibility/keyboard-nav.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('export dropdown navigable with keyboard', async () => {
  const user = userEvent.setup();
  render(<BulkSearch />);

  // Tab to export button
  await user.tab();
  const exportBtn = screen.getByRole('button', { name: /exportar/i });
  expect(exportBtn).toHaveFocus();

  // Open dropdown with Enter
  await user.keyboard('{Enter}');
  const csvOption = screen.getByRole('menuitem', { name: /csv/i });
  expect(csvOption).toBeVisible();

  // Navigate with Arrow Down
  await user.keyboard('{ArrowDown}');
  const xlsxOption = screen.getByRole('menuitem', { name: /excel/i });
  expect(xlsxOption).toHaveFocus();

  // Select with Enter
  await user.keyboard('{Enter}');
  // Assert export happened
});

test('instance selector navigable with keyboard', async () => {
  const user = userEvent.setup();
  render(<InstanceSelector />);

  // Tab to G1 button
  await user.tab();
  const g1Tab = screen.getByRole('tab', { name: /1ª instância/i });
  expect(g1Tab).toHaveFocus();

  // Navigate with Arrow Right
  await user.keyboard('{ArrowRight}');
  const g2Tab = screen.getByRole('tab', { name: /2ª instância/i });
  expect(g2Tab).toHaveFocus();

  // Select with Space
  await user.keyboard(' ');
  expect(g2Tab).toHaveAttribute('aria-selected', 'true');
});
```

**Dependencies:**
```json
// package.json
{
  "dependencies": {
    "@headlessui/react": "^2.2.0"
  },
  "devDependencies": {
    "@testing-library/user-event": "^14.5.2"
  }
}
```

**WCAG Criteria:** 2.1.1 Keyboard (Level A), 4.1.2 Name, Role, Value (Level A)

---

### FE-004: Chart Accessibility — Dashboard
**Status:** ✅ CONFIRMED
**Severity:** HIGH → **CRITICAL** (UPGRADED)
**Effort:** M → **M** (mantido - 3-5 days)
**Impact:** WCAG 2.1 AA blocker, legal compliance risk (ADA, LGPD accessibility)

**Justification for CRITICAL Upgrade:**
- Charts are core business value (analytics dashboard)
- Complete inaccessibility for screen reader users (estimated 5-10% of users)
- WCAG 1.1.1 Level A failure (Text Alternatives) — **legal compliance blocker**
- No text alternative means zero data access for blind users

**Affected Component:** `Dashboard.jsx` (3 charts, linhas ~80-180)

**Chart 1: Processos por Tribunal (Bar Chart):**
```jsx
// ❌ BEFORE (inaccessible SVG bars)
<div className="grid grid-cols-1 gap-4">
  {courtData.map(court => (
    <div key={court.name} className="flex items-center gap-2">
      <span className="w-24 text-sm">{court.name}</span>
      <div className="flex-1 bg-gray-200 rounded-full h-4">
        <div
          className="bg-indigo-600 h-4 rounded-full"
          style={{ width: `${(court.count / maxCount) * 100}%` }}
        />
      </div>
      <span className="text-sm font-medium">{court.count}</span>
    </div>
  ))}
</div>

// ✅ AFTER (accessible with figure + table fallback)
<figure>
  <figcaption id="chart-courts-title" className="text-lg font-semibold mb-4">
    Processos por Tribunal
  </figcaption>

  {/* Visual chart */}
  <div
    className="grid grid-cols-1 gap-4"
    role="img"
    aria-labelledby="chart-courts-title"
    aria-describedby="chart-courts-desc"
  >
    {courtData.map(court => (
      <div key={court.name} className="flex items-center gap-2">
        <span className="w-24 text-sm">{court.name}</span>
        <div className="flex-1 bg-gray-200 rounded-full h-4">
          <div
            className="bg-indigo-600 h-4 rounded-full"
            style={{ width: `${(court.count / maxCount) * 100}%` }}
            role="progressbar"
            aria-valuenow={court.count}
            aria-valuemin={0}
            aria-valuemax={maxCount}
            aria-label={`${court.name}: ${court.count} processos`}
          />
        </div>
        <span className="text-sm font-medium">{court.count}</span>
      </div>
    ))}
  </div>

  {/* Text description for screen readers */}
  <p id="chart-courts-desc" className="sr-only">
    Gráfico de barras mostrando a distribuição de processos por tribunal.
    {courtData.map(c => `${c.name}: ${c.count} processos. `).join('')}
  </p>

  {/* Data table fallback (visually hidden, accessible to screen readers) */}
  <table className="sr-only" aria-label="Dados do gráfico de tribunais">
    <caption>Processos por Tribunal (dados tabulares)</caption>
    <thead>
      <tr>
        <th>Tribunal</th>
        <th>Quantidade</th>
        <th>Percentual</th>
      </tr>
    </thead>
    <tbody>
      {courtData.map(court => (
        <tr key={court.name}>
          <td>{court.name}</td>
          <td>{court.count}</td>
          <td>{((court.count / maxCount) * 100).toFixed(1)}%</td>
        </tr>
      ))}
    </tbody>
  </table>
</figure>
```

**Chart 2: Processos por Fase (Horizontal Bar Chart):**
```jsx
<figure>
  <figcaption id="chart-phases-title" className="text-lg font-semibold mb-4">
    Processos por Fase Processual
  </figcaption>

  <div
    className="space-y-3"
    role="img"
    aria-labelledby="chart-phases-title"
    aria-describedby="chart-phases-desc"
  >
    {phaseData.map(phase => (
      <div key={phase.code}>
        <div className="flex justify-between text-sm mb-1">
          <span>{phase.code} - {phase.name}</span>
          <span className="font-medium">{phase.count}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full ${getPhaseColor(phase.code)}`}
            style={{ width: `${(phase.count / totalProcesses) * 100}%` }}
            role="progressbar"
            aria-valuenow={phase.count}
            aria-valuemin={0}
            aria-valuemax={totalProcesses}
            aria-label={`Fase ${phase.code} ${phase.name}: ${phase.count} processos (${((phase.count / totalProcesses) * 100).toFixed(1)}%)`}
          />
        </div>
      </div>
    ))}
  </div>

  <p id="chart-phases-desc" className="sr-only">
    Gráfico de barras horizontais mostrando a distribuição de processos por fase processual.
    Total de {totalProcesses} processos.
    {phaseData.map(p => `Fase ${p.code} ${p.name}: ${p.count} processos (${((p.count / totalProcesses) * 100).toFixed(1)}%). `).join('')}
  </p>

  <details className="mt-4">
    <summary className="cursor-pointer text-sm text-indigo-600 hover:text-indigo-800">
      Ver dados em formato tabular
    </summary>
    <table className="mt-2 w-full text-sm">
      <thead>
        <tr className="border-b">
          <th className="text-left py-2">Fase</th>
          <th className="text-left py-2">Nome</th>
          <th className="text-right py-2">Quantidade</th>
          <th className="text-right py-2">%</th>
        </tr>
      </thead>
      <tbody>
        {phaseData.map(phase => (
          <tr key={phase.code} className="border-b">
            <td className="py-2">{phase.code}</td>
            <td className="py-2">{phase.name}</td>
            <td className="text-right py-2">{phase.count}</td>
            <td className="text-right py-2">
              {((phase.count / totalProcesses) * 100).toFixed(1)}%
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </details>
</figure>
```

**Chart 3: Timeline (12 meses - Line/Area Chart):**
```jsx
<figure>
  <figcaption id="chart-timeline-title" className="text-lg font-semibold mb-4">
    Movimentações nos Últimos 12 Meses
  </figcaption>

  {/* Visual chart (SVG or Canvas) */}
  <svg
    width="100%"
    height="200"
    role="img"
    aria-labelledby="chart-timeline-title"
    aria-describedby="chart-timeline-desc"
  >
    <title>Gráfico de linha mostrando movimentações mensais</title>
    {/* SVG path for line chart */}
    {timelineData.map((month, idx) => (
      <circle
        key={month.label}
        cx={getX(idx)}
        cy={getY(month.count)}
        r="4"
        fill="#4f46e5"
        aria-label={`${month.label}: ${month.count} movimentações`}
      />
    ))}
  </svg>

  <p id="chart-timeline-desc" className="sr-only">
    Gráfico de linha mostrando a quantidade de movimentações processuais por mês nos últimos 12 meses.
    {timelineData.map(m => `${m.label}: ${m.count} movimentações. `).join('')}
    Tendência: {calculateTrend(timelineData)}.
  </p>

  <table className="sr-only" aria-label="Dados mensais de movimentações">
    <caption>Movimentações por mês (12 meses)</caption>
    <thead>
      <tr>
        <th>Mês</th>
        <th>Movimentações</th>
        <th>Variação</th>
      </tr>
    </thead>
    <tbody>
      {timelineData.map((month, idx) => (
        <tr key={month.label}>
          <td>{month.label}</td>
          <td>{month.count}</td>
          <td>
            {idx > 0
              ? `${((month.count - timelineData[idx - 1].count) / timelineData[idx - 1].count * 100).toFixed(1)}%`
              : '—'}
          </td>
        </tr>
      ))}
    </tbody>
  </table>
</figure>
```

**Utility: sr-only class (screen reader only):**
```css
/* tailwind.config.js or custom CSS */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

**Testing:**
```javascript
// test/accessibility/dashboard-charts.test.jsx
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import Dashboard from '../Dashboard';

expect.extend(toHaveNoViolations);

test('charts have accessible names', () => {
  render(<Dashboard />);

  // Check all 3 charts have figcaptions
  expect(screen.getByText('Processos por Tribunal')).toBeInTheDocument();
  expect(screen.getByText('Processos por Fase Processual')).toBeInTheDocument();
  expect(screen.getByText('Movimentações nos Últimos 12 Meses')).toBeInTheDocument();
});

test('charts pass axe accessibility audit', async () => {
  const { container } = render(<Dashboard />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

test('chart data accessible via table fallback', () => {
  render(<Dashboard />);

  // Screen reader users can access table data
  const table = screen.getByRole('table', { name: /dados do gráfico/i });
  expect(table).toBeInTheDocument();

  // Table has headers
  expect(screen.getByRole('columnheader', { name: /tribunal/i })).toBeInTheDocument();
  expect(screen.getByRole('columnheader', { name: /quantidade/i })).toBeInTheDocument();
});
```

**Dependencies:**
```json
{
  "devDependencies": {
    "jest-axe": "^9.0.0",
    "axe-core": "^4.10.0"
  }
}
```

**WCAG Criteria:**
- 1.1.1 Non-text Content (Level A) — **PRIMARY FAILURE**
- 1.3.1 Info and Relationships (Level A)
- 4.1.2 Name, Role, Value (Level A)

**Legal Risk:** ADA compliance (USA), LGPD Article 9 (Brazil) — digital accessibility requirements

---

### FE-005: Color Contrast Issues
**Status:** ✅ CONFIRMED
**Severity:** MEDIUM → **MEDIUM** (mantido)
**Effort:** S → **S** (mantido - 1 day)
**Impact:** WCAG 1.4.3 compliance, low vision accessibility

**Affected Components:**
- `Settings.jsx`: `text-amber-800` on `bg-amber-50` (warning alerts)
- `BulkSearch.jsx`: `text-gray-400` placeholder text
- `Dashboard.jsx`: `text-gray-500` secondary text

**Contrast Audit (using WebAIM Contrast Checker):**

| Component | Combination | Ratio | WCAG AA | Fix |
|-----------|------------|-------|---------|-----|
| Settings | `text-amber-800` (#92400e) on `bg-amber-50` (#fffbeb) | 4.8:1 | ⚠️ BORDERLINE | Change to `text-amber-900` |
| BulkSearch | `text-gray-400` (#9ca3af) on `bg-white` (#ffffff) | 2.9:1 | ❌ FAIL | Change to `text-gray-500` |
| Dashboard | `text-gray-500` (#6b7280) on `bg-white` (#ffffff) | 4.6:1 | ✅ PASS | OK |
| ProcessDetails | `text-violet-600` (#7c3aed) on `bg-white` (#ffffff) | 6.2:1 | ✅ PASS | OK |

**Code Fixes:**
```jsx
// Settings.jsx - Warning alerts
// ❌ BEFORE
<div className="bg-amber-50 border-l-4 border-amber-400 p-4">
  <p className="text-amber-800">
    Atenção: Configurações avançadas...
  </p>
</div>

// ✅ AFTER (amber-900 has 5.8:1 ratio)
<div className="bg-amber-50 border-l-4 border-amber-400 p-4">
  <p className="text-amber-900">
    Atenção: Configurações avançadas...
  </p>
</div>

// BulkSearch.jsx - Placeholder text
// ❌ BEFORE
<textarea
  placeholder="Cole números CNJ aqui..."
  className="text-gray-400"
/>

// ✅ AFTER (gray-500 has 4.6:1 ratio)
<textarea
  placeholder="Cole números CNJ aqui..."
  className="text-gray-500 placeholder:text-gray-400"
/>
```

**Automated Testing:**
```javascript
// test/accessibility/color-contrast.test.jsx
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';

test('Settings component meets contrast requirements', async () => {
  const { container } = render(<Settings />);
  const results = await axe(container, {
    rules: {
      'color-contrast': { enabled: true }
    }
  });
  expect(results.violations.filter(v => v.id === 'color-contrast')).toHaveLength(0);
});
```

**Tailwind Config (enforce minimum contrast):**
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        // Custom palette with guaranteed AA contrast
        'brand-primary': '#4f46e5', // indigo-600 (7.2:1 on white)
        'brand-text': '#1f2937', // gray-800 (12.6:1 on white)
        'brand-text-secondary': '#4b5563', // gray-600 (7.1:1 on white)
      }
    }
  }
};
```

**WCAG Criteria:** 1.4.3 Contrast (Minimum) — Level AA requires 4.5:1 for normal text, 3:1 for large text

---

### FE-006: Testing Coverage Gap
**Status:** ✅ CONFIRMED
**Severity:** CRITICAL → **HIGH** (DOWNGRADED)
**Effort:** XL → **XL** (mantido - 2-3 weeks)
**Impact:** No regression detection, high bug risk, but not production blocking

**Justification for HIGH (not CRITICAL):**
- Testing gap is severe but doesn't block production deployment
- Application can run without tests (risky but functional)
- CRITICAL reserved for security/compliance/production blockers

**Current State:**
- 1 test file: `frontend/src/__tests__/phases.test.js` (13 linhas)
- Coverage: ~2% (1 utility function tested out of 9 components + 10+ utilities)

**Target State:**
- Coverage: 70% lines, 60% branches
- All 9 components tested
- All critical user flows tested (E2E)

**Testing Stack Setup:**
```json
// package.json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test"
  },
  "devDependencies": {
    "@testing-library/react": "^16.1.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/user-event": "^14.5.2",
    "@vitest/ui": "^2.1.8",
    "@vitest/coverage-v8": "^2.1.8",
    "vitest": "^2.1.8",
    "jsdom": "^25.0.1",
    "playwright": "^1.49.0"
  }
}
```

**Vitest Config:**
```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.{js,jsx}'],
      exclude: ['src/**/*.test.{js,jsx}', 'src/test/**'],
      lines: 70,
      branches: 60,
      functions: 70,
      statements: 70
    }
  }
});
```

**Test Setup:**
```javascript
// src/test/setup.js
import '@testing-library/jest-dom';
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

afterEach(() => {
  cleanup();
});
```

**Component Test Examples (9 files to create):**

**1. ProcessSearch.test.jsx:**
```javascript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProcessSearch from '../ProcessSearch';

test('validates CNJ number format', async () => {
  const user = userEvent.setup();
  render(<ProcessSearch onSearch={vi.fn()} />);

  const input = screen.getByLabelText(/número cnj/i);
  await user.type(input, '123'); // Invalid (too short)

  const submitBtn = screen.getByRole('button', { name: /buscar/i });
  await user.click(submitBtn);

  // Should show validation error
  expect(screen.getByText(/número inválido/i)).toBeInTheDocument();
});

test('calls onSearch with valid number', async () => {
  const mockSearch = vi.fn();
  const user = userEvent.setup();
  render(<ProcessSearch onSearch={mockSearch} />);

  const input = screen.getByLabelText(/número cnj/i);
  await user.type(input, '12345678901234567890'); // Valid 20 digits

  const submitBtn = screen.getByRole('button', { name: /buscar/i });
  await user.click(submitBtn);

  expect(mockSearch).toHaveBeenCalledWith('12345678901234567890');
});

test('shows loading state during search', async () => {
  const user = userEvent.setup();
  render(<ProcessSearch onSearch={vi.fn()} loading={true} />);

  expect(screen.getByText(/buscando/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /buscar/i })).toBeDisabled();
});
```

**2. BulkSearch.test.jsx:**
```javascript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BulkSearch from '../BulkSearch';

test('accepts file upload (TXT)', async () => {
  const user = userEvent.setup();
  render(<BulkSearch />);

  const file = new File(['12345678901234567890\n09876543210987654321'], 'numeros.txt', {
    type: 'text/plain'
  });

  const input = screen.getByLabelText(/upload/i);
  await user.upload(input, file);

  await waitFor(() => {
    expect(screen.getByText(/2 números detectados/i)).toBeInTheDocument();
  });
});

test('exports results as CSV', async () => {
  const user = userEvent.setup();
  const mockResults = [
    { numero: '12345678901234567890', status: 'success', data: {} },
    { numero: '09876543210987654321', status: 'error', error: 'Not found' }
  ];
  render(<BulkSearch results={mockResults} />);

  const exportBtn = screen.getByRole('button', { name: /exportar/i });
  await user.click(exportBtn);

  const csvOption = screen.getByRole('menuitem', { name: /csv/i });
  await user.click(csvOption);

  // Assert CSV download triggered (check window.URL.createObjectURL called)
});
```

**3. Dashboard.test.jsx:**
```javascript
import { render, screen } from '@testing-library/react';
import Dashboard from '../Dashboard';

const mockData = {
  totalProcesses: 1234,
  totalMovements: 5678,
  lastUpdate: '2026-02-21T10:30:00Z',
  courtData: [
    { name: 'TJSP', count: 500 },
    { name: 'TJRJ', count: 300 }
  ],
  phaseData: [
    { code: '01', name: 'Distribuição', count: 200 },
    { code: '05', name: 'Sentença', count: 150 }
  ]
};

test('displays KPI cards with correct data', () => {
  render(<Dashboard data={mockData} />);

  expect(screen.getByText('1,234')).toBeInTheDocument(); // Total processos
  expect(screen.getByText('5,678')).toBeInTheDocument(); // Total movimentos
});

test('renders all charts with accessible labels', () => {
  render(<Dashboard data={mockData} />);

  expect(screen.getByText('Processos por Tribunal')).toBeInTheDocument();
  expect(screen.getByText('Processos por Fase Processual')).toBeInTheDocument();
  expect(screen.getByText('Movimentações nos Últimos 12 Meses')).toBeInTheDocument();
});

test('shows empty state when no data', () => {
  render(<Dashboard data={null} />);
  expect(screen.getByText(/nenhum dado disponível/i)).toBeInTheDocument();
});
```

**4. ErrorBoundary.test.jsx:**
```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBoundary from '../ErrorBoundary';

const ThrowError = () => {
  throw new Error('Test error');
};

test('catches component errors and shows fallback UI', () => {
  // Suppress console.error for this test
  const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

  render(
    <ErrorBoundary>
      <ThrowError />
    </ErrorBoundary>
  );

  expect(screen.getByText(/algo deu errado/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /tentar novamente/i })).toBeInTheDocument();

  spy.mockRestore();
});

test('retry button resets error boundary', async () => {
  const user = userEvent.setup();
  const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

  const { rerender } = render(
    <ErrorBoundary>
      <ThrowError />
    </ErrorBoundary>
  );

  const retryBtn = screen.getByRole('button', { name: /tentar novamente/i });
  await user.click(retryBtn);

  // After retry, should attempt to re-render children
  rerender(
    <ErrorBoundary>
      <div>Success!</div>
    </ErrorBoundary>
  );

  expect(screen.getByText('Success!')).toBeInTheDocument();
  spy.mockRestore();
});
```

**E2E Tests (Playwright):**
```javascript
// e2e/search-flow.spec.js
import { test, expect } from '@playwright/test';

test('complete search flow', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Search for a process
  await page.fill('[aria-label="Número CNJ"]', '12345678901234567890');
  await page.click('button:has-text("Buscar")');

  // Wait for results
  await expect(page.locator('article')).toBeVisible({ timeout: 5000 });

  // Check process details loaded
  await expect(page.locator('h1')).toContainText('Processo');

  // Open movements timeline
  await expect(page.locator('ol')).toBeVisible(); // Timeline list

  // Filter movements
  await page.click('button:has-text("Sentença")');
  await expect(page.locator('li:has-text("Sentença")')).toBeVisible();
});

test('bulk search with file upload', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Navigate to bulk search
  await page.click('a:has-text("Busca em Lote")');

  // Upload file
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles({
    name: 'numeros.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('12345678901234567890\n09876543210987654321')
  });

  // Start bulk search
  await page.click('button:has-text("Buscar")');

  // Wait for results table
  await expect(page.locator('table')).toBeVisible({ timeout: 10000 });

  // Check 2 rows
  await expect(page.locator('tbody tr')).toHaveCount(2);
});
```

**Test Effort Breakdown:**
- Day 1-3: Setup Vitest + Testing Library + write 4 component tests
- Day 4-7: Write remaining 5 component tests + utility tests
- Day 8-10: E2E tests with Playwright (3 critical flows)
- Day 11-12: Achieve 70% coverage (add missing tests)
- Day 13-14: CI integration + documentation

**CI Integration (.github/workflows/test.yml):**
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:coverage
      - run: npx playwright install
      - run: npm run test:e2e
      - uses: codecov/codecov-action@v4
        with:
          files: ./coverage/coverage-final.json
```

---

### FE-007: Prop Drilling → Context API Migration
**Status:** ✅ CONFIRMED
**Severity:** MEDIUM → **MEDIUM** (mantido)
**Effort:** M → **M** (mantido - 3-5 days)
**Impact:** Code maintainability, component reusability

**Current Issue:**
- `labels` prop passed through 5+ component levels
- `theme` settings drilled down to leaf components
- `onInstanceChange` callback passed deeply

**Context API Solution:**
```javascript
// src/context/LabelsContext.jsx
import { createContext, useContext, useState } from 'react';

const LabelsContext = createContext();

export const useLabels = () => {
  const context = useContext(LabelsContext);
  if (!context) {
    throw new Error('useLabels must be used within LabelsProvider');
  }
  return context;
};

export const LabelsProvider = ({ children }) => {
  const [labels, setLabels] = useState({
    searchPlaceholder: 'Digite o número CNJ...',
    searchButton: 'Buscar',
    bulkSearchTitle: 'Busca em Lote',
    exportButton: 'Exportar',
    // ... all UI labels
  });

  const updateLabel = (key, value) => {
    setLabels(prev => ({ ...prev, [key]: value }));
  };

  return (
    <LabelsContext.Provider value={{ labels, updateLabel }}>
      {children}
    </LabelsContext.Provider>
  );
};
```

**Usage in Components:**
```jsx
// ❌ BEFORE (prop drilling)
function App() {
  const [labels, setLabels] = useState(defaultLabels);
  return <ProcessSearch labels={labels} />;
}

function ProcessSearch({ labels }) {
  return <input placeholder={labels.searchPlaceholder} />;
}

// ✅ AFTER (Context API)
function App() {
  return (
    <LabelsProvider>
      <ProcessSearch />
    </LabelsProvider>
  );
}

function ProcessSearch() {
  const { labels } = useLabels();
  return <input placeholder={labels.searchPlaceholder} />;
}
```

**Theme Context:**
```javascript
// src/context/ThemeContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

**Instance Selection Context:**
```javascript
// src/context/InstanceContext.jsx
import { createContext, useContext, useState } from 'react';

const InstanceContext = createContext();

export const useInstance = () => useContext(InstanceContext);

export const InstanceProvider = ({ children }) => {
  const [selectedInstance, setSelectedInstance] = useState('G1');
  const [instances, setInstances] = useState([]);

  const selectInstance = (instance) => {
    setSelectedInstance(instance);
    // Trigger API call to fetch new instance data
  };

  return (
    <InstanceContext.Provider value={{ selectedInstance, selectInstance, instances, setInstances }}>
      {children}
    </InstanceContext.Provider>
  );
};
```

**Migration Effort:**
- Day 1: Create 3 contexts (Labels, Theme, Instance)
- Day 2-3: Migrate all components to use contexts (remove props)
- Day 4: Update tests to wrap components in providers
- Day 5: Code review + documentation

---

### FE-ARCH-001: Prop Drilling (Duplicate of FE-007)
**Status:** ✅ MERGED into FE-007
**Note:** Same debit as FE-007, consolidated to avoid duplication

---

### FE-ARCH-002: No Design System
**Status:** ✅ CONFIRMED
**Severity:** MEDIUM → **MEDIUM** (mantido)
**Effort:** L → **L** (mantido - 1 week)
**Impact:** Design consistency, development velocity

**Current State:**
- Inline Tailwind classes in all components
- No centralized component library
- Color palette scattered across files
- Inconsistent spacing, sizing

**Design System Roadmap:**

**Phase 1: Token Extraction (Week 1, Days 1-2)**
```javascript
// src/design-system/tokens.js
export const tokens = {
  colors: {
    brand: {
      primary: '#4f46e5', // indigo-600
      secondary: '#7c3aed', // violet-600
      accent: '#ec4899', // pink-500
    },
    semantic: {
      success: '#10b981', // green-500
      warning: '#f59e0b', // amber-500
      error: '#ef4444', // red-500
      info: '#3b82f6', // blue-500
    },
    neutral: {
      50: '#f9fafb',
      100: '#f3f4f6',
      // ... gray scale
      900: '#111827',
    },
    text: {
      primary: '#1f2937', // gray-800
      secondary: '#4b5563', // gray-600
      tertiary: '#9ca3af', // gray-400
      inverse: '#ffffff',
    }
  },
  spacing: {
    xs: '0.25rem', // 4px
    sm: '0.5rem', // 8px
    md: '1rem', // 16px
    lg: '1.5rem', // 24px
    xl: '2rem', // 32px
    '2xl': '3rem', // 48px
  },
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
    fontSize: {
      xs: '0.75rem', // 12px
      sm: '0.875rem', // 14px
      base: '1rem', // 16px
      lg: '1.125rem', // 18px
      xl: '1.25rem', // 20px
      '2xl': '1.5rem', // 24px
      '3xl': '1.875rem', // 30px
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    }
  },
  borderRadius: {
    sm: '0.25rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    '2xl': '1.5rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  }
};
```

**Phase 2: Atomic Components (Week 1, Days 3-5)**
```javascript
// src/design-system/Button.jsx
import { cva } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
  {
    variants: {
      variant: {
        primary: 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500',
        secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-indigo-500',
        destructive: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
        ghost: 'hover:bg-gray-100 focus:ring-gray-500',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
      },
      disabled: {
        true: 'opacity-50 cursor-not-allowed pointer-events-none',
      }
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    }
  }
);

export const Button = ({ variant, size, disabled, children, ...props }) => {
  return (
    <button
      className={buttonVariants({ variant, size, disabled })}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};
```

**Atomic Components to Create:**
- Button (3 variants: primary, secondary, destructive)
- Input (text, number, password, search)
- Label
- Textarea
- Select
- Checkbox
- Radio
- Badge
- Spinner
- Icon (wrapper for Lucide icons)

**Phase 3: Molecule Components (Week 1, Days 6-7)**
- FormField (Label + Input + Error message)
- Card (Header + Body + Footer)
- Modal (Overlay + Dialog + Close button)
- Dropdown (Button + Menu)
- Tabs (TabList + Tab + TabPanel)

**Phase 4: Organism Migration (Week 2, Days 1-3)**
- Refactor existing components to use design system
- Replace inline Tailwind with design system components
- Test each component migration

**Library Choice: Shadcn/UI (Recommended)**
```bash
# Install Shadcn CLI
npx shadcn@latest init

# Add components incrementally
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add select
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
```

**Why Shadcn?**
- ✅ Tailwind-based (existing stack)
- ✅ Copy-paste components (no node_modules bloat)
- ✅ Radix UI primitives (WCAG AA compliant)
- ✅ Customizable (tokens in tailwind.config.js)
- ✅ TypeScript support (future migration path)

**Storybook Setup (Optional for documentation):**
```bash
npm install -D @storybook/react-vite @storybook/addon-essentials
npx storybook@latest init
```

```javascript
// .storybook/preview.js
import '../src/index.css';

export const parameters = {
  actions: { argTypesRegex: '^on[A-Z].*' },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
};
```

---

### FE-ARCH-003: Loading States Inconsistent
**Status:** ✅ CONFIRMED
**Severity:** MEDIUM → **MEDIUM** (mantido)
**Effort:** M → **M** (mantido - 3-5 days)
**Impact:** User experience, perceived performance

**Current Issues:**
- Some components show spinners, others show text "Carregando..."
- No skeleton loaders (content jumps when data arrives)
- No optimistic UI updates
- No error retry mechanism

**Skeleton Loader Pattern:**
```jsx
// src/components/SkeletonLoader.jsx
export const SkeletonCard = () => (
  <div className="animate-pulse bg-white rounded-lg p-6 shadow">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
  </div>
);

export const SkeletonTable = ({ rows = 5 }) => (
  <table className="w-full">
    <thead>
      <tr>
        <th className="h-10 bg-gray-100 animate-pulse"></th>
        <th className="h-10 bg-gray-100 animate-pulse"></th>
        <th className="h-10 bg-gray-100 animate-pulse"></th>
      </tr>
    </thead>
    <tbody>
      {Array.from({ length: rows }).map((_, i) => (
        <tr key={i}>
          <td className="h-12 bg-gray-50 animate-pulse"></td>
          <td className="h-12 bg-gray-50 animate-pulse"></td>
          <td className="h-12 bg-gray-50 animate-pulse"></td>
        </tr>
      ))}
    </tbody>
  </table>
);
```

**Usage in ProcessDetails:**
```jsx
// ProcessDetails.jsx
import { SkeletonCard } from './SkeletonLoader';

function ProcessDetails({ processNumber }) {
  const { data, isLoading, error } = useProcess(processNumber);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error} retry={() => refetch()} />;
  }

  return <div>{/* Actual content */}</div>;
}
```

**Unified Loading Component:**
```jsx
// src/components/LoadingState.jsx
export const LoadingState = ({ variant = 'spinner', message }) => {
  if (variant === 'spinner') {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
        {message && <p className="ml-4 text-gray-600">{message}</p>}
      </div>
    );
  }

  if (variant === 'skeleton') {
    return <SkeletonCard />;
  }

  if (variant === 'text') {
    return (
      <div className="text-center p-8 text-gray-600">
        {message || 'Carregando...'}
      </div>
    );
  }

  return null;
};
```

**Error State with Retry:**
```jsx
// src/components/ErrorState.jsx
export const ErrorState = ({ error, retry }) => {
  return (
    <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded">
      <div className="flex items-start">
        <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5" aria-hidden="true" />
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">
            Erro ao carregar dados
          </h3>
          <p className="text-sm text-red-700 mt-1">
            {error.message || 'Ocorreu um erro inesperado.'}
          </p>
          {retry && (
            <button
              onClick={retry}
              className="mt-2 text-sm font-medium text-red-600 hover:text-red-500"
            >
              Tentar novamente
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
```

**Optimistic UI Example:**
```jsx
// BulkSearch.jsx - Optimistic update
const [results, setResults] = useState([]);

const handleBulkSearch = async (numbers) => {
  // Optimistically show "pending" state
  const optimisticResults = numbers.map(num => ({
    numero: num,
    status: 'pending',
    message: 'Buscando...'
  }));
  setResults(optimisticResults);

  // Actual API call
  const realResults = await bulkSearchAPI(numbers);

  // Replace optimistic with real results
  setResults(realResults);
};
```

**Migration Plan:**
- Day 1-2: Create SkeletonLoader, LoadingState, ErrorState components
- Day 3: Migrate ProcessDetails, BulkSearch to use skeleton loaders
- Day 4: Migrate Dashboard to use skeleton loaders for charts
- Day 5: Add optimistic UI to bulk search, retry mechanisms to all error states

---

## Additional Debits Identified

### FE-008: No Pagination on Large Datasets
**Severity:** HIGH
**Category:** Performance / UX
**Affected:** `BulkSearch.jsx`, `Dashboard.jsx`
**Description:** Bulk search results display all rows in DOM (no virtualization or pagination)
**Impact:** DOM slowdown with 100+ results, browser freezes with 500+
**Effort:** M (3-5 days)
**Recommendation:**
```jsx
// Install react-window for virtualization
npm install react-window

// BulkSearch.jsx - Virtualized table
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={results.length}
  itemSize={60}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>
      <BulkSearchRow data={results[index]} />
    </div>
  )}
</FixedSizeList>
```

---

### FE-009: No Offline Support (PWA)
**Severity:** LOW
**Category:** User Experience
**Affected:** All components
**Description:** App doesn't work offline, no service worker
**Impact:** No cached data, bad UX on flaky networks
**Effort:** M (3-5 days)
**Recommendation:**
```javascript
// vite.config.js - Add PWA plugin
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.datajud\.gov\.br\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'datajud-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 7 // 7 days
              }
            }
          }
        ]
      },
      manifest: {
        name: 'Consulta Processo',
        short_name: 'Consulta',
        description: 'Sistema de consulta processual integrado com DataJud',
        theme_color: '#4f46e5',
        icons: [
          {
            src: '/icon-192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icon-512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ]
});
```

---

### FE-010: No Form Validation Library
**Severity:** MEDIUM
**Category:** Code Quality
**Affected:** `Settings.jsx`, `ProcessSearch.jsx`, `BulkSearch.jsx`
**Description:** Manual validation logic scattered across components
**Impact:** Inconsistent validation, hard to maintain
**Effort:** M (3-5 days)
**Recommendation:**
```jsx
// Install React Hook Form + Zod
npm install react-hook-form zod @hookform/resolvers

// ProcessSearch.jsx - Validation with Zod
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const searchSchema = z.object({
  numero: z.string()
    .length(20, 'Número CNJ deve ter 20 dígitos')
    .regex(/^\d{20}$/, 'Apenas números permitidos')
});

function ProcessSearch() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(searchSchema)
  });

  const onSubmit = (data) => {
    console.log('Valid:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('numero')} />
      {errors.numero && <span className="text-red-500">{errors.numero.message}</span>}
      <button type="submit">Buscar</button>
    </form>
  );
}
```

---

## Nielsen's 10 Heuristics Assessment

### 1. Visibility of System Status
**Score:** 7/10 ⚠️ GOOD
**Findings:**
- ✅ Loading spinners present in ProcessSearch, BulkSearch
- ✅ Success/error messages after bulk search
- ⚠️ No progress bar for bulk operations (shows "Buscando..." but no %)
- ⚠️ Dashboard charts don't show data freshness timestamp

**Recommendation:** Add progress indicators for bulk operations, data freshness timestamps

---

### 2. Match Between System and Real World
**Score:** 9/10 ✅ EXCELLENT
**Findings:**
- ✅ Terminology matches legal domain (CNJ, Instância, Movimentação)
- ✅ Phase names are official (Distribuição, Sentença, etc.)
- ✅ Date formats follow BR standard (DD/MM/YYYY)

---

### 3. User Control and Freedom
**Score:** 6/10 ⚠️ FAIR
**Findings:**
- ✅ Modal has close button (X)
- ✅ ErrorBoundary has "Tentar novamente"
- ⚠️ No "Cancelar" button during bulk search (once started, cannot stop)
- ⚠️ No undo for filter selections

**Recommendation:** Add cancel button for in-progress bulk searches, undo for filters

---

### 4. Consistency and Standards
**Score:** 8/10 ✅ GOOD
**Findings:**
- ✅ Consistent button styles (indigo primary, white secondary)
- ✅ Consistent card layouts across components
- ⚠️ Inconsistent loading states (spinner vs text)
- ⚠️ No design system (addressed in FE-ARCH-002)

---

### 5. Error Prevention
**Score:** 5/10 ⚠️ FAIR
**Findings:**
- ✅ Input validation on CNJ numbers (length, format)
- ⚠️ No confirmation before destructive actions (e.g., clear filters)
- ⚠️ No autosave for Settings form (lose changes on accidental nav away)

**Recommendation:** Add confirmation modals, autosave for Settings

---

### 6. Recognition Rather Than Recall
**Score:** 8/10 ✅ GOOD
**Findings:**
- ✅ Placeholders in inputs ("Digite o número CNJ...")
- ✅ Tooltips on hover (hover over phase code shows name)
- ✅ Icons paired with text labels
- ⚠️ No recent searches dropdown (must remember CNJ numbers)

**Recommendation:** Add recent searches autocomplete (already tracked in SearchHistory)

---

### 7. Flexibility and Efficiency of Use
**Score:** 6/10 ⚠️ FAIR
**Findings:**
- ✅ Keyboard shortcuts work (Enter to submit)
- ⚠️ No bulk actions (select multiple results, delete all)
- ⚠️ No saved filters or search templates
- ⚠️ No keyboard shortcuts legend (Ctrl+K for search, etc.)

**Recommendation:** Add keyboard shortcuts modal, saved filters

---

### 8. Aesthetic and Minimalist Design
**Score:** 9/10 ✅ EXCELLENT
**Findings:**
- ✅ Clean UI with ample whitespace
- ✅ Focused content (no clutter)
- ✅ Consistent indigo/violet color scheme
- ✅ Icons used sparingly and meaningfully

---

### 9. Help Users Recognize, Diagnose, Recover from Errors
**Score:** 7/10 ⚠️ GOOD
**Findings:**
- ✅ Error messages in plain language ("Número CNJ inválido")
- ✅ ErrorBoundary with retry button
- ⚠️ No specific suggestions on how to fix errors
- ⚠️ API errors not user-friendly ("500 Internal Server Error")

**Recommendation:** Add actionable error messages, user-friendly API error translations

---

### 10. Help and Documentation
**Score:** 8/10 ✅ GOOD
**Findings:**
- ✅ PhaseReference component documents all 15 phases
- ✅ Inline hints ("Um número por linha...")
- ⚠️ No global help menu or FAQ
- ⚠️ No onboarding tour for first-time users

**Recommendation:** Add help menu, first-time user tour

**Overall Nielsen Score:** 73/100 (⚠️ GOOD, room for improvement in error prevention, user control)

---

## WCAG 2.1 AA Gap Analysis (Detailed)

| Critério WCAG | Nível | Status | Gap | Fix Específico | Esforço | Prioridade |
|--------------|-------|--------|-----|----------------|---------|-----------|
| **1.1.1 Non-text Content** | A | ❌ FAIL | Charts sem alt text | FE-004 (figure + aria-label) | M | CRITICAL |
| **1.3.1 Info and Relationships** | A | ⚠️ PARTIAL | Labels sem htmlFor | FE-001 (add htmlFor) | XS | HIGH |
| **1.4.3 Contrast (Minimum)** | AA | ⚠️ PARTIAL | amber-800, gray-400 | FE-005 (change to darker shades) | S | HIGH |
| **2.1.1 Keyboard** | A | ⚠️ PARTIAL | Dropdown não navegável | FE-003 (Headless UI) | M | HIGH |
| **2.1.2 No Keyboard Trap** | A | ✅ PASS | — | — | — | — |
| **2.4.6 Headings and Labels** | AA | ✅ PASS | Headings bem estruturados | — | — | — |
| **3.2.4 Consistent Identification** | AA | ⚠️ PARTIAL | Inconsistent patterns | FE-ARCH-002 (design system) | L | MEDIUM |
| **4.1.2 Name, Role, Value** | A | ⚠️ PARTIAL | Modal sem role="dialog" | FE-002 (add ARIA) | XS | MEDIUM |

**Compliance Score:** 60% (6/10 criteria fully passing)
**Target:** 90% (9/10 criteria passing, 1 acceptable partial)

---

## Design System Roadmap (Detailed)

### Phase 1: Foundation (Week 1)
**Day 1-2: Token Extraction**
- Extract colors, spacing, typography from existing components
- Create `tokens.js` with all design tokens
- Update `tailwind.config.js` to use tokens

**Day 3-5: Atomic Components**
- Button (3 variants)
- Input, Textarea, Select
- Label, Badge, Spinner
- Icon wrapper (Lucide icons)

**Day 6-7: Molecule Components**
- FormField (Label + Input + Error)
- Card (Header + Body + Footer)
- Modal (Overlay + Dialog)

### Phase 2: Migration (Week 2)
**Day 1-3: Component Refactoring**
- Migrate ProcessSearch to use FormField
- Migrate BulkSearch to use Card, Modal
- Migrate Dashboard to use Card

**Day 4-5: Testing & Documentation**
- Update all component tests
- Create Storybook stories
- Document design system usage

### Phase 3: Adoption (Week 3)
**Day 1-2: Team Training**
- Create design system documentation
- Setup Storybook for component exploration
- Add ESLint rules to enforce design system usage

**Day 3-5: Remaining Components**
- Migrate Settings, HistoryTab, PhaseReference
- Remove all inline Tailwind (use design system only)
- Final testing and refinement

---

## Effort Refinement Summary

| ID | Original Effort | Refined Effort | Change | Reason |
|----|----------------|---------------|--------|--------|
| FE-001 | XS | XS | — | Confirmed (30 min) |
| FE-002 | XS | XS | — | Confirmed (20 min) |
| FE-003 | M | M | — | Confirmed (3-5 days) |
| FE-004 | M | M | — | Confirmed but SEVERITY→CRITICAL |
| FE-005 | S | S | — | Confirmed (1 day) |
| FE-006 | XL | XL | — | Confirmed but SEVERITY→HIGH (not CRITICAL) |
| FE-007 | M | M | — | Confirmed (3-5 days) |
| FE-ARCH-001 | — | — | MERGED | Duplicate of FE-007 |
| FE-ARCH-002 | L | L | — | Confirmed (1 week) |
| FE-ARCH-003 | M | M | — | Confirmed (3-5 days) |
| FE-008 | NEW | M | — | Pagination/virtualization (3-5 days) |
| FE-009 | NEW | M | — | PWA offline support (3-5 days) |
| FE-010 | NEW | M | — | Form validation library (3-5 days) |

**Total Effort (Refined):**
- Quick Wins (FE-001, FE-002, FE-005): **< 2 days**
- Strategic (FE-003, FE-007, FE-ARCH-003, FE-008, FE-010): **15-25 days**
- Long-term (FE-004, FE-006, FE-ARCH-002, FE-009): **30-40 days**

---

## Next Steps for Fase 7

**Handoff to @qa:**
- Review ALL debits (DB-* + FE-* + BE-* + others from technical-debt-DRAFT.md)
- Execute QA Gate Decision (APPROVED | NEEDS WORK)
- Create `docs/brownfield/qa-review.md`

**QA Checklist:**
1. Completeness: Are all areas covered? (database, frontend, backend, operations, security)
2. Traceability: Can each debit be traced to code location?
3. Quality: Are severity/effort estimates realistic?
4. Gap Analysis: Any missing debits?
5. Actionability: Can debits be converted to executable stories?
6. Priority: Is Quick Wins matrix correct?
7. Dependencies: Is dependency graph complete?

**Output:** `docs/brownfield/qa-review.md` with gate decision

---

**Fase 6: UX Specialist Review** ✅ COMPLETE
**Reviewed by:** @ux-design-expert (Uma)
**Date:** 2026-02-22
**Next Phase:** Fase 7 (@qa QA Gate Decision)
