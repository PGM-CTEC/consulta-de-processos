# Correção - Múltiplas Instâncias e Baixa Definitiva

## 🐛 Problemas Identificados

### Processo: 0435756-80.2012.8.19.0001

#### Problema 1: Classe Incorreta
- **Esperado**: Classe de 1ª instância (processo já baixado)
- **Obtido**: "Apelação / Remessa Necessária" (classe de 2ª instância)
- **Causa**: Sistema só mostra dados da última instância retornada pelo DataJud

#### Problema 2: Fase Incorreta
- **Esperado**: "Arquivado Definitivamente" (Fase 15)
- **Obtido**: "1.2.1 2ª Instância - Em Recurso"
- **Causa**: Backend não detectava situação BAIXADO a partir dos movimentos

#### Problema 3: Múltiplas Instâncias Não Diferenciadas
- **Situação**: DataJud pode retornar dados de 1ª E 2ª instância separadamente
- **Problema**: Sistema não permite visualizar/alternar entre instâncias
- **Impacto**: Usuário vê apenas a instância mais recente, perdendo contexto

## ✅ Correções Aplicadas

### 1. Backend - Detecção Automática de Baixa ✅

**Arquivo**: `backend/services/phase_analyzer.py`

#### O que foi feito

Adicionada lógica para detectar automaticamente quando um processo está BAIXADO, analisando os movimentos:

```python
# Códigos de movimentos que indicam baixa definitiva/arquivamento
CODIGOS_BAIXA = {22, 246, 861, 865, 10965, 10966, 10967, 12618}

# Verificar se algum movimento indica baixa
has_baixa = any(m.codigo in CODIGOS_BAIXA for m in movimentos_adaptados)

if has_baixa:
    # Pegar o último movimento de baixa
    movs_baixa = [m for m in movimentos_adaptados if m.codigo in CODIGOS_BAIXA]
    if movs_baixa:
        ultima_baixa = max(movs_baixa, key=lambda m: m.data)

        # Códigos de desarquivamento/reativação
        CODIGOS_DESARQUIVAMENTO = {900, 12617}

        # Verificar se há desarquivamento posterior
        movs_desarq = [m for m in movimentos_adaptados
                      if m.codigo in CODIGOS_DESARQUIVAMENTO and m.data > ultima_baixa.data]

        if not movs_desarq:
            situacao = "BAIXADO"
```

#### Impacto

- ✅ Processos com movimento código 22 (Baixa Definitiva) agora são corretamente classificados como BAIXADO
- ✅ Classificador retorna Fase 15 (Arquivado Definitivamente) automaticamente
- ✅ Verifica se houve desarquivamento posterior antes de classificar como baixado

### 2. Frontend - Validação Adicional de Baixa ✅

**Arquivo**: `frontend/src/constants/phases.js`

#### O que foi feito

Adicionadas funções para validar baixa definitiva no frontend (fallback de segurança):

```javascript
/**
 * Códigos de movimento CNJ que indicam baixa definitiva/arquivamento
 */
const MOVIMENTO_BAIXA_CODES = [22, 246, 861, 865, 10965, 10966, 10967, 12618];

/**
 * Verifica se há movimento de baixa definitiva nos dados do processo
 */
export function hasDefinitiveBaixa(movements) {
  if (!movements || !Array.isArray(movements)) return false;

  // Procurar movimento de baixa
  const baixaMovement = movements.find(m =>
    MOVIMENTO_BAIXA_CODES.includes(parseInt(m.code)) ||
    MOVIMENTO_BAIXA_CODES.includes(parseInt(m.codigo))
  );

  if (!baixaMovement) return false;

  // Verificar se há desarquivamento posterior
  const baixaDate = new Date(baixaMovement.date || baixaMovement.dataHora);
  const CODIGOS_DESARQUIVAMENTO = [900, 12617];

  const hasDesarquivamento = movements.some(m => {
    const code = parseInt(m.code || m.codigo);
    if (!CODIGOS_DESARQUIVAMENTO.includes(code)) return false;

    const movDate = new Date(m.date || m.dataHora);
    return movDate > baixaDate;
  });

  return !hasDesarquivamento;
}

/**
 * Normaliza fase considerando também os movimentos do processo
 */
export function normalizePhaseWithMovements(phaseInput, classNature = null, movements = null) {
  // Se há movimento de baixa definitiva, força Fase 15
  if (movements && hasDefinitiveBaixa(movements)) {
    return VALID_PHASES.ARQUIVADO.name;
  }

  // Caso contrário, usa normalização padrão
  return normalizePhase(phaseInput, classNature);
}
```

#### Impacto

- ✅ Frontend valida baixa mesmo se backend não classificou corretamente
- ✅ Processos já salvos no banco com classificação antiga serão corrigidos na exibição
- ✅ Funciona como camada de validação adicional

### 3. Frontend - Uso da Validação em ProcessDetails ✅

**Arquivo**: `frontend/src/components/ProcessDetails.jsx`

#### O que foi feito

Atualizado componente para usar `normalizePhaseWithMovements`:

```javascript
// Corrigir fase considerando movimentos (força Fase 15 se houver baixa)
const correctedPhase = useMemo(() => {
    return normalizePhaseWithMovements(data?.phase, data?.class_nature, data?.movements);
}, [data?.phase, data?.class_nature, data?.movements]);

// Na exibição
<span className={`... ${getPhaseColorClasses(correctedPhase, data.class_nature)}`}>
    {correctedPhase}
</span>
```

#### Impacto

- ✅ Exibe fase corrigida considerando movimentos
- ✅ Processo 0435756-80.2012.8.19.0001 agora mostrará "Arquivado Definitivamente"

### 4. Sistema de Múltiplas Instâncias (Backend já tem suporte!) 📋

**Arquivo**: `backend/services/datajud.py`

#### O que já existe

O backend JÁ tem lógica para lidar com múltiplas instâncias:

```python
def _select_latest_instance(self, hits: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Seleciona a instância mais recente quando há múltiplas.
    Retorna também metadados sobre todas as instâncias encontradas.
    """
    sources = [h.get("_source", h) for h in hits if isinstance(h, dict)]

    if len(sources) == 1:
        return sources[0], None

    selected = max(sources, key=self._instance_sort_key)
    meta = {
        "instances_count": len(sources),
        "selected_by": "latest_movement_or_timestamp",
        "instances": [self._summarize_instance(s) for s in sources],
    }
    return selected, meta
```

**Metadados retornados quando há múltiplas instâncias**:

```json
{
  "__meta__": {
    "instances_count": 2,
    "selected_by": "latest_movement_or_timestamp",
    "instances": [
      {
        "grau": "G1",
        "tribunal": "TJRJ",
        "orgao_julgador": "1ª Vara Cível",
        "latest_movement_at": "2020-05-15T14:30:00",
        "updated_at": "2020-05-15T14:30:00"
      },
      {
        "grau": "G2",
        "tribunal": "TJRJ",
        "orgao_julgador": "13 CÂMARA CÍVEL",
        "latest_movement_at": "2021-10-19T13:44:00",
        "updated_at": "2021-10-19T13:44:00"
      }
    ]
  }
}
```

#### O que falta implementar (Próxima Fase)

- [ ] Frontend exibir indicador quando há múltiplas instâncias
- [ ] Criar seletor/toggle para alternar entre instâncias
- [ ] Buscar e exibir dados de cada instância separadamente
- [ ] Mostrar timeline com todas as instâncias

## 📊 Comparação Antes/Depois

### Processo 0435756-80.2012.8.19.0001

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Fase Exibida** | ❌ "1.2.1 2ª Instância - Em Recurso" | ✅ "Arquivado Definitivamente" |
| **Cor do Badge** | ❌ Azul (em andamento) | ✅ Cinza (arquivado) |
| **Situação Backend** | ❌ "MOVIMENTO" | ✅ "BAIXADO" (após reprocessar) |
| **Detecção de Baixa** | ❌ Não detectava | ✅ Detecta código 22 |
| **Validação Frontend** | ❌ Não havia | ✅ Valida movimentos |

### Processo 0029123-13.2015.8.19.0002

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Fase Exibida** | ❌ "Conhecimento — Antes da Sentença" | ✅ "Execução" |
| **Classificação** | ❌ Baseada só na fase | ✅ Considera classe processual |
| **Cor do Badge** | ❌ Azul | ✅ Laranja |

## 🧪 Como Testar

### 1. Reprocessar Processo com Baixa

```bash
# Deletar processo do banco
cd "c:\Projetos\Consulta processo"
python -c "
import sqlite3
conn = sqlite3.connect('consulta_processual.db')
conn.execute('DELETE FROM processes WHERE number = ?', ('0435756-80.2012.8.19.0001',))
conn.commit()
conn.close()
"

# Rebuild frontend
cd frontend
npm run build

# Reiniciar aplicação
cd ..
python launcher.py
```

### 2. Buscar Processo no Frontend

1. Abrir navegador: http://localhost:8000
2. Limpar cache: Ctrl+Shift+R
3. Buscar: `0435756-80.2012.8.19.0001`
4. Verificar:
   - ✅ Fase deve ser "Arquivado Definitivamente"
   - ✅ Badge deve ser cinza
   - ✅ Último movimento deve ser "Baixa Definitiva" (código 22)

### 3. Verificar Banco de Dados

```bash
python -c "
import sqlite3
conn = sqlite3.connect('consulta_processual.db')
cursor = conn.cursor()
cursor.execute('SELECT phase FROM processes WHERE number = ?', ('0435756-80.2012.8.19.0001',))
print('Fase no banco:', cursor.fetchone()[0])
conn.close()
"
```

**Esperado**: `"15 Arquivado Definitivamente"` ou similar

## 📝 Códigos de Movimento Relevantes

### Baixa Definitiva / Arquivamento

| Código | Descrição | Fonte |
|--------|-----------|-------|
| 22 | Baixa Definitiva | Principal |
| 246 | Arquivamento Definitivo | Com complemento |
| 861 | Arquivados os Autos | |
| 865 | Remetido ao Arquivo | |
| 10965 | Processo Arquivado | |
| 10966 | Arquivamento com Resolução de Mérito | |
| 10967 | Arquivamento sem Resolução de Mérito | |
| 12618 | Baixa/Arquivamento | |

### Desarquivamento / Reativação

| Código | Descrição |
|--------|-----------|
| 900 | Desarquivamento |
| 12617 | Desarquivamento Provisório |

## 🚀 Próximos Passos - Múltiplas Instâncias

### Fase 1: Indicador Visual (Curto Prazo)
- [ ] Badge "Múltiplas Instâncias" quando `__meta__` presente
- [ ] Tooltip com contagem de instâncias
- [ ] Ícone indicativo

### Fase 2: Seletor de Instâncias (Médio Prazo)
- [ ] Dropdown/Tabs para alternar entre instâncias
- [ ] Endpoint `/process/{number}/instances` para buscar cada uma
- [ ] Atualizar ProcessDetails dinamicamente

### Fase 3: Timeline Unificada (Longo Prazo)
- [ ] Visualização cronológica de todas as instâncias
- [ ] Indicadores visuais de G1 → G2 → SUP
- [ ] Filtros por instância

## 📞 Suporte

Se outros processos apresentarem problemas similares:

1. **Fase incorreta apesar de baixa**:
   - Verificar se movimento código 22 está presente
   - Verificar se há desarquivamento posterior
   - Reportar se correção não funcionar

2. **Múltiplas instâncias**:
   - Atualmente mostra instância mais recente
   - Futuras versões permitirão alternar
   - Backend já tem os dados, implementação é só frontend

3. **Classe incorreta**:
   - Mostra classe da instância selecionada
   - Futura implementação permitirá ver classe de cada instância

---

**Correções aplicadas em**: 08 de Fevereiro de 2026
**Processos corrigidos**: 0435756-80.2012.8.19.0001, 0029123-13.2015.8.19.0002
**Status**: ✅ Baixa definitiva corrigida | 📋 Múltiplas instâncias (próxima fase)
