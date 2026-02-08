# Sistema de Fases Processuais - Frontend

## Visão Geral

Este sistema implementa as **15 fases processuais oficiais** definidas no modelo de classificação da Procuradoria-Geral do Município do Rio de Janeiro (PGM-Rio), versão 2.0, de fevereiro de 2026.

## As 15 Fases Processuais

### Fases de Conhecimento (01-09)

#### 1ª Instância
- **01** - Conhecimento — Antes da Sentença
- **02** - Conhecimento — Sentença sem Trânsito em Julgado
- **03** - Conhecimento — Sentença com Trânsito em Julgado

#### 2ª Instância (Tribunais de Justiça)
- **04** - Conhecimento — Recurso 2ª Instância — Pendente Julgamento
- **05** - Conhecimento — Recurso 2ª Instância — Julgado sem Trânsito
- **06** - Conhecimento — Recurso 2ª Instância — Transitado em Julgado

#### Tribunais Superiores (STJ, STF)
- **07** - Conhecimento — Recurso Tribunais Superiores — Pendente Julgamento
- **08** - Conhecimento — Recurso Tribunais Superiores — Julgado sem Trânsito
- **09** - Conhecimento — Recurso Tribunais Superiores — Transitado em Julgado

### Fases de Execução (10-12, 14)

- **10** - Execução
- **11** - Execução Suspensa
- **12** - Execução Suspensa Parcialmente (Impugnação Parcial)
- **14** - Conversão em Renda

### Fases Transversais e Finais (13, 15)

- **13** - Suspenso / Sobrestado
- **15** - Arquivado Definitivamente

## Arquitetura do Sistema

### Arquivos Principais

```
frontend/src/
├── constants/
│   ├── phases.js              # Definições e lógica de normalização
│   └── README-FASES.md        # Esta documentação
└── utils/
    ├── phaseColors.js         # Estilização e exibição
    └── exportHelpers.js       # Exportação de dados
```

### Fluxo de Dados

```
Backend (API)
    ↓
  phase: "execução" (pode ser variável)
    ↓
normalizePhase(phase)
    ↓
  "Execução" (uma das 15 fases oficiais)
    ↓
getPhaseInfo(phase)
    ↓
  {code: "10", name: "Execução", type: "Execução", color: "orange"}
    ↓
getPhaseColorClasses(phase)
    ↓
  "bg-orange-100 text-orange-800" (classes Tailwind)
```

## Funções Principais

### `normalizePhase(phaseInput)`

Converte qualquer entrada de fase (código, nome parcial, variações) em um dos 15 nomes oficiais.

**Exemplos:**
```javascript
normalizePhase("execução")           // "Execução"
normalizePhase("10")                 // "Execução"
normalizePhase("exec suspensa")      // "Execução Suspensa"
normalizePhase("arquivado")          // "Arquivado Definitivamente"
normalizePhase("conhecimento")       // "Conhecimento — Antes da Sentença"
normalizePhase(null)                 // "Conhecimento — Antes da Sentença"
```

### `getPhaseInfo(phaseInput)`

Retorna objeto completo com informações da fase.

**Exemplo:**
```javascript
getPhaseInfo("10")
// {
//   code: "10",
//   name: "Execução",
//   type: "Execução",
//   color: "orange"
// }
```

### `getPhaseColorClasses(phase)`

Retorna classes Tailwind CSS para estilização do badge de fase.

**Exemplo:**
```javascript
getPhaseColorClasses("Execução")
// "bg-orange-100 text-orange-800"
```

### `isValidPhase(phase)`

Verifica se uma string corresponde a um nome oficial de fase.

**Exemplo:**
```javascript
isValidPhase("Execução")                               // true
isValidPhase("Conhecimento — Antes da Sentença")       // true
isValidPhase("Fase Inválida")                          // false
```

## Código de Cores

| Cor    | Fases                                      | Classes Tailwind             |
|--------|--------------------------------------------|------------------------------|
| 🔵 Azul   | Conhecimento (01, 02, 04, 05, 07, 08)    | `bg-blue-100 text-blue-800`  |
| 🟢 Verde  | Trânsito em Julgado (03, 06, 09)         | `bg-green-100 text-green-800`|
| 🟠 Laranja| Execução (10, 11, 12)                     | `bg-orange-100 text-orange-800`|
| 🟡 Amarelo| Suspenso/Sobrestado (13)                  | `bg-yellow-100 text-yellow-800`|
| 🟣 Roxo   | Conversão em Renda (14)                   | `bg-purple-100 text-purple-800`|
| ⚫ Cinza  | Arquivado (15)                            | `bg-gray-100 text-gray-800`  |

## Uso nos Componentes

### ProcessDetails.jsx

```jsx
import { getPhaseColorClasses, getPhaseDisplayName } from '../utils/phaseColors';

// No render
<span className={`... ${getPhaseColorClasses(data.phase)}`}>
  {getPhaseDisplayName(data.phase)}
</span>
```

### BulkSearch.jsx

```jsx
import { getPhaseColorClasses, getPhaseDisplayName } from '../utils/phaseColors';

// Na tabela
<span className={`... ${getPhaseColorClasses(p.phase)}`}>
  {getPhaseDisplayName(p.phase)}
</span>
```

### Dashboard.jsx

```jsx
import { getPhaseColorClasses, getPhaseDisplayName } from '../utils/phaseColors';

// No gráfico de fases
<span className={`... ${getPhaseColorClasses(phase.phase)}`}>
  {getPhaseDisplayName(phase.phase)}
</span>
```

### exportHelpers.js

```javascript
import { normalizePhase } from '../constants/phases';

// Ao preparar dados para exportação
export function prepareExportData(results) {
  return results.map(p => ({
    'Fase Atual': normalizePhase(p.phase)  // Sempre exporta nome oficial
  }));
}
```

## Validação e Qualidade de Dados

O sistema garante que:

1. **Todas as fases exibidas são válidas**: Usa `normalizePhase()` para converter variações em nomes oficiais
2. **Consistência visual**: Mesmas cores em todo o sistema via `getPhaseColorClasses()`
3. **Exportação padronizada**: Relatórios sempre contêm nomes oficiais das fases
4. **Fallback robusto**: Se a fase não for reconhecida, usa "Conhecimento — Antes da Sentença"

## Manutenção

### Adicionar Nova Fase

1. Adicione a definição em `constants/phases.js`:
```javascript
export const VALID_PHASES = {
  // ...
  NOVA_FASE: {
    code: '16',
    name: 'Nome da Nova Fase',
    type: 'Tipo',
    color: 'blue'
  }
};
```

2. Atualize a lógica de normalização se necessário:
```javascript
export function normalizePhase(phaseInput) {
  // Adicione regras de detecção se necessário
  if (inputLower.includes('palavra-chave')) {
    return VALID_PHASES.NOVA_FASE.name;
  }
  // ...
}
```

### Alterar Cores

Modifique o mapeamento em `utils/phaseColors.js`:
```javascript
const colorMap = {
  'blue': 'bg-blue-100 text-blue-800',
  'green': 'bg-green-500 text-white',  // Exemplo: cor mais forte
  // ...
};
```

## Referências

- **Modelo de Classificação**: `modelo_classificacao_fases_processuais_pgm_rio-08.02.2026.md`
- **Backend Classification**: `backend/services/classification_rules.py`
- **Tabelas CNJ**: Resoluções CNJ 46/2007 e 326/2020

## Histórico

| Versão | Data       | Alterações                                        |
|--------|------------|---------------------------------------------------|
| 1.0    | 08/02/2026 | Sistema de 15 fases implementado no frontend     |
