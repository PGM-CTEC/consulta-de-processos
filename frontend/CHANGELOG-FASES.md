# Changelog - Sistema de Fases Processuais

## [2.0.0] - 2026-02-08

### 🎯 Objetivo
Corrigir o frontend para exibir exclusivamente as **15 fases processuais oficiais** definidas no modelo de classificação da PGM-Rio (Versão 2.0 - Fevereiro 2026).

### ✨ Adicionado

#### Novo Módulo de Constantes
- **`frontend/src/constants/phases.js`**
  - Definição completa das 15 fases processuais com código, nome, tipo e cor
  - Função `normalizePhase()`: converte variações de entrada em nomes oficiais
  - Função `getPhaseInfo()`: retorna informações completas de uma fase
  - Função `isValidPhase()`: valida se uma fase é oficial
  - Suporte para códigos (01-15) e nomes completos
  - Compatibilidade com traços (`-`) e travessões (`—`)

#### Documentação
- **`frontend/src/constants/README-FASES.md`**
  - Documentação completa do sistema de fases
  - Guia de uso para desenvolvedores
  - Exemplos de código
  - Referências aos modelos CNJ

#### Componente de Referência
- **`frontend/src/components/PhaseReference.jsx`**
  - Visualização interativa das 15 fases
  - Agrupamento por tipo (Conhecimento, Execução, Transversal, Final)
  - Legenda de cores
  - Útil para treinamento e validação

### 🔄 Modificado

#### Utilitários de Fase (`frontend/src/utils/phaseColors.js`)
- **Antes**: Lógica baseada em palavras-chave (heurística)
- **Depois**: Usa `getPhaseInfo()` para determinar cores de forma consistente
- Garantia de que todas as fases exibidas são uma das 15 oficiais
- Fallback robusto para "Conhecimento — Antes da Sentença"

#### Exportação de Dados (`frontend/src/utils/exportHelpers.js`)
- **Antes**: Exportava fase como recebida do backend (pode ser variável)
- **Depois**: Normaliza fase usando `normalizePhase()` antes de exportar
- Garante que todos os relatórios (CSV, XLSX, TXT, MD) contenham nomes oficiais

### 📋 As 15 Fases Processuais

| Código | Nome da Fase | Tipo | Cor |
|--------|-------------|------|-----|
| **01** | Conhecimento — Antes da Sentença | Conhecimento | 🔵 Azul |
| **02** | Conhecimento — Sentença sem Trânsito em Julgado | Conhecimento | 🔵 Azul |
| **03** | Conhecimento — Sentença com Trânsito em Julgado | Conhecimento | 🟢 Verde |
| **04** | Conhecimento — Recurso 2ª Instância — Pendente Julgamento | Conhecimento | 🔵 Azul |
| **05** | Conhecimento — Recurso 2ª Instância — Julgado sem Trânsito | Conhecimento | 🔵 Azul |
| **06** | Conhecimento — Recurso 2ª Instância — Transitado em Julgado | Conhecimento | 🟢 Verde |
| **07** | Conhecimento — Recurso Tribunais Superiores — Pendente Julgamento | Conhecimento | 🔵 Azul |
| **08** | Conhecimento — Recurso Tribunais Superiores — Julgado sem Trânsito | Conhecimento | 🔵 Azul |
| **09** | Conhecimento — Recurso Tribunais Superiores — Transitado em Julgado | Conhecimento | 🟢 Verde |
| **10** | Execução | Execução | 🟠 Laranja |
| **11** | Execução Suspensa | Execução | 🟠 Laranja |
| **12** | Execução Suspensa Parcialmente (Impugnação Parcial) | Execução | 🟠 Laranja |
| **13** | Suspenso / Sobrestado | Transversal | 🟡 Amarelo |
| **14** | Conversão em Renda | Execução | 🟣 Roxo |
| **15** | Arquivado Definitivamente | Final | ⚫ Cinza |

### 🔧 Fluxo de Normalização

```
Backend API
  ↓ fase: "Conhecimento - Sentença sem Trânsito em Julgado"
  ↓ (variável, pode ter traço ou travessão)
  ↓
normalizePhase()
  ↓ Normaliza traços/travessões
  ↓ Valida contra lista de fases oficiais
  ↓
  "Conhecimento — Sentença sem Trânsito em Julgado"
  ↓ (uma das 15 fases oficiais)
  ↓
getPhaseInfo()
  ↓ {code: "02", name: "...", type: "Conhecimento", color: "blue"}
  ↓
getPhaseColorClasses()
  ↓ "bg-blue-100 text-blue-800"
  ↓
Componentes React
  ↓ Exibição consistente em todo o frontend
```

### 🎨 Código de Cores

| Cor | Classes Tailwind | Aplicação |
|-----|------------------|-----------|
| 🔵 Azul | `bg-blue-100 text-blue-800` | Conhecimento em andamento (01, 02, 04, 05, 07, 08) |
| 🟢 Verde | `bg-green-100 text-green-800` | Conhecimento com trânsito (03, 06, 09) |
| 🟠 Laranja | `bg-orange-100 text-orange-800` | Execução (10, 11, 12) |
| 🟡 Amarelo | `bg-yellow-100 text-yellow-800` | Suspenso/Sobrestado (13) |
| 🟣 Roxo | `bg-purple-100 text-purple-800` | Conversão em Renda (14) |
| ⚫ Cinza | `bg-gray-100 text-gray-800` | Arquivado (15) |

### ✅ Garantias de Qualidade

1. **Validação Automática**: Toda fase exibida é garantidamente uma das 15 oficiais
2. **Consistência Visual**: Mesmas cores em todos os componentes
3. **Exportação Padronizada**: Relatórios sempre com nomes oficiais
4. **Fallback Robusto**: Em caso de fase desconhecida, usa "Conhecimento — Antes da Sentença"
5. **Compatibilidade**: Aceita variações do backend (traços, travessões, códigos)

### 🧪 Componentes Afetados

- ✅ `ProcessDetails.jsx` - Exibe fase do processo individual
- ✅ `BulkSearch.jsx` - Exibe fases na tabela de busca em lote
- ✅ `Dashboard.jsx` - Exibe estatísticas de fases
- ✅ `exportHelpers.js` - Normaliza fases antes de exportar

### 📚 Referências

- **Modelo de Classificação**: `modelo_classificacao_fases_processuais_pgm_rio-08.02.2026.md`
- **Backend**: `backend/services/classification_rules.py`
- **Documentação Frontend**: `frontend/src/constants/README-FASES.md`
- **Resoluções CNJ**: 46/2007, 326/2020, 455/2022

### 🚀 Como Usar

#### Para Desenvolvedores

```javascript
import { normalizePhase, getPhaseInfo } from '../constants/phases';
import { getPhaseColorClasses, getPhaseDisplayName } from '../utils/phaseColors';

// Normalizar fase vinda do backend
const normalizedPhase = normalizePhase(data.phase);

// Obter informações completas
const phaseInfo = getPhaseInfo(data.phase);
console.log(phaseInfo);
// { code: "10", name: "Execução", type: "Execução", color: "orange" }

// Obter classes CSS
const colorClasses = getPhaseColorClasses(data.phase);
// "bg-orange-100 text-orange-800"

// Uso no JSX
<span className={`... ${getPhaseColorClasses(data.phase)}`}>
  {getPhaseDisplayName(data.phase)}
</span>
```

#### Visualizar Referência de Fases

```javascript
// Adicionar rota temporária para visualizar as fases
import PhaseReference from './components/PhaseReference';

// No roteador ou componente principal
<PhaseReference />
```

### 🐛 Correções

- ❌ **Antes**: Fases variáveis como "Execução", "Fase Executiva", "Trânsito em Julgado"
- ✅ **Depois**: Apenas uma das 15 fases oficiais: "Execução", "Conhecimento — Sentença com Trânsito em Julgado", etc.

### 🔮 Próximos Passos (Sugestões)

1. Adicionar filtro por fase no Dashboard
2. Implementar gráficos de distribuição por fase
3. Criar relatório de processos por fase
4. Adicionar tooltips explicativos nas fases
5. Implementar busca/filtro por fase no histórico

### 👥 Créditos

- **Modelo de Classificação**: Coordenação de Tecnologia - PGM-Rio
- **Implementação Frontend**: Sistema de Consulta Processual v2.0
- **Data**: 08 de Fevereiro de 2026
