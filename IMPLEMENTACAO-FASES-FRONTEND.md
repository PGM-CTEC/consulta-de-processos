# Implementação das 15 Fases Processuais no Frontend

## 📋 Resumo

Sistema de classificação de fases processuais implementado no frontend para garantir que apenas as **15 fases oficiais** definidas no modelo da PGM-Rio sejam exibidas aos usuários.

## 🎯 Problema Resolvido

**Antes**: O frontend exibia fases variáveis vindas do backend sem validação, resultando em inconsistências como:
- "Execução"
- "Fase Executiva"
- "Trânsito em Julgado"
- "Conhecimento"
- Outras variações

**Depois**: Todas as fases são normalizadas para uma das 15 fases oficiais do modelo PGM-Rio.

## 📁 Arquivos Criados/Modificados

### ✨ Novos Arquivos

1. **`frontend/src/constants/phases.js`** (286 linhas)
   - Definições das 15 fases processuais
   - Funções de normalização e validação
   - Mapeamentos por código e nome

2. **`frontend/src/constants/README-FASES.md`** (268 linhas)
   - Documentação completa do sistema
   - Guias de uso e exemplos
   - Referências técnicas

3. **`frontend/src/components/PhaseReference.jsx`** (159 linhas)
   - Componente visual de referência
   - Exibe todas as 15 fases com cores
   - Útil para documentação e treinamento

4. **`frontend/src/constants/phases.test.js`** (123 linhas)
   - Testes unitários da normalização
   - Casos de teste para validação
   - Executável no navegador ou Node.js

5. **`frontend/CHANGELOG-FASES.md`** (242 linhas)
   - Histórico de mudanças
   - Exemplos de uso
   - Referências e créditos

### 🔧 Arquivos Modificados

1. **`frontend/src/utils/phaseColors.js`**
   - Refatorado para usar `getPhaseInfo()`
   - Garantia de fases válidas
   - Mapeamento de cores consistente

2. **`frontend/src/utils/exportHelpers.js`**
   - Adiciona normalização de fase
   - Garante relatórios com nomes oficiais

## 🔄 Arquitetura da Solução

```
┌──────────────────────────────────────────────────────────────┐
│                    BACKEND (API)                             │
│  classification_rules.py → FaseProcessual.descricao          │
│  "Conhecimento - Sentença sem Trânsito em Julgado"          │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│               FRONTEND - CAMADA DE CONSTANTES                │
│  frontend/src/constants/phases.js                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  VALID_PHASES (15 fases oficiais)                    │   │
│  │  • Código (01-15)                                     │   │
│  │  • Nome oficial (com travessão —)                     │   │
│  │  • Tipo (Conhecimento, Execução, etc.)               │   │
│  │  • Cor (blue, green, orange, etc.)                   │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  normalizePhase(input)                               │   │
│  │  • Aceita códigos (01-15)                            │   │
│  │  • Aceita nomes com traço ou travessão               │   │
│  │  • Faz match por palavras-chave                      │   │
│  │  • Fallback: "Conhecimento — Antes da Sentença"      │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│               FRONTEND - CAMADA DE UTILS                     │
│  frontend/src/utils/phaseColors.js                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  getPhaseDisplayName(phase)                          │   │
│  │  → normalizePhase(phase)                             │   │
│  │  → "Conhecimento — Sentença sem Trânsito em Julgado" │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  getPhaseColorClasses(phase)                         │   │
│  │  → getPhaseInfo(phase)                               │   │
│  │  → "bg-blue-100 text-blue-800"                       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│               FRONTEND - COMPONENTES REACT                   │
│  • ProcessDetails.jsx                                        │
│  • BulkSearch.jsx                                            │
│  • Dashboard.jsx                                             │
│  • exportHelpers.js                                          │
│                                                              │
│  <span className={getPhaseColorClasses(data.phase)}>        │
│    {getPhaseDisplayName(data.phase)}                         │
│  </span>                                                     │
└──────────────────────────────────────────────────────────────┘
```

## 🎨 Mapeamento de Cores

| Fase | Código | Cor | Classes Tailwind |
|------|--------|-----|------------------|
| Conhecimento (em andamento) | 01, 02, 04, 05, 07, 08 | 🔵 Azul | `bg-blue-100 text-blue-800` |
| Conhecimento (transitado) | 03, 06, 09 | 🟢 Verde | `bg-green-100 text-green-800` |
| Execução | 10, 11, 12 | 🟠 Laranja | `bg-orange-100 text-orange-800` |
| Suspenso/Sobrestado | 13 | 🟡 Amarelo | `bg-yellow-100 text-yellow-800` |
| Conversão em Renda | 14 | 🟣 Roxo | `bg-purple-100 text-purple-800` |
| Arquivado | 15 | ⚫ Cinza | `bg-gray-100 text-gray-800` |

## ✅ Testes e Validação

### Executar Testes Unitários

```javascript
// No console do navegador
import { runTests } from './src/constants/phases.test.js';
runTests();
```

### Visualizar Referência de Fases

Adicione temporariamente ao `App.jsx`:

```javascript
import PhaseReference from './components/PhaseReference';

function App() {
  return (
    <div>
      <PhaseReference />
      {/* resto da aplicação */}
    </div>
  );
}
```

### Casos de Teste Cobertos

- ✅ Códigos numéricos (01-15, 1-15)
- ✅ Nomes completos com travessão (—)
- ✅ Nomes com traço (-) vindos do backend
- ✅ Variações e palavras-chave
- ✅ Entradas nulas ou vazias
- ✅ Fases inválidas (fallback)

## 📊 Impacto nos Componentes

### ProcessDetails.jsx
- Exibe fase normalizada do processo
- Badge com cor consistente

### BulkSearch.jsx
- Tabela com fases normalizadas
- Filtros e ordenação por fase

### Dashboard.jsx
- Gráficos com fases agrupadas corretamente
- Estatísticas por fase oficial

### exportHelpers.js
- CSV/XLSX/TXT/MD com nomes oficiais
- Dados exportados padronizados

## 🔒 Garantias de Qualidade

1. **Validação Automática**: Toda fase exibida é uma das 15 oficiais
2. **Consistência Visual**: Cores uniformes em todo o sistema
3. **Compatibilidade**: Aceita variações do backend
4. **Fallback Seguro**: Fase padrão em caso de erro
5. **Testabilidade**: Suite de testes incluída

## 📚 Documentação Adicional

- **Modelo de Classificação**: `/modelo_classificacao_fases_processuais_pgm_rio-08.02.2026.md`
- **Backend Implementation**: `/backend/services/classification_rules.py`
- **Frontend Guide**: `/frontend/src/constants/README-FASES.md`
- **Changelog**: `/frontend/CHANGELOG-FASES.md`

## 🚀 Próximos Passos

### Sugestões de Melhorias

1. **Dashboard Avançado**
   - Gráfico de pizza por fase
   - Timeline de mudanças de fase
   - Filtros por fase

2. **Busca e Filtros**
   - Buscar processos por fase
   - Filtrar histórico por fase
   - Ordenar por fase

3. **Relatórios**
   - Relatório de processos por fase
   - Análise de tempo médio em cada fase
   - Alertas de fases críticas

4. **UX/UI**
   - Tooltips explicativos nas fases
   - Ícones customizados por fase
   - Animações de transição de fase

5. **Validação**
   - Integração com LLM para validação
   - Auditoria de classificações
   - Logs de mudanças de fase

## 🧑‍💻 Como Usar

### Para Desenvolvedores

```javascript
// 1. Importar funções
import { normalizePhase, getPhaseInfo } from '../constants/phases';
import { getPhaseColorClasses, getPhaseDisplayName } from '../utils/phaseColors';

// 2. Normalizar fase
const phase = normalizePhase(data.phase);
// "Conhecimento — Sentença sem Trânsito em Julgado"

// 3. Obter informações
const info = getPhaseInfo(data.phase);
// { code: "02", name: "...", type: "Conhecimento", color: "blue" }

// 4. Estilizar no JSX
<span className={`px-3 py-1 rounded-full ${getPhaseColorClasses(data.phase)}`}>
  {getPhaseDisplayName(data.phase)}
</span>
```

### Para Testes

```bash
# Executar testes
cd frontend
npm test phases.test.js

# Ou no console do navegador
window.runPhaseTests()
```

## 🐛 Troubleshooting

### Problema: Fase não normaliza corretamente
**Solução**: Verifique se o backend está retornando um dos nomes esperados. Use `console.log(normalizePhase(data.phase))` para debug.

### Problema: Cores não aparecem
**Solução**: Certifique-se de que as classes Tailwind estão sendo incluídas no bundle. Verifique `tailwind.config.js`.

### Problema: Testes falhando
**Solução**: Execute `npm install` para garantir que todas as dependências estão instaladas.

## 📞 Suporte

Para dúvidas sobre o sistema de fases:
- Consulte `/frontend/src/constants/README-FASES.md`
- Verifique o modelo oficial: `/modelo_classificacao_fases_processuais_pgm_rio-08.02.2026.md`
- Contate a Coordenação de Tecnologia - PGM-Rio

---

**Implementado em**: 08 de Fevereiro de 2026
**Versão**: 2.0.0
**Status**: ✅ Concluído
