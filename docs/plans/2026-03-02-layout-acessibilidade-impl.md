# Layout, Acessibilidade e Dark Mode — Plano de Implementação

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reestruturar a navegação (4 abas), adicionar drawer de configurações no Analytics, modal das 15 fases, toggle de tema claro/escuro e dark mode em todos os componentes.

**Architecture:** `useTheme.js` lê/grava `settingsStore.theme` e aplica a classe `dark` no `<html>`. `PhasesReferenceModal` e `SettingsDrawer` são novos componentes leves que encapsulam os existentes (`PhaseReference`, `Settings`). O dark mode usa variantes `dark:` do Tailwind — o `tailwind.config.js` já tem `darkMode: ['class']`.

**Tech Stack:** React 18, Tailwind CSS (dark: já configurado), Vitest + @testing-library/react, Zustand (settingsStore), lucide-react (ícones Sun/Moon/Settings/HelpCircle)

---

## Task 1: Hook `useTheme.js` — infraestrutura do tema

**Files:**
- Create: `frontend/src/hooks/useTheme.js`
- Create: `frontend/src/hooks/__tests__/useTheme.test.js`

**Step 1: Escrever o teste (RED)**

```javascript
// frontend/src/hooks/__tests__/useTheme.test.js
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { useSettingsStore } from '../../stores/settingsStore';
import { useTheme } from '../useTheme';

describe('useTheme', () => {
  beforeEach(() => {
    // Reset store e DOM
    useSettingsStore.setState({ theme: 'light' });
    document.documentElement.classList.remove('dark');
  });

  it('retorna theme light por padrão', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('light');
    expect(result.current.isDark).toBe(false);
  });

  it('toggleTheme muda para dark e aplica classe no <html>', () => {
    const { result } = renderHook(() => useTheme());
    act(() => { result.current.toggleTheme(); });
    expect(result.current.theme).toBe('dark');
    expect(result.current.isDark).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('toggleTheme de dark para light remove classe do <html>', () => {
    useSettingsStore.setState({ theme: 'dark' });
    const { result } = renderHook(() => useTheme());
    act(() => { result.current.toggleTheme(); });
    expect(result.current.theme).toBe('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('aplica classe dark no mount se theme=dark no store', () => {
    useSettingsStore.setState({ theme: 'dark' });
    renderHook(() => useTheme());
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });
});
```

**Step 2: Rodar para confirmar RED**
```bash
cd frontend && npx vitest run src/hooks/__tests__/useTheme.test.js
```
Esperado: FAIL — `useTheme` não existe.

**Step 3: Implementar `useTheme.js`**

```javascript
// frontend/src/hooks/useTheme.js
import { useEffect } from 'react';
import { useSettingsStore } from '../stores/settingsStore';

export function useTheme() {
  const theme = useSettingsStore((s) => s.theme);
  const updateSetting = useSettingsStore((s) => s.updateSetting);
  const isDark = theme === 'dark';

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  const toggleTheme = () => updateSetting('theme', isDark ? 'light' : 'dark');

  return { theme, isDark, toggleTheme };
}

export default useTheme;
```

**Step 4: Rodar para confirmar GREEN**
```bash
cd frontend && npx vitest run src/hooks/__tests__/useTheme.test.js
```
Esperado: 4 passed.

**Step 5: Commit**
```bash
git add frontend/src/hooks/useTheme.js frontend/src/hooks/__tests__/useTheme.test.js
git commit -m "feat: hook useTheme para gerenciar tema claro/escuro com persistência"
```

---

## Task 2: Reestruturar navegação em `App.jsx`

Remove abas Performance e Configurações. Adiciona toggle ☀️/🌙 e estado para modal das fases.

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/App.test.jsx` (se existir) ou Create: `frontend/src/__tests__/App.nav.test.jsx`

**Step 1: Escrever o teste (RED)**

```javascript
// frontend/src/__tests__/App.nav.test.jsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('App — navegação', () => {
  it('não exibe aba Performance', () => {
    render(<App />);
    expect(screen.queryByRole('tab', { name: /performance/i })).toBeNull();
  });

  it('não exibe aba Configurações', () => {
    render(<App />);
    expect(screen.queryByRole('tab', { name: /configurações/i })).toBeNull();
  });

  it('exibe as 4 abas corretas', () => {
    render(<App />);
    expect(screen.getByRole('tab', { name: /consulta individual/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /busca em lote/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /analytics/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /histórico/i })).toBeInTheDocument();
  });

  it('exibe botão de toggle de tema', () => {
    render(<App />);
    expect(screen.getByRole('button', { name: /alternar tema/i })).toBeInTheDocument();
  });
});
```

**Step 2: Rodar para confirmar RED**
```bash
cd frontend && npx vitest run src/__tests__/App.nav.test.jsx
```

**Step 3: Modificar `App.jsx`**

Substituir o bloco do `<header>` e os imports:

```jsx
// Imports a adicionar/substituir no topo:
import { useState, lazy, Suspense } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { Search, Database, Layers, BarChart3, Sun, Moon, HelpCircle } from 'lucide-react';
import SearchProcess from './components/SearchProcess';
import LoadingFallback from './components/LoadingFallback';
import FeedbackButton from './components/FeedbackButton';
import { searchProcess } from './services/api';
import { useLabels } from './hooks/useLabels';
import { useTheme } from './hooks/useTheme';

// Lazy-loaded:
const ProcessDetails = lazy(() => import('./components/ProcessDetails'));
const BulkSearch     = lazy(() => import('./components/BulkSearch'));
const Dashboard      = lazy(() => import('./components/Dashboard'));
const HistoryTab     = lazy(() => import('./components/HistoryTab'));
const PhasesReferenceModal = lazy(() => import('./components/PhasesReferenceModal'));
// REMOVIDOS: PerformanceDashboard, SettingsComponent
```

Dentro de `function App()`, após os estados existentes, adicionar:
```jsx
const { isDark, toggleTheme } = useTheme();
const [showPhasesModal, setShowPhasesModal] = useState(false);
// Remover 'performance' e 'settings' do activeTab — apenas: 'single'|'bulk'|'analytics'|'history'
```

Substituir o bloco `<nav>` inteiro:
```jsx
<div className="flex items-center gap-3">
  <nav
    className="flex bg-gray-100 dark:bg-gray-700 p-1 rounded-xl border border-gray-200 dark:border-gray-600"
    role="tablist"
    aria-label="Tipo de consulta"
  >
    {[
      { id: 'single',    label: labels.nav.single,    icon: Search    },
      { id: 'bulk',      label: labels.nav.bulk,      icon: Layers    },
      { id: 'analytics', label: labels.nav.analytics, icon: BarChart3 },
      { id: 'history',   label: labels.nav.history,   icon: Database  },
    ].map(({ id, label, icon: Icon }) => (
      <button
        key={id}
        onClick={() => setActiveTab(id)}
        role="tab"
        aria-selected={activeTab === id}
        aria-controls={`tab-panel-${id}`}
        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all
          focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
          ${activeTab === id
            ? 'bg-white dark:bg-gray-800 text-indigo-600 shadow-sm'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
          }`}
      >
        <Icon className="h-4 w-4" aria-hidden="true" />
        <span>{label}</span>
      </button>
    ))}
  </nav>

  {/* Toggle tema */}
  <button
    onClick={toggleTheme}
    aria-label="Alternar tema"
    aria-pressed={isDark}
    className="p-2 rounded-lg text-gray-500 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
  >
    {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
  </button>
</div>
```

Remover os blocos `{activeTab === 'performance' && ...}` e `{activeTab === 'settings' && ...}`.

Adicionar o modal das fases logo antes do `<FeedbackButton />`:
```jsx
{showPhasesModal && (
  <Suspense fallback={null}>
    <PhasesReferenceModal onClose={() => setShowPhasesModal(false)} />
  </Suspense>
)}
```

Passar `onShowPhases` para as abas que precisam do botão:
```jsx
{activeTab === 'single' && (
  <div ...>
    ...
    <SearchProcess onSearch={handleSearch} loading={loading} labels={labels}
                   onShowPhases={() => setShowPhasesModal(true)} />
    ...
  </div>
)}
{activeTab === 'bulk' && (
  <div ...>
    <Suspense ...>
      <BulkSearch onShowPhases={() => setShowPhasesModal(true)} />
    </Suspense>
  </div>
)}
```

**Step 4: Rodar para confirmar GREEN**
```bash
cd frontend && npx vitest run src/__tests__/App.nav.test.jsx
```

**Step 5: Commit**
```bash
git add frontend/src/App.jsx frontend/src/__tests__/App.nav.test.jsx
git commit -m "feat: reestrutura nav — 4 abas, toggle tema, remove Performance e Configurações"
```

---

## Task 3: Componente `PhasesReferenceModal.jsx`

**Files:**
- Create: `frontend/src/components/PhasesReferenceModal.jsx`
- Create: `frontend/src/components/__tests__/PhasesReferenceModal.test.jsx`

**Step 1: Escrever o teste (RED)**

```javascript
// frontend/src/components/__tests__/PhasesReferenceModal.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import PhasesReferenceModal from '../PhasesReferenceModal';

describe('PhasesReferenceModal', () => {
  it('renderiza o título das fases', () => {
    render(<PhasesReferenceModal onClose={() => {}} />);
    expect(screen.getByText(/fases processuais/i)).toBeInTheDocument();
  });

  it('chama onClose ao clicar no botão fechar', () => {
    const onClose = vi.fn();
    render(<PhasesReferenceModal onClose={onClose} />);
    fireEvent.click(screen.getByRole('button', { name: /fechar/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('fecha ao pressionar Escape', () => {
    const onClose = vi.fn();
    render(<PhasesReferenceModal onClose={onClose} />);
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('tem atributos de acessibilidade corretos', () => {
    render(<PhasesReferenceModal onClose={() => {}} />);
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby');
  });
});
```

**Step 2: Rodar para confirmar RED**
```bash
cd frontend && npx vitest run src/components/__tests__/PhasesReferenceModal.test.jsx
```

**Step 3: Implementar `PhasesReferenceModal.jsx`**

```jsx
// frontend/src/components/PhasesReferenceModal.jsx
import { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import PhaseReference from './PhaseReference';

export default function PhasesReferenceModal({ onClose }) {
  const closeRef = useRef(null);

  // Fechar com Escape
  useEffect(() => {
    const handle = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handle);
    closeRef.current?.focus();
    return () => document.removeEventListener('keydown', handle);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      aria-hidden="false"
    >
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="phases-modal-title"
        className="relative z-10 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl
                   w-full max-w-4xl max-h-[90vh] overflow-y-auto mx-4"
      >
        {/* Header fixo */}
        <div className="sticky top-0 z-10 flex items-center justify-between
                        bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700
                        px-6 py-4 rounded-t-2xl">
          <h2 id="phases-modal-title"
              className="text-lg font-bold text-gray-900 dark:text-white">
            Fases Processuais
          </h2>
          <button
            ref={closeRef}
            onClick={onClose}
            aria-label="Fechar"
            className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200
                       hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors
                       focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Conteúdo */}
        <div className="p-2">
          <PhaseReference />
        </div>
      </div>
    </div>
  );
}
```

**Step 4: Rodar para confirmar GREEN**
```bash
cd frontend && npx vitest run src/components/__tests__/PhasesReferenceModal.test.jsx
```

**Step 5: Commit**
```bash
git add frontend/src/components/PhasesReferenceModal.jsx \
        frontend/src/components/__tests__/PhasesReferenceModal.test.jsx
git commit -m "feat: modal PhasesReferenceModal com as 15 fases processuais"
```

---

## Task 4: Botão "? Ver fases" em `SearchProcess.jsx` e `BulkSearch.jsx`

**Files:**
- Modify: `frontend/src/components/SearchProcess.jsx`
- Modify: `frontend/src/components/BulkSearch.jsx`

**Step 1: Escrever os testes (RED)**

```javascript
// Adicionar ao teste existente de SearchProcess ou criar novo arquivo
// frontend/src/components/__tests__/SearchProcess.phases.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SearchProcess from '../SearchProcess';

const labels = {
  search: { placeholder: 'Nº', button: 'Consultar', loading: 'Buscando...' }
};

it('exibe botão "Ver fases" e chama onShowPhases ao clicar', () => {
  const onShowPhases = vi.fn();
  render(<SearchProcess onSearch={() => {}} loading={false} labels={labels} onShowPhases={onShowPhases} />);
  const btn = screen.getByRole('button', { name: /ver fases/i });
  expect(btn).toBeInTheDocument();
  fireEvent.click(btn);
  expect(onShowPhases).toHaveBeenCalledOnce();
});
```

```javascript
// frontend/src/components/__tests__/BulkSearch.phases.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import BulkSearch from '../BulkSearch';

it('exibe botão "Ver fases" e chama onShowPhases ao clicar', () => {
  const onShowPhases = vi.fn();
  render(<BulkSearch onShowPhases={onShowPhases} />);
  const btn = screen.getByRole('button', { name: /ver fases/i });
  fireEvent.click(btn);
  expect(onShowPhases).toHaveBeenCalledOnce();
});
```

**Step 2: Rodar para confirmar RED**
```bash
cd frontend && npx vitest run src/components/__tests__/SearchProcess.phases.test.jsx \
                              src/components/__tests__/BulkSearch.phases.test.jsx
```

**Step 3: Adicionar botão em `SearchProcess.jsx`**

Adicionar a prop `onShowPhases` na assinatura da função e inserir o botão logo abaixo do campo de busca (ou abaixo do botão "Consultar"):

```jsx
// Adicionar import
import { HelpCircle } from 'lucide-react';

// Na assinatura:
function SearchProcess({ onSearch, loading, labels, onShowPhases }) {

// Inserir botão após o form de busca:
<div className="flex justify-end mt-2">
  <button
    type="button"
    onClick={onShowPhases}
    className="flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400
               hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
  >
    <HelpCircle className="h-3.5 w-3.5" />
    Ver fases
  </button>
</div>
```

**Step 4: Adicionar botão em `BulkSearch.jsx`**

Adicionar a prop `onShowPhases` e inserir botão no cabeçalho da seção de resultados:

```jsx
import { HelpCircle } from 'lucide-react';

function BulkSearch({ onShowPhases }) {
  // ...

  // No JSX do cabeçalho da seção de resultados, adicionar ao lado do título:
  <div className="flex items-center justify-between mb-4">
    <h2 className="text-lg font-bold text-gray-900 dark:text-white">Resultados</h2>
    <button
      type="button"
      onClick={onShowPhases}
      className="flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400
                 hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
    >
      <HelpCircle className="h-3.5 w-3.5" />
      Ver fases
    </button>
  </div>
```

**Step 5: Rodar para confirmar GREEN**
```bash
cd frontend && npx vitest run src/components/__tests__/SearchProcess.phases.test.jsx \
                              src/components/__tests__/BulkSearch.phases.test.jsx
```

**Step 6: Commit**
```bash
git add frontend/src/components/SearchProcess.jsx \
        frontend/src/components/BulkSearch.jsx \
        frontend/src/components/__tests__/SearchProcess.phases.test.jsx \
        frontend/src/components/__tests__/BulkSearch.phases.test.jsx
git commit -m "feat: botão 'Ver fases' em SearchProcess e BulkSearch"
```

---

## Task 5: `SettingsDrawer.jsx` + integração em `Dashboard.jsx`

**Files:**
- Create: `frontend/src/components/SettingsDrawer.jsx`
- Create: `frontend/src/components/__tests__/SettingsDrawer.test.jsx`
- Modify: `frontend/src/components/Dashboard.jsx`

**Step 1: Escrever o teste (RED)**

```javascript
// frontend/src/components/__tests__/SettingsDrawer.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SettingsDrawer from '../SettingsDrawer';

describe('SettingsDrawer', () => {
  it('renderiza o título "Configurações de Dados"', () => {
    render(<SettingsDrawer onClose={() => {}} />);
    expect(screen.getByText(/configurações de dados/i)).toBeInTheDocument();
  });

  it('chama onClose ao clicar no botão fechar', () => {
    const onClose = vi.fn();
    render(<SettingsDrawer onClose={onClose} />);
    fireEvent.click(screen.getByRole('button', { name: /fechar configurações/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('chama onClose ao pressionar Escape', () => {
    const onClose = vi.fn();
    render(<SettingsDrawer onClose={onClose} />);
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('tem role=dialog e aria-modal=true', () => {
    render(<SettingsDrawer onClose={() => {}} />);
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true');
  });
});
```

**Step 2: Rodar para confirmar RED**
```bash
cd frontend && npx vitest run src/components/__tests__/SettingsDrawer.test.jsx
```

**Step 3: Implementar `SettingsDrawer.jsx`**

```jsx
// frontend/src/components/SettingsDrawer.jsx
import { useEffect, useRef, lazy, Suspense } from 'react';
import { X } from 'lucide-react';

const SettingsComponent = lazy(() => import('./Settings'));

export default function SettingsDrawer({ onClose }) {
  const closeRef = useRef(null);

  useEffect(() => {
    const handle = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handle);
    closeRef.current?.focus();
    return () => document.removeEventListener('keydown', handle);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex justify-end" aria-hidden="false">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer panel */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="settings-drawer-title"
        className="relative z-10 w-full max-w-lg h-full bg-white dark:bg-gray-900
                   shadow-2xl overflow-y-auto flex flex-col
                   animate-in slide-in-from-right-4 duration-300"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4
                        border-b border-gray-200 dark:border-gray-700 shrink-0">
          <h2 id="settings-drawer-title"
              className="text-lg font-bold text-gray-900 dark:text-white">
            ⚙ Configurações de Dados
          </h2>
          <button
            ref={closeRef}
            onClick={onClose}
            aria-label="Fechar configurações"
            className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200
                       hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors
                       focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Conteúdo */}
        <div className="flex-1 overflow-y-auto">
          <Suspense fallback={<div className="p-8 text-center text-gray-400">Carregando...</div>}>
            <SettingsComponent />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
```

**Step 4: Adicionar botão ⚙ e drawer em `Dashboard.jsx`**

```jsx
// Adicionar import no topo de Dashboard.jsx:
import { RefreshCw, Settings } from 'lucide-react';  // Settings já pode existir
import { useState, lazy, Suspense } from 'react';
const SettingsDrawer = lazy(() => import('./SettingsDrawer'));

// No componente, adicionar estado:
const [showSettingsDrawer, setShowSettingsDrawer] = useState(false);

// No header do Dashboard, ao lado do botão "Atualizar", adicionar:
<button
  onClick={() => setShowSettingsDrawer(true)}
  aria-label="Abrir configurações de dados"
  className="p-2 rounded-lg text-gray-500 dark:text-gray-300
             hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors
             focus:outline-none focus:ring-2 focus:ring-indigo-500"
>
  <Settings className="h-5 w-5" />
</button>

// Antes do return, adicionar o drawer:
{showSettingsDrawer && (
  <Suspense fallback={null}>
    <SettingsDrawer onClose={() => setShowSettingsDrawer(false)} />
  </Suspense>
)}
```

**Step 5: Rodar para confirmar GREEN**
```bash
cd frontend && npx vitest run src/components/__tests__/SettingsDrawer.test.jsx
```

**Step 6: Commit**
```bash
git add frontend/src/components/SettingsDrawer.jsx \
        frontend/src/components/__tests__/SettingsDrawer.test.jsx \
        frontend/src/components/Dashboard.jsx
git commit -m "feat: drawer de configurações SQL no Analytics, acessível por ícone ⚙"
```

---

## Task 6: Dark mode — `App.jsx`, header e footer

**Files:**
- Modify: `frontend/src/App.jsx`

**Step 1: Aplicar variantes `dark:` no wrapper principal, header e footer**

Substituir as classes de cor hardcoded pelas equivalentes com `dark:`:

```jsx
// Wrapper principal:
<div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col">

// <header>:
<header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30 shadow-sm">

// Título do app:
<h1 className="text-xl font-extrabold text-gray-900 dark:text-white tracking-tight leading-none">

// Subtítulo:
<p className="text-[10px] text-indigo-600 dark:text-indigo-400 font-bold ...">

// <footer>:
<footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 mt-auto">

// Texto do footer:
<p className="text-gray-400 dark:text-gray-500 text-sm">

// Hero title:
<h2 className="text-4xl font-extrabold text-gray-900 dark:text-white sm:text-5xl">

// Hero subtitle:
<p className="max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
```

**Step 2: Verificar visualmente**

```bash
cd frontend && npm run dev
# Abrir http://localhost:5173
# Clicar no toggle 🌙 — app deve escurecer
# Clicar novamente ☀️ — deve voltar ao claro
# Recarregar página — tema deve persistir
```

**Step 3: Commit**
```bash
git add frontend/src/App.jsx
git commit -m "feat: dark mode no App.jsx — wrapper, header e footer"
```

---

## Task 7: Dark mode — `SearchProcess.jsx` e `ProcessDetails.jsx`

**Files:**
- Modify: `frontend/src/components/SearchProcess.jsx`
- Modify: `frontend/src/components/ProcessDetails.jsx`

**Step 1: Aplicar `dark:` em `SearchProcess.jsx`**

Localizar e substituir as classes de cor principais:
```jsx
// Cards e containers:
className="... bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"

// Labels e texto:
className="... text-gray-700 dark:text-gray-200"
className="... text-gray-500 dark:text-gray-400"

// Input:
className="... bg-white dark:bg-gray-700 text-gray-900 dark:text-white
           border-gray-300 dark:border-gray-600
           placeholder-gray-400 dark:placeholder-gray-500"

// Botão secundário (Ver fases):
className="... text-indigo-600 dark:text-indigo-400"
```

**Step 2: Aplicar `dark:` em `ProcessDetails.jsx`**

```jsx
// Container principal:
className="... bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"

// Seções/cards internos:
className="... bg-gray-50 dark:bg-gray-700"

// Texto de campo:
className="... text-gray-900 dark:text-white"
className="... text-gray-500 dark:text-gray-400"

// Labels:
className="... text-gray-600 dark:text-gray-300"

// Badges de fase — manter cores existentes, que já têm bom contraste
```

**Step 3: Verificar visualmente**

```bash
cd frontend && npm run dev
# Ativar modo escuro e navegar pela tela de Consulta Individual
# Verificar: campo de busca, resultado do processo, todos os campos visíveis
```

**Step 4: Commit**
```bash
git add frontend/src/components/SearchProcess.jsx \
        frontend/src/components/ProcessDetails.jsx
git commit -m "feat: dark mode em SearchProcess e ProcessDetails"
```

---

## Task 8: Dark mode — `BulkSearch.jsx`

**Files:**
- Modify: `frontend/src/components/BulkSearch.jsx`

**Step 1: Aplicar `dark:` no BulkSearch**

```jsx
// Container:
className="... bg-white dark:bg-gray-800"

// Cabeçalho da tabela:
className="... bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300"

// Linhas da tabela:
className="... hover:bg-gray-50 dark:hover:bg-gray-700 border-gray-200 dark:border-gray-700"

// Texto:
className="... text-gray-900 dark:text-white"
className="... text-gray-500 dark:text-gray-400"

// Área de upload/dropzone:
className="... bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600"
```

**Step 2: Verificar visualmente**
```bash
# Ativar dark mode e navegar para Busca em Lote
# Verificar área de upload, tabela de resultados, badges de fase
```

**Step 3: Commit**
```bash
git add frontend/src/components/BulkSearch.jsx
git commit -m "feat: dark mode em BulkSearch"
```

---

## Task 9: Dark mode — `Dashboard.jsx`

**Files:**
- Modify: `frontend/src/components/Dashboard.jsx`

**Step 1: Aplicar `dark:` no Dashboard**

```jsx
// Container geral:
className="... bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700"

// Cards de métricas:
className="... bg-white dark:bg-gray-800 shadow-sm border border-gray-100 dark:border-gray-700"

// Títulos:
className="... text-gray-900 dark:text-white"
className="... text-gray-500 dark:text-gray-400"

// Gráficos — fundo das barras:
className="... bg-gray-100 dark:bg-gray-700"

// Header do Dashboard (gradient) — manter gradiente, é legível em ambos os temas

// Tabela sr-only (acessibilidade) — não requer mudança
```

**Step 2: Verificar visualmente**
```bash
# Ativar dark mode e navegar para Analytics/BI
# Verificar cards de métricas, gráficos de barras, timeline
```

**Step 3: Commit**
```bash
git add frontend/src/components/Dashboard.jsx
git commit -m "feat: dark mode em Dashboard (Analytics/BI)"
```

---

## Task 10: Dark mode — `HistoryTab.jsx` e componentes restantes

**Files:**
- Modify: `frontend/src/components/HistoryTab.jsx`
- Modify: `frontend/src/components/PhaseReference.jsx` (para modal)
- Modify: `frontend/src/components/Settings.jsx` (para drawer)

**Step 1: Aplicar `dark:` no `HistoryTab.jsx`**

```jsx
// Container:
className="... bg-white dark:bg-gray-800"

// Itens do histórico:
className="... hover:bg-gray-50 dark:hover:bg-gray-700 border-gray-200 dark:border-gray-700"

// Texto:
className="... text-gray-900 dark:text-white"
className="... text-gray-500 dark:text-gray-400"
```

**Step 2: Aplicar `dark:` no `PhaseReference.jsx`**

```jsx
// Cards de grupo:
className="... bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700"

// Cabeçalho do grupo:
className="... bg-gray-50 dark:bg-gray-700 border-gray-100 dark:border-gray-600"

// Texto:
className="... text-gray-900 dark:text-white"
className="... text-gray-600 dark:text-gray-400"

// Info box:
className="... bg-blue-50 dark:bg-blue-900/20 border-blue-500"
className="... text-blue-900 dark:text-blue-200"
className="... text-blue-800 dark:text-blue-300"
```

**Step 3: Aplicar `dark:` no `Settings.jsx`**

```jsx
// Container:
className="... bg-white dark:bg-gray-800"

// Labels:
className="... text-gray-700 dark:text-gray-200"

// Inputs:
className="... bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600
           text-gray-900 dark:text-white"

// Seção expansível:
className="... bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600"
```

**Step 4: Verificar visualmente**
```bash
# Ativar dark mode e navegar para Histórico
# Abrir drawer de Configurações (Analytics ⚙)
# Abrir modal de Fases (Consulta Individual — Ver fases)
```

**Step 5: Commit final**
```bash
git add frontend/src/components/HistoryTab.jsx \
        frontend/src/components/PhaseReference.jsx \
        frontend/src/components/Settings.jsx
git commit -m "feat: dark mode em HistoryTab, PhaseReference e Settings"
```

---

## Task 11: Rodar a suite de testes completa e verificar

**Step 1: Rodar todos os testes do frontend**
```bash
cd frontend && npx vitest run
```
Esperado: todos os testes passando (exceto pré-existentes já conhecidos como falhando).

**Step 2: Build de produção**
```bash
cd frontend && npm run build
```
Esperado: build sem erros.

**Step 3: Verificação manual final**

Cheklist visual com dark mode ativado:
- [ ] Nav exibe 4 abas + toggle ☀️/🌙
- [ ] Performance e Configurações não aparecem na nav
- [ ] Toggle persiste o tema após recarregar a página
- [ ] Botão "? Ver fases" visível em Consulta Individual e Busca em Lote
- [ ] Modal das fases abre, exibe as 15 fases, fecha com ✕ e Escape
- [ ] Ícone ⚙ no header do Analytics abre o drawer de configurações
- [ ] Drawer de configurações fecha com ✕, Escape e clique no overlay
- [ ] Todas as telas visíveis e legíveis no modo escuro

**Step 4: Commit de encerramento**
```bash
git add -A
git commit -m "chore: verificação final — layout, acessibilidade e dark mode completo"
```
