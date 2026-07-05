# Correção da Suíte de Testes Frontend Pré-Existente Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir as 58 falhas pré-existentes da suíte `vitest` do frontend (de 482 testes), descobertas ao estabelecer a baseline para o plano `2026-07-04-fase-processual-doctree-adaptation.md`. Nenhuma dessas falhas foi causada por esse plano nem pela instalação de dependências (`npm install --legacy-peer-deps`) — todas são dívida técnica acumulada de refatorações anteriores (migração do modelo de fases 01-15 para o modelo hierárquico `STAGES`/`SUBSTAGES`, adição de `getConfirmedProcesses`/`getLatestCorrections` ao fluxo de histórico, adição da aba "Configurações").

**Architecture:** Duas categorias de correção. (1) **Testes desatualizados** (mocks ou asserções que não acompanharam uma refatoração de produção): corrige-se apenas o teste, sem tocar no componente. (2) **Regressão de acessibilidade real**: o componente `Dashboard.jsx` perdeu, na migração para o modelo hierárquico, toda a marcação ARIA (`role="meter"`, `aria-label`, tabelas `sr-only`, `section[aria-labelledby]`) que a suíte `DashboardA11y.test.jsx`/`SemanticHTML.test.jsx` (stories REM-028/REM-032) documentam como requisito — aqui a correção é no componente, restaurando o comportamento, não apenas no teste. Cada task é independente e termina com a suíte daquele arquivo verde; a Task 9 roda a suíte completa (backend + frontend) como regressão final.

**Tech Stack:** React 18, Vitest 4, @testing-library/react, @testing-library/user-event, Tailwind CSS (classe utilitária `sr-only` já disponível via `frontend/src/index.css`/Tailwind base).

---

## Diagnóstico por arquivo

| Arquivo | Falhas | Causa raiz | Tipo de correção |
|---|---|---|---|
| `frontend/src/tests/HistoryTab.test.jsx` | 12 | `beforeEach` não mocka `getConfirmedProcesses`/`getLatestCorrections`, que `HistoryTab.jsx` chama em `Promise.all` desde que o fluxo de confirmação/correção de fase foi adicionado; a promise resolve `undefined`, `undefined.confirmed_processes` lança, o `catch` zera o histórico | Só teste |
| `frontend/src/tests/ComponentMigration.test.jsx` | 1 | Asserção busca o texto antigo "Processos por Fase"; o título atual (pós-migração hierárquica) é "Processos por Estágio" | Só teste |
| `frontend/src/tests/Dashboard.test.jsx` | 2 (TC-11, TC-17) | Mock de `stats` usa o campo antigo `phases`; `Dashboard.jsx` lê `stats.stages` (formato hierárquico) — a seção de estágios nunca recebe dados nesses dois testes | Só teste |
| `frontend/src/tests/DashboardA11y.test.jsx` | 15 | Duas causas empilhadas: (a) mock de `stats` usa `phases` em vez de `stages`; (b) `Dashboard.jsx` não emite mais `role="meter"`, `aria-label`, `figure[aria-label]` nem tabelas `sr-only` desde a migração hierárquica | Teste + componente |
| `frontend/src/tests/SemanticHTML.test.jsx` | 2 | Mesma causa (b) acima — `section[aria-labelledby]`/`h2[id]` não existem mais | Componente (mock também precisa do campo `stages`) |
| `frontend/src/__tests__/App.nav.test.jsx` | 1 | Teste "não exibe aba Configurações" — a aba Configurações é uma feature completa e intencional (`SettingsComponent`, lazy-loaded, painel funcional); o teste é anterior à sua adição e nunca foi atualizado | Só teste |
| `frontend/src/tests/PhaseReference.test.jsx` | 25 | Suíte inteira testa o componente antigo (fases 01-15 em lista plana, legenda de cores, ícones por tipo); `PhaseReference.jsx` foi totalmente reescrito para o modelo hierárquico (`STAGES`/`SUBSTAGES`/`TRANSIT_OPTIONS`) — nenhuma asserção do arquivo atual bate com o componente atual | Só teste (reescrita completa) |

---

## Task 1: Corrigir mocks de API em `HistoryTab.test.jsx`

**Files:**
- Modify: `frontend/src/tests/HistoryTab.test.jsx:47-50`

- [ ] **Step 1: Rodar a suíte para confirmar a falha atual**

Run: `cd frontend && npx vitest run src/tests/HistoryTab.test.jsx`
Expected: FAIL — 12 testes falhando (TC-7, TC-8, TC-9, TC-10, TC-11, TC-12, TC-13, TC-16, TC-17, TC-18, TC-19, TC-20), a maioria com `Unable to find an element with the text: ...` porque `HistoryTab` mostra o estado vazio em vez da lista.

- [ ] **Step 2: Adicionar os mocks que faltam no `beforeEach`**

Old:
```js
    beforeEach(() => {
        vi.clearAllMocks();
        global.confirm.mockReturnValue(true); // Default: user confirms
    });
```

New:
```js
    beforeEach(() => {
        vi.clearAllMocks();
        global.confirm.mockReturnValue(true); // Default: user confirms
        // HistoryTab.loadHistory() chama estas três APIs em Promise.all;
        // sem mock, as duas abaixo resolvem `undefined` e o acesso a
        // `confirmed.confirmed_processes` lança, esvaziando o histórico.
        api.getConfirmedProcesses.mockResolvedValue({ confirmed_processes: [] });
        api.getLatestCorrections.mockResolvedValue({ corrections: {} });
    });
```

- [ ] **Step 3: Rodar a suíte novamente**

Run: `cd frontend && npx vitest run src/tests/HistoryTab.test.jsx`
Expected: PASS — 20/20 testes.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/tests/HistoryTab.test.jsx
git commit -m "test: mock getConfirmedProcesses/getLatestCorrections in HistoryTab tests"
```

---

## Task 2: Corrigir asserção desatualizada em `ComponentMigration.test.jsx`

**Files:**
- Modify: `frontend/src/tests/ComponentMigration.test.jsx:106-113`

- [ ] **Step 1: Rodar a suíte para confirmar a falha atual**

Run: `cd frontend && npx vitest run src/tests/ComponentMigration.test.jsx`
Expected: FAIL em `Dashboard Component Migration — REM-035 > displays phase chart section with Card` — `Unable to find an element with the text: Processos por Fase`.

- [ ] **Step 2: Atualizar o teste para o título atual**

Old:
```js
  it('displays phase chart section with Card', async () => {
    render(<Dashboard />);
    await screen.findByText('Processos por Fase');

    const phaseSection = screen.getByText('Processos por Fase').closest('section');
    expect(phaseSection).toBeTruthy();
    expect(phaseSection.className).toContain('bg-white');
  });
```

New:
```js
  it('displays stage chart section with Card', async () => {
    render(<Dashboard />);
    await screen.findByText('Processos por Estágio');

    const stageSection = screen.getByText('Processos por Estágio').closest('section');
    expect(stageSection).toBeTruthy();
    expect(stageSection.className).toContain('bg-white');
  });
```

- [ ] **Step 3: Rodar a suíte novamente**

Run: `cd frontend && npx vitest run src/tests/ComponentMigration.test.jsx`
Expected: PASS — todos os testes do arquivo.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/tests/ComponentMigration.test.jsx
git commit -m "test: update ComponentMigration assertion to hierarchical stage title"
```

---

## Task 3: Corrigir `Dashboard.test.jsx` TC-11/TC-17 (dados de `stages` + mock de `phaseColors`)

**Files:**
- Modify: `frontend/src/tests/Dashboard.test.jsx:24-31` (mock de `phaseColors`)
- Modify: `frontend/src/tests/Dashboard.test.jsx:192-203` (TC-11)
- Modify: `frontend/src/tests/Dashboard.test.jsx:310-322` (TC-17)

- [ ] **Step 1: Rodar a suíte para confirmar a falha atual**

Run: `cd frontend && npx vitest run src/tests/Dashboard.test.jsx`
Expected: FAIL em TC-11 (`renders phase statistics`) e TC-17 (`renders all phase names using utility`) — `container.textContent` nunca contém `Fase 01`, porque `mockStatsData.phases` não é lido por `Dashboard.jsx` (que usa `stats.stages`).

- [ ] **Step 2: Ampliar o mock de `phaseColors` com as funções de estágio**

`Dashboard.jsx` importa `getStageColorClasses`/`getStageProgressBarClasses` de `../utils/phaseColors`. O mock atual do arquivo substitui o módulo inteiro e não inclui essas duas funções — assim que `stats.stages` tiver dados (Step 3), o componente vai chamá-las e quebrar com `TypeError: getStageColorClasses is not a function` se elas não estiverem no mock.

Old:
```js
// Mock phase color utilities
vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn((phase) => ({
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-300',
    })),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
}));
```

New:
```js
// Mock phase color utilities
vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn((phase) => ({
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-300',
    })),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
    getStageColorClasses: vi.fn(() => 'bg-blue-100 text-blue-800'),
    getStageProgressBarClasses: vi.fn(() => 'bg-blue-500'),
}));
```

- [ ] **Step 3: Corrigir TC-11 para usar o formato `stages`**

Old:
```js
        it('TC-11: renders phase statistics', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                // Mocked getPhaseDisplayName returns "Fase {phase}"
                expect(container.textContent).toContain('Fase 01');
            });

            expect(container.textContent).toContain('Fase 10');
        });
```

New:
```js
        it('TC-11: renders stage statistics with counts', async () => {
            api.getStats.mockResolvedValue({
                ...mockStatsData,
                stages: [
                    { stage: 1, count: 30, substages: [] },
                    { stage: 2, count: 70, substages: [] },
                ],
            });

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                // STAGES[1].label === 'Conhecimento' (constants/phases.js)
                expect(container.textContent).toContain('Conhecimento');
            });

            expect(container.textContent).toContain('30');
            expect(container.textContent).toContain('Execução');
            expect(container.textContent).toContain('70');
        });
```

- [ ] **Step 4: Corrigir TC-17 para testar `SUBSTAGES` em vez do utilitário removido**

`Dashboard.jsx` não chama mais `getPhaseDisplayName` para rotular estágios — ele lê `STAGES`/`SUBSTAGES` diretamente de `constants/phases.js`. A asserção sobre a chamada ao utilitário não tem mais sentido; o teste passa a validar que os rótulos de subfase (`SUBSTAGES`) aparecem.

Old:
```js
        it('TC-17: renders all phase names using utility', async () => {
            api.getStats.mockResolvedValue(mockStatsData);

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('Fase 01');
            });

            // Verify phase display name utility was called
            const { getPhaseDisplayName } = await import('../utils/phaseColors');
            expect(getPhaseDisplayName).toHaveBeenCalled();
        });
```

New:
```js
        it('TC-17: renders substage names from SUBSTAGES constant', async () => {
            api.getStats.mockResolvedValue({
                ...mockStatsData,
                stages: [
                    { stage: 1, count: 30, substages: [{ substage: '1.1', count: 30 }] },
                ],
            });

            const { container } = render(<Dashboard />);

            await waitFor(() => {
                expect(container.textContent).toContain('Conhecimento');
            });

            // SUBSTAGES['1.1'].label === 'Antes da Sentença' (constants/phases.js)
            expect(container.textContent).toContain('Antes da Sentença');
        });
```

- [ ] **Step 5: Rodar a suíte novamente**

Run: `cd frontend && npx vitest run src/tests/Dashboard.test.jsx`
Expected: PASS — 22/22 testes.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/tests/Dashboard.test.jsx
git commit -m "test: fix Dashboard TC-11/TC-17 to use hierarchical stages mock data"
```

---

## Task 4: Restaurar acessibilidade dos gráficos em `Dashboard.jsx`

**Files:**
- Modify: `frontend/src/components/Dashboard.jsx:103-105` (hoist `maxClassCount`)
- Modify: `frontend/src/components/Dashboard.jsx:186-335` (as 4 seções de gráfico)

Esta task não segue o ciclo red-green por teste unitário isolado, porque a "asserção" já existe (em `DashboardA11y.test.jsx` e `SemanticHTML.test.jsx`, corrigidas nas Tasks 5 e 6) — o código de produção é que está incompleto. Implemente aqui; as Tasks 5/6 ajustam os mocks dos testes e então tudo é verificado junto.

- [ ] **Step 1: Rodar as duas suítes afetadas para registrar a baseline de falha**

Run: `cd frontend && npx vitest run src/tests/DashboardA11y.test.jsx src/tests/SemanticHTML.test.jsx`
Expected: FAIL — 17 testes (15 + 2), nenhum `figure[aria-label]`, `[role="meter"]`, `table.sr-only` ou `section[aria-labelledby]` encontrado.

- [ ] **Step 2: Adicionar `maxClassCount` junto aos outros `max*`**

Old (`Dashboard.jsx:103-105`):
```js
    const maxTribunalCount = Math.max(...stats.tribunals.map(t => t.count), 1);
    const maxTimelineCount = Math.max(...stats.timeline.map(t => t.count), 1);
    const maxStageCount = Math.max(...(stats.stages?.map(s => s.count) || []), 1);
```

New:
```js
    const maxTribunalCount = Math.max(...stats.tribunals.map(t => t.count), 1);
    const maxTimelineCount = Math.max(...stats.timeline.map(t => t.count), 1);
    const maxStageCount = Math.max(...(stats.stages?.map(s => s.count) || []), 1);
    const maxClassCount = Math.max(...(stats.classes?.map(c => c.count) || []), 1);
```

- [ ] **Step 3: Reescrever as 4 seções de gráfico com `figure[aria-label]`, `role="meter"` e tabelas `sr-only`**

Old (`Dashboard.jsx:186-335`, bloco completo das duas `<div className="grid ...">` de gráficos):
```jsx
            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Tribunals Chart */}
                <section className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                    <h2 className="text-lg font-bold text-gray-900 mb-4">Processos por Tribunal</h2>
                    {stats.tribunals.length > 0 ? (
                        <figure>
                            <ul className="space-y-3 list-none p-0">
                                {stats.tribunals.map((tribunal, idx) => (
                                    <li key={idx} className="space-y-1">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-semibold text-gray-700 truncate mr-2">{tribunal.tribunal_name}</span>
                                            <span className="font-bold text-indigo-600">{tribunal.count.toLocaleString()}</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                            <div
                                                className="bg-gradient-to-r from-indigo-500 to-indigo-600 h-3 rounded-full transition-all duration-500"
                                                style={{ width: `${(tribunal.count / maxTribunalCount) * 100}%` }}
                                            />
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </figure>
                    ) : (
                        <p className="text-gray-600 text-sm italic">Nenhum dado disponível</p>
                    )}
                </section>

                {/* Stages Chart — Hierarchical */}
                <section className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-gray-100 dark:border-slate-700 p-6">
                    <div className="mb-6">
                        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Processos por Estágio</h2>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Classificação hierárquica: estágio / subfase
                        </p>
                    </div>

                    {stagesWithLabels.length > 0 ? (
                        <figure>
                            <ul className="space-y-5 list-none p-0">
                                {stagesWithLabels.map((stage) => (
                                    <li key={stage.stage}>
                                        {/* Stage bar */}
                                        <div className="flex justify-between items-center text-sm mb-1">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${getStageColorClasses(stage.stage)}`}>
                                                {stage.stage}. {stage.label}
                                            </span>
                                            <span className="font-bold text-gray-800 dark:text-gray-200">
                                                {stage.count.toLocaleString()}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-100 dark:bg-slate-700 rounded-full h-3 overflow-hidden mb-2">
                                            <div
                                                className={`h-3 rounded-full transition-all duration-500 ${getStageProgressBarClasses(stage.stage)}`}
                                                style={{ width: `${(stage.count / maxStageCount) * 100}%` }}
                                            />
                                        </div>
                                        {/* Substages */}
                                        {stage.substages.length > 0 && (
                                            <ul className="ml-4 space-y-1 list-none p-0">
                                                {stage.substages.map((ss) => (
                                                    <li key={ss.substage || 'null'} className="flex items-center gap-2 text-xs">
                                                        <span className="text-gray-400 font-mono w-6 shrink-0">{ss.substage || '—'}</span>
                                                        <span className="text-gray-600 dark:text-gray-400 flex-1 truncate">{ss.label}</span>
                                                        <span className="font-semibold text-gray-700 dark:text-gray-300 tabular-nums">{ss.count.toLocaleString()}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </figure>
                    ) : (
                        <p className="text-gray-500 dark:text-gray-400 text-sm italic">
                            Nenhum dado hierárquico disponível. Consulte processos primeiro.
                        </p>
                    )}
                </section>
            </div>

            {/* Process Classes Chart - REPLACING the old redundant Nature filter with actual class stats */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <section className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-bold text-gray-900">Processos por Classe</h2>
                        <div className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-xs font-bold flex items-center">
                            <Filter className="h-3 w-3 mr-1" />
                            {stats.classes?.length || 0} Classes
                        </div>
                    </div>
                    {stats.classes && stats.classes.length > 0 ? (
                        <div className="max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                            <ul className="space-y-3 list-none p-0">
                                {stats.classes.map((cls, idx) => {
                                    const maxClassCount = Math.max(...stats.classes.map(c => c.count), 1);
                                    return (
                                        <li key={idx} className="space-y-1">
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="font-semibold text-gray-700 truncate mr-2" title={cls.class_nature}>
                                                    {cls.class_nature}
                                                </span>
                                                <span className="font-bold text-indigo-600">{cls.count.toLocaleString()}</span>
                                            </div>
                                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                                                <div
                                                    className="bg-indigo-400 h-2 rounded-full transition-all duration-500"
                                                    style={{ width: `${(cls.count / maxClassCount) * 100}%` }}
                                                />
                                            </div>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    ) : (
                        <p className="text-gray-600 text-sm italic">Nenhum dado categorizado</p>
                    )}
                </section>

                {/* Timeline Chart */}
                {stats.timeline && stats.timeline.length > 0 && (
                    <section className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                        <h2 className="text-lg font-bold text-gray-900 mb-4">Distribuição Temporal (Últimos 12 meses)</h2>
                        <figure>
                            <div className="flex items-end justify-between space-x-2 h-64 px-2">
                                {stats.timeline.map((item, idx) => {
                                    const height = (item.count / maxTimelineCount) * 100;
                                    return (
                                        <div key={idx} className="flex-1 flex flex-col items-center group">
                                            <div className="w-full flex flex-col items-center justify-end h-full pb-2 relative">
                                                <div className="absolute -top-8 bg-indigo-900 text-white text-[10px] py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                                    {item.count} processos
                                                </div>
                                                <div
                                                    className="w-full bg-gradient-to-t from-indigo-500 to-indigo-400 rounded-t-lg hover:from-indigo-600 hover:to-indigo-500 transition-all cursor-pointer"
                                                    style={{ height: `${height || 2}%` }}
                                                />
                                            </div>
                                            <span className="text-[10px] text-gray-600 font-semibold mt-2 transform -rotate-45 origin-top-left">
                                                {item.month}
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                        </figure>
                    </section>
                )}
            </div>
```

New:
```jsx
            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Tribunals Chart */}
                <section className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6" aria-labelledby="tribunals-heading">
                    <h2 id="tribunals-heading" className="text-lg font-bold text-gray-900 mb-4">Processos por Tribunal</h2>
                    {stats.tribunals.length > 0 ? (
                        <figure aria-label={`Distribuição de processos por tribunal (${stats.tribunals.length} tribunais)`}>
                            <ul className="space-y-3 list-none p-0">
                                {stats.tribunals.map((tribunal, idx) => (
                                    <li key={idx} className="space-y-1">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-semibold text-gray-700 truncate mr-2">{tribunal.tribunal_name}</span>
                                            <span className="font-bold text-indigo-600">{tribunal.count.toLocaleString()}</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                            <div
                                                className="bg-gradient-to-r from-indigo-500 to-indigo-600 h-3 rounded-full transition-all duration-500"
                                                style={{ width: `${(tribunal.count / maxTribunalCount) * 100}%` }}
                                                role="meter"
                                                aria-label={`${tribunal.tribunal_name}: ${tribunal.count} processos`}
                                                aria-valuenow={tribunal.count}
                                                aria-valuemin="0"
                                                aria-valuemax={maxTribunalCount}
                                            />
                                        </div>
                                    </li>
                                ))}
                            </ul>
                            <table className="sr-only">
                                <caption>Processos por tribunal</caption>
                                <thead>
                                    <tr><th>Tribunal</th><th>Processos</th></tr>
                                </thead>
                                <tbody>
                                    {stats.tribunals.map((tribunal, idx) => (
                                        <tr key={idx}>
                                            <td>{tribunal.tribunal_name}</td>
                                            <td>{tribunal.count}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </figure>
                    ) : (
                        <p className="text-gray-600 text-sm italic">Nenhum dado disponível</p>
                    )}
                </section>

                {/* Stages Chart — Hierarchical */}
                <section className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-gray-100 dark:border-slate-700 p-6" aria-labelledby="stages-heading">
                    <div className="mb-6">
                        <h2 id="stages-heading" className="text-lg font-bold text-gray-900 dark:text-white">Processos por Estágio</h2>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Classificação hierárquica: estágio / subfase
                        </p>
                    </div>

                    {stagesWithLabels.length > 0 ? (
                        <figure aria-label={`Processos por estágio e fase processual (${stagesWithLabels.length} estágios)`}>
                            <ul className="space-y-5 list-none p-0">
                                {stagesWithLabels.map((stage) => (
                                    <li key={stage.stage}>
                                        {/* Stage bar */}
                                        <div className="flex justify-between items-center text-sm mb-1">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${getStageColorClasses(stage.stage)}`}>
                                                {stage.stage}. {stage.label}
                                            </span>
                                            <span className="font-bold text-gray-800 dark:text-gray-200">
                                                {stage.count.toLocaleString()}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-100 dark:bg-slate-700 rounded-full h-3 overflow-hidden mb-2">
                                            <div
                                                className={`h-3 rounded-full transition-all duration-500 ${getStageProgressBarClasses(stage.stage)}`}
                                                style={{ width: `${(stage.count / maxStageCount) * 100}%` }}
                                                role="meter"
                                                aria-label={`Fase ${stage.label}: ${stage.count} processos`}
                                                aria-valuenow={stage.count}
                                                aria-valuemin="0"
                                                aria-valuemax={maxStageCount}
                                            />
                                        </div>
                                        {/* Substages */}
                                        {stage.substages.length > 0 && (
                                            <ul className="ml-4 space-y-1 list-none p-0">
                                                {stage.substages.map((ss) => (
                                                    <li key={ss.substage || 'null'} className="flex items-center gap-2 text-xs">
                                                        <span className="text-gray-400 font-mono w-6 shrink-0">{ss.substage || '—'}</span>
                                                        <span className="text-gray-600 dark:text-gray-400 flex-1 truncate">{ss.label}</span>
                                                        <span className="font-semibold text-gray-700 dark:text-gray-300 tabular-nums">{ss.count.toLocaleString()}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        )}
                                    </li>
                                ))}
                            </ul>
                            <table className="sr-only">
                                <caption>Processos por estágio e fase processual</caption>
                                <thead>
                                    <tr><th>Estágio</th><th>Processos</th></tr>
                                </thead>
                                <tbody>
                                    {stagesWithLabels.map((stage) => (
                                        <tr key={stage.stage}>
                                            <td>{stage.stage}. {stage.label}</td>
                                            <td>{stage.count}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </figure>
                    ) : (
                        <p className="text-gray-500 dark:text-gray-400 text-sm italic">
                            Nenhum dado hierárquico disponível. Consulte processos primeiro.
                        </p>
                    )}
                </section>
            </div>

            {/* Process Classes Chart - REPLACING the old redundant Nature filter with actual class stats */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <section className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6" aria-labelledby="classes-heading">
                    <div className="flex justify-between items-center mb-6">
                        <h2 id="classes-heading" className="text-lg font-bold text-gray-900">Processos por Classe</h2>
                        <div className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-xs font-bold flex items-center">
                            <Filter className="h-3 w-3 mr-1" />
                            {stats.classes?.length || 0} Classes
                        </div>
                    </div>
                    {stats.classes && stats.classes.length > 0 ? (
                        <figure aria-label={`Processos por classe processual (${stats.classes.length} classes)`}>
                            <div className="max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                                <ul className="space-y-3 list-none p-0">
                                    {stats.classes.map((cls, idx) => (
                                        <li key={idx} className="space-y-1">
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="font-semibold text-gray-700 truncate mr-2" title={cls.class_nature}>
                                                    {cls.class_nature}
                                                </span>
                                                <span className="font-bold text-indigo-600">{cls.count.toLocaleString()}</span>
                                            </div>
                                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                                                <div
                                                    className="bg-indigo-400 h-2 rounded-full transition-all duration-500"
                                                    style={{ width: `${(cls.count / maxClassCount) * 100}%` }}
                                                    role="meter"
                                                    aria-label={`${cls.class_nature}: ${cls.count} processos`}
                                                    aria-valuenow={cls.count}
                                                    aria-valuemin="0"
                                                    aria-valuemax={maxClassCount}
                                                />
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <table className="sr-only">
                                <caption>Processos por classe processual</caption>
                                <thead>
                                    <tr><th>Classe</th><th>Processos</th></tr>
                                </thead>
                                <tbody>
                                    {stats.classes.map((cls, idx) => (
                                        <tr key={idx}>
                                            <td>{cls.class_nature}</td>
                                            <td>{cls.count}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </figure>
                    ) : (
                        <p className="text-gray-600 text-sm italic">Nenhum dado categorizado</p>
                    )}
                </section>

                {/* Timeline Chart */}
                {stats.timeline && stats.timeline.length > 0 && (
                    <section className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6" aria-labelledby="timeline-heading">
                        <h2 id="timeline-heading" className="text-lg font-bold text-gray-900 mb-4">Distribuição Temporal (Últimos 12 meses)</h2>
                        <figure aria-label="Distribuição temporal de processos nos últimos meses">
                            <div className="flex items-end justify-between space-x-2 h-64 px-2">
                                {stats.timeline.map((item, idx) => {
                                    const height = (item.count / maxTimelineCount) * 100;
                                    return (
                                        <div key={idx} className="flex-1 flex flex-col items-center group">
                                            <div className="w-full flex flex-col items-center justify-end h-full pb-2 relative">
                                                <div className="absolute -top-8 bg-indigo-900 text-white text-[10px] py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                                    {item.count} processos
                                                </div>
                                                <div
                                                    className="w-full bg-gradient-to-t from-indigo-500 to-indigo-400 rounded-t-lg hover:from-indigo-600 hover:to-indigo-500 transition-all cursor-pointer"
                                                    style={{ height: `${height || 2}%` }}
                                                    role="meter"
                                                    aria-label={`${item.month}: ${item.count} processos`}
                                                    aria-valuenow={item.count}
                                                    aria-valuemin="0"
                                                    aria-valuemax={maxTimelineCount}
                                                />
                                            </div>
                                            <span className="text-[10px] text-gray-600 font-semibold mt-2 transform -rotate-45 origin-top-left">
                                                {item.month}
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                            <table className="sr-only">
                                <caption>Distribuição temporal de processos</caption>
                                <thead>
                                    <tr><th>Mês</th><th>Processos</th></tr>
                                </thead>
                                <tbody>
                                    {stats.timeline.map((item, idx) => (
                                        <tr key={idx}>
                                            <td>{item.month}</td>
                                            <td>{item.count}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </figure>
                    </section>
                )}
            </div>
```

- [ ] **Step 4: Rodar as duas suítes de novo (vão continuar falhando até as Tasks 5/6 corrigirem os mocks de dados — isso é esperado)**

Run: `cd frontend && npx vitest run src/tests/DashboardA11y.test.jsx src/tests/SemanticHTML.test.jsx`
Expected: ainda FAIL nos testes que dependem de `stats.stages` (o mock desses arquivos ainda usa `phases`); os testes de tribunal e timeline (que não dependem de `stages`) já devem passar.

- [ ] **Step 5: Rodar a suíte completa do frontend para checar regressão nos testes que hoje passam**

Run: `cd frontend && npx vitest run`
Expected: nenhum teste que hoje passa (antes desta task) deve quebrar. Preste atenção especial a qualquer `getByText` singular sobre nome de tribunal/mês/classe que passe a encontrar 2 elementos (visível + tabela `sr-only`) — se isso ocorrer, ajuste o teste para `getAllByText` ou `container.textContent` (nenhum caso conhecido no momento deste plano; ver tabela de diagnóstico).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/Dashboard.jsx
git commit -m "fix: restore chart accessibility (aria-label, role=meter, sr-only tables) in Dashboard"
```

---

## Task 5: Atualizar mocks de `DashboardA11y.test.jsx` para o formato `stages`

**Files:**
- Modify: `frontend/src/tests/DashboardA11y.test.jsx:16-23` (mock de `phaseColors`)
- Modify: `frontend/src/tests/DashboardA11y.test.jsx:34-44` (`mockStatsData`)

- [ ] **Step 1: Ampliar o mock de `phaseColors`**

Old:
```js
// Mock phase color utilities
vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn(() => ({
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-300',
    })),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
}));
```

New:
```js
// Mock phase color utilities
vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn(() => ({
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-300',
    })),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
    getStageColorClasses: vi.fn(() => 'bg-blue-100 text-blue-800'),
    getStageProgressBarClasses: vi.fn(() => 'bg-blue-500'),
}));
```

- [ ] **Step 2: Trocar `phases` por `stages` no mock de dados**

Old:
```js
    const mockStatsData = {
        total_processes: 100,
        total_movements: 500,
        tribunals: [
            { tribunal_name: 'STF', count: 5 },
            { tribunal_name: 'STJ', count: 10 },
            { tribunal_name: 'TJRJ', count: 30 },
        ],
        phases: [
            { phase: '01', class_nature: 'conhecimento', count: 8 },
            { phase: '10', class_nature: 'execucao', count: 12 },
        ],
        timeline: [
            { month: 'Jan', count: 15 },
            { month: 'Feb', count: 20 },
            { month: 'Mar', count: 25 },
        ],
        last_updated: '2026-02-23T10:00:00',
    };
```

New:
```js
    const mockStatsData = {
        total_processes: 100,
        total_movements: 500,
        tribunals: [
            { tribunal_name: 'STF', count: 5 },
            { tribunal_name: 'STJ', count: 10 },
            { tribunal_name: 'TJRJ', count: 30 },
        ],
        stages: [
            { stage: 1, count: 8, substages: [] },
            { stage: 2, count: 12, substages: [] },
        ],
        timeline: [
            { month: 'Jan', count: 15 },
            { month: 'Feb', count: 20 },
            { month: 'Mar', count: 25 },
        ],
        last_updated: '2026-02-23T10:00:00',
    };
```

- [ ] **Step 3: Rodar a suíte**

Run: `cd frontend && npx vitest run src/tests/DashboardA11y.test.jsx`
Expected: PASS — 23/23 testes.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/tests/DashboardA11y.test.jsx
git commit -m "test: align DashboardA11y mocks with hierarchical stages shape"
```

---

## Task 6: Atualizar mocks de `SemanticHTML.test.jsx` para o formato `stages`

**Files:**
- Modify: `frontend/src/tests/SemanticHTML.test.jsx:11-36` (mock de `../services/api`)

- [ ] **Step 1: Trocar `phases` por `stages` no mock**

Old:
```js
vi.mock('../services/api', () => ({
  getStats: vi.fn(() => Promise.resolve({
    total_processes: 100,
    total_movements: 500,
    last_updated: '2026-02-27T10:00:00Z',
    tribunals: [
      { tribunal_name: 'STF', count: 5 },
      { tribunal_name: 'STJ', count: 10 },
    ],
    phases: [
      { phase: 'Fase 1', class_nature: 'Civil', count: 8 },
      { phase: 'Fase 2', class_nature: 'Civil', count: 12 },
    ],
    timeline: [
      { month: 'Jan', count: 15 },
      { month: 'Feb', count: 20 },
    ],
  })),
  bulkSearch: vi.fn(() => Promise.resolve({
    results: [
      { number: '0000001-01.2020.1.01.0000', tribunal_name: 'STF', court_unit: 'Vara 1', phase: 'Fase 1', class_nature: 'Civil' },
      { number: '0000002-01.2020.1.01.0000', tribunal_name: 'STJ', court_unit: 'Vara 2', phase: 'Fase 2', class_nature: 'Civil' },
    ],
    failures: [],
  })),
}));
```

New:
```js
vi.mock('../services/api', () => ({
  getStats: vi.fn(() => Promise.resolve({
    total_processes: 100,
    total_movements: 500,
    last_updated: '2026-02-27T10:00:00Z',
    tribunals: [
      { tribunal_name: 'STF', count: 5 },
      { tribunal_name: 'STJ', count: 10 },
    ],
    stages: [
      { stage: 1, count: 8, substages: [] },
      { stage: 2, count: 12, substages: [] },
    ],
    timeline: [
      { month: 'Jan', count: 15 },
      { month: 'Feb', count: 20 },
    ],
  })),
  bulkSearch: vi.fn(() => Promise.resolve({
    results: [
      { number: '0000001-01.2020.1.01.0000', tribunal_name: 'STF', court_unit: 'Vara 1', phase: 'Fase 1', class_nature: 'Civil' },
      { number: '0000002-01.2020.1.01.0000', tribunal_name: 'STJ', court_unit: 'Vara 2', phase: 'Fase 2', class_nature: 'Civil' },
    ],
    failures: [],
  })),
}));
```

- [ ] **Step 2: Rodar a suíte**

Run: `cd frontend && npx vitest run src/tests/SemanticHTML.test.jsx`
Expected: PASS — todos os testes do arquivo (Dashboard + BulkSearch).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/tests/SemanticHTML.test.jsx
git commit -m "test: align SemanticHTML Dashboard mock with hierarchical stages shape"
```

---

## Task 7: Reescrever `PhaseReference.test.jsx` para o componente hierárquico atual

**Files:**
- Modify: `frontend/src/tests/PhaseReference.test.jsx` (arquivo inteiro)

- [ ] **Step 1: Confirmar que a suíte atual está obsoleta**

Run: `cd frontend && npx vitest run src/tests/PhaseReference.test.jsx`
Expected: FAIL — 25/27 testes, todos por ausência de elementos do componente antigo (fases 01-15, "Legenda de Cores", ícones por tipo) que não existem mais em `PhaseReference.jsx`.

- [ ] **Step 2: Substituir o arquivo inteiro pela suíte alinhada ao componente hierárquico**

New (conteúdo completo de `frontend/src/tests/PhaseReference.test.jsx`):
```jsx
/**
 * Tests for PhaseReference Component
 *
 * PhaseReference.jsx foi reescrito para o modelo hierárquico (Estágio /
 * Subfase / Trânsito em Julgado). Esta suíte testa o componente atual,
 * usando as constantes reais de `constants/phases.js` (sem mock) para
 * que a suíte acompanhe automaticamente futuras mudanças em STAGES/SUBSTAGES.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import PhaseReference from '../components/PhaseReference';
import { STAGES, TRANSIT_OPTIONS, getSubstagesForStage } from '../constants/phases';

describe('PhaseReference Component', () => {
    describe('Header Section', () => {
        it('TC-1: renders main title', () => {
            render(<PhaseReference />);
            expect(screen.getByText('Referência de Classificação Processual')).toBeInTheDocument();
        });

        it('TC-2: displays hierarchical model subtitle', () => {
            render(<PhaseReference />);
            expect(
                screen.getByText('Modelo Hierárquico PGM-Rio — Estágio / Subfase / Trânsito em Julgado')
            ).toBeInTheDocument();
        });

        it('TC-3: shows BookOpen icon', () => {
            const { container } = render(<PhaseReference />);
            const icons = container.querySelectorAll('svg');
            expect(icons.length).toBeGreaterThan(0);
        });

        it('TC-4: header has gradient background', () => {
            const { container } = render(<PhaseReference />);
            const header = container.querySelector('.bg-gradient-to-r.from-indigo-600.to-violet-600');
            expect(header).toBeInTheDocument();
        });
    });

    describe('Info Box Section', () => {
        it('TC-5: displays info box title', () => {
            render(<PhaseReference />);
            expect(screen.getByText('Sobre o Sistema de Classificação')).toBeInTheDocument();
        });

        it('TC-6: shows CNJ resolutions info', () => {
            render(<PhaseReference />);
            expect(screen.getByText(/Resoluções 46\/2007 e 326\/2020/)).toBeInTheDocument();
            expect(screen.getByText(/Resolução CNJ 455\/2022/)).toBeInTheDocument();
        });

        it('TC-7: info box has blue styling', () => {
            const { container } = render(<PhaseReference />);
            const infoBox = container.querySelector('.bg-blue-50.border-l-4.border-blue-500');
            expect(infoBox).toBeInTheDocument();
        });
    });

    describe('Hierarchical Classification Section', () => {
        it('TC-8: renders section title', () => {
            render(<PhaseReference />);
            expect(screen.getByText('Classificação Hierárquica (3 Campos)')).toBeInTheDocument();
        });

        it('TC-9: renders all 5 stage labels', () => {
            render(<PhaseReference />);
            Object.values(STAGES).forEach((stage) => {
                expect(screen.getByText(`${stage.value}. ${stage.label}`)).toBeInTheDocument();
            });
        });

        it('TC-10: renders substages nested under stage 1', () => {
            render(<PhaseReference />);
            const stage1Substages = getSubstagesForStage(1);
            expect(stage1Substages.length).toBeGreaterThan(0);
            stage1Substages.forEach((ss) => {
                expect(screen.getByText(ss.label)).toBeInTheDocument();
            });
        });

        it('TC-11: renders substages nested under stage 2', () => {
            render(<PhaseReference />);
            const stage2Substages = getSubstagesForStage(2);
            expect(stage2Substages.length).toBeGreaterThan(0);
            stage2Substages.forEach((ss) => {
                expect(screen.getByText(ss.label)).toBeInTheDocument();
            });
        });

        it('TC-12: stages 3, 4 and 5 have no substages', () => {
            [3, 4, 5].forEach((stageValue) => {
                expect(getSubstagesForStage(stageValue)).toHaveLength(0);
            });
        });

        it('TC-13: renders stage badge with getStageColorClasses styling', () => {
            render(<PhaseReference />);
            // STAGES[1].color === 'blue' -> getStageColorClasses(1) inclui 'bg-blue-100 text-blue-800'
            const stage1Badge = screen.getByText('1. Conhecimento');
            expect(stage1Badge.className).toContain('bg-blue-100');
            expect(stage1Badge.className).toContain('text-blue-800');
        });
    });

    describe('Trânsito em Julgado Section', () => {
        it('TC-14: renders section title', () => {
            render(<PhaseReference />);
            expect(screen.getByText('Trânsito em Julgado (campo independente)')).toBeInTheDocument();
        });

        it('TC-15: renders all transit options', () => {
            render(<PhaseReference />);
            Object.values(TRANSIT_OPTIONS).forEach((t) => {
                expect(screen.getByText(`${t.value} = ${t.label}`)).toBeInTheDocument();
            });
        });
    });

    describe('Documentation Link', () => {
        it('TC-16: displays documentation reference', () => {
            render(<PhaseReference />);
            expect(screen.getByText(/Para mais informações/)).toBeInTheDocument();
        });

        it('TC-17: shows correct documentation path', () => {
            render(<PhaseReference />);
            expect(screen.getByText('frontend/src/constants/README-FASES.md')).toBeInTheDocument();
        });

        it('TC-18: documentation path is in code tag', () => {
            const { container } = render(<PhaseReference />);
            const codeTag = Array.from(container.querySelectorAll('code')).find((el) =>
                el.textContent.includes('README-FASES.md')
            );
            expect(codeTag).toBeInTheDocument();
            expect(codeTag).toHaveClass('font-mono');
        });
    });

    describe('Layout and Structure', () => {
        it('TC-19: uses correct container max-width', () => {
            const { container } = render(<PhaseReference />);
            const mainContainer = container.querySelector('.max-w-6xl.mx-auto');
            expect(mainContainer).toBeInTheDocument();
        });

        it('TC-20: renders rounded cards for sections', () => {
            const { container } = render(<PhaseReference />);
            const roundedCards = container.querySelectorAll('.rounded-2xl');
            expect(roundedCards.length).toBeGreaterThan(2);
        });
    });
});
```

- [ ] **Step 3: Rodar a suíte**

Run: `cd frontend && npx vitest run src/tests/PhaseReference.test.jsx`
Expected: PASS — 20/20 testes.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/tests/PhaseReference.test.jsx
git commit -m "test: rewrite PhaseReference suite for the hierarchical component"
```

---

## Task 8: Corrigir expectativa obsoleta sobre a aba "Configurações" em `App.nav.test.jsx`

**Files:**
- Modify: `frontend/src/__tests__/App.nav.test.jsx:23-26`

- [ ] **Step 1: Rodar a suíte para confirmar a falha atual**

Run: `cd frontend && npx vitest run src/__tests__/App.nav.test.jsx`
Expected: FAIL em `App — navegação > não exibe aba Configurações` — o botão com `role="tab"` e nome "Configurações" existe (`App.jsx:94`, `SettingsComponent` lazy-loaded e com painel funcional), então `queryByRole` não retorna `null`.

- [ ] **Step 2: Atualizar o teste para refletir a feature intencional**

Old:
```js
  it('não exibe aba Configurações', () => {
    render(<App />);
    expect(screen.queryByRole('tab', { name: /configurações/i })).toBeNull();
  });
```

New:
```js
  it('exibe aba Configurações', () => {
    render(<App />);
    expect(screen.getByRole('tab', { name: /configurações/i })).toBeInTheDocument();
  });
```

- [ ] **Step 3: Rodar a suíte novamente**

Run: `cd frontend && npx vitest run src/__tests__/App.nav.test.jsx`
Expected: PASS — 4/4 testes.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/__tests__/App.nav.test.jsx
git commit -m "test: update App nav test — Configurações tab is an intentional, shipped feature"
```

---

## Task 9: Regressão final (backend + frontend)

**Files:** nenhum (apenas verificação).

- [ ] **Step 1: Rodar a suíte completa do backend**

Run: `cd backend && python -m pytest -q`
Expected: PASS — mesma contagem da baseline original (633 passed, 17 skipped) ou mais (sem diminuir).

- [ ] **Step 2: Rodar a suíte completa do frontend**

Run: `cd frontend && npx vitest run`
Expected: PASS — 482/482 testes (0 falhas). Caso sobre alguma falha nova não coberta por este plano, pare e trate como um achado novo antes de prosseguir para o plano de adaptação doctree.

- [ ] **Step 3: Confirmar que nenhum arquivo fora do escopo deste plano foi alterado**

Run: `git status`
Expected: working tree limpo (todas as mudanças já commitadas task a task); `git log --oneline -9` mostra os 8 commits deste plano em sequência.

---

## Observação sobre o plano seguinte

Este plano é **pré-requisito de baseline**, não parte do plano `2026-07-04-fase-processual-doctree-adaptation.md`. Ele não toca nenhum arquivo listado na tabela "Estrutura de arquivos" daquele plano (`backend/services/document_phase_classifier.py`, `hierarchical_classification.py`, `process_service.py`, `reclassify_hierarchical.py`, `frontend/src/constants/phases.js`, `frontend/src/utils/phaseColors.js`) — portanto pode ser executado em qualquer ordem em relação a ele, mas **deve ser concluído primeiro** para que a Task 9 acima sirva de baseline limpa (0 falhas) antes de iniciar as tasks do plano doctree.
