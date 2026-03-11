# Comparativo: Main vs Fusion-Only

## 📊 Sumário Executivo

| Aspecto | Main (5173/8000) | Fusion-Only (5174/8001) |
|---------|------------------|------------------------|
| **Classificação de Fase** | DataJud (PhaseAnalyzer) → Fusion (fallback/enrichment) | Fusion PAV/MNI (DocumentPhaseClassifier) EXCLUSIVAMENTE |
| **Origem de Dados Cadastrais** | DataJud | DataJud |
| **Badge de Fase** | "DataJud" normalmente | "Fusion" sempre |
| **Phase Source** | `"datajud"` ou `"fusion_api"` | `"fusion_api"` ou `"fusion_sql"` |
| **Banner Informativo** | ❌ Não | ✅ Sim (Amarelo/Laranja) |
| **Branch Git** | `main` | `feature/fusion-only-classification` |

---

## 🔍 Detalhes da Classificação

### Main (Padrão - DataJud First)

```
Fluxo:
1. DataJud API → retorna movimentos com códigos CNJ
2. PhaseAnalyzer.analyze() → analisa códigos CNJ → retorna fase
3. Se DataJud não encontrar:
   - Tenta Fusion como fallback
   - DocumentPhaseClassifier classifica a fase
4. Se DataJud encontrar sem 1ª instância:
   - Tenta Fusion para enriquecimento
   - Adiciona dados sintéticos G1
   - Re-analisa fase

Fonte primária: CNJ codes (DataJud)
Fonte secundária: Batismos Fusion (fallback/enrichment)
```

**Metadata no raw_data.__meta__:**
```json
{
  "phase_analysis_mode": "unified" | "single_instance" | "override",
  "unified_phase": "02 Conhecimento - Sentença...",
  "fusion_g1_enriched": false,
  "phase_source": "datajud"
}
```

### Fusion-Only (Experimental)

```
Fluxo:
1. DataJud API → retorna apenas dados cadastrais
   (não usa movimentos para classificação)
2. Fusion PAV → retorna movimentos "batismos"
3. DocumentPhaseClassifier.classify() → analisa batismos → retorna fase
4. Se Fusion não encontrar:
   - phase = "Indefinido"
   - Exibe warning claro

Fonte primária: Batismos Fusion (SEMPRE)
Fonte secundária: Dados cadastrais DataJud (complementar)
```

**Metadata no raw_data.__meta__:**
```json
{
  "phase_analysis_mode": "fusion_only" | "fusion_only_fallback",
  "unified_phase": "02 Conhecimento - Sentença...",
  "fusion_phase_override": "02 Conhecimento - Sentença...",
  "fusion_phase_source": "fusion_api" | "fusion_sql",
  "fusion_phase_warning": null,
  "phase_source": "fusion_api" | "fusion_sql"
}
```

---

## 🎨 Interface

### Main (5173)

```
┌─────────────────────────────────────────┐
│ [Database Icon] Consulta de Processos   │
│ Pesquisa em tribunal judiciário         │
│                                         │
│ [Tabs] Consulta | Lote | Analytics | ...│
└─────────────────────────────────────────┘
│
│ [Busca]
│
│ ┌─────────────────────────────────────┐
│ │ Número: 0195298-87.2021.8.19.0001  │
│ │ Assunto: Ação Ordinária              │
│ │                                     │
│ │ Classe: Ação Ordinária              │
│ │ Tribunal: TJRJ                      │
│ │ Fase: [02 Conhecimento] [DataJud]  │
│ │                                     │
│ │ Movimentações: [CNJ codes]          │
│ └─────────────────────────────────────┘
```

### Fusion-Only (5174)

```
┌──────────────────────────────────────────────────────────┐
│ ⚠️ Modo Experimental: Classificação via Fusion PAV/MNI    │
│ Dados obtidos exclusivamente do Movimento Processual...  │
│ Branch: feature/fusion-only-classification         [X]   │
└──────────────────────────────────────────────────────────┘
├─────────────────────────────────────────┐
│ [Database Icon] Consulta de Processos   │
│ Pesquisa em tribunal judiciário         │
│                                         │
│ [Tabs] Consulta | Lote | Analytics | ...│
└─────────────────────────────────────────┘
│
│ [Busca]
│
│ ┌─────────────────────────────────────┐
│ │ Número: 0195298-87.2021.8.19.0001  │
│ │ Assunto: Ação Ordinária              │
│ │                                     │
│ │ Classe: Ação Ordinária              │
│ │ Tribunal: TJRJ                      │
│ │ Fase: [02 Conhecimento] [Fusion]   │
│ │                                     │
│ │ Movimentações Fusion: [Batismos]    │
│ │ Movimentações: [CNJ codes]          │
│ └─────────────────────────────────────┘
```

---

## 📈 Casos de Teste Recomendados

### Caso 1: Processo em Ambas as Fontes

**Teste:** `0195298-87.2021.8.19.0001`

| Aspecto | Main (5173) | Fusion-Only (5174) |
|---------|------------|------------------|
| Fase encontrada | ✅ Sim | ✅ Sim |
| Fonte fase | DataJud (PhaseAnalyzer) | Fusion (DocumentPhaseClassifier) |
| Badge | DataJud | Fusion |
| Movimentações Fusion | Se enriquecido | Sempre |
| **Resultado esperado** | Fase via CNJ codes | Fase via batismos |

### Caso 2: Processo Apenas no DataJud (Novo)

**Teste:** Processo recente não ainda indexado no Fusion

| Aspecto | Main (5173) | Fusion-Only (5174) |
|---------|------------|------------------|
| Fase encontrada | ✅ Sim | ❌ Não |
| Fonte fase | DataJud (PhaseAnalyzer) | Indefinido |
| Badge | DataJud | - |
| Warning | Não | ✅ Sim |
| **Resultado esperado** | Classificação normal | Aviso "não encontrado no Fusion" |

### Caso 3: Processo Apenas no Fusion (Antigo)

**Teste:** Processo antigo não exposto no DataJud público

| Aspecto | Main (5173) | Fusion-Only (5174) |
|---------|------------|------------------|
| Fase encontrada | ❌ Não encontrado | ✅ Sim |
| Fonte fase | N/A | Fusion (DocumentPhaseClassifier) |
| Badge | N/A | Fusion |
| **Resultado esperado** | Não encontrado | Fase via Fusion |

---

## 💡 Insights de Implementação

### Por que Deux Fontes?

**Main (DataJud First):**
- DataJud é a base pública oficial
- CNJ codes já foram validados pelo tribunal
- Fusion como backup garante cobertura total

**Fusion-Only:**
- Teste hipótese: Fusion é mais preciso/consistente?
- Reduz dependência de DataJud
- Pode revelar diferenças de classificação

### Diferenças de Classificação Esperadas

Como os classificadores operam diferentemente:

| Cenário | DataJud (CNJ codes) | Fusion (Batismos) |
|---------|-------------------|------------------|
| **Sentença proferia** | Código 246 = não baixa | Descrição "Sentença" = fase 02 |
| **Trânsito em julgado** | Código para "transitado" | Batismo contém "transitado" |
| **Remessa recursal** | Código remessa imediata | Batismo "remessa" posterior |
| **Processos antigos** | Pode não ter CNJ codes completos | Sempre tem "batismos" |

---

## 🔧 Logs para Análise

### Backend Main (8000)
```bash
tail -f /tmp/backend-main.log | grep -i "phase\|analyzer"
```

Procure por logs do `PhaseAnalyzer.analyze()` e `analyze_unified()`

### Backend Fusion-Only (8001)
```bash
tail -f /tmp/backend-fusion.log | grep -i "fusion-only\|classifier"
```

Procure por logs com prefixo `[Fusion-only]` e chamadas do `DocumentPhaseClassifier.classify()`

---

## 🎯 Decisão Pós-Teste

Após testar ambas as versões, você poderá:

### ✅ Aceitar Fusion-Only
- Mergear `feature/fusion-only-classification` → `main`
- Remover código legado de DataJud-first
- Usar Fusion como fonte oficial de classificação

### 🔄 Manter Ambas (Toggle)
- Adicionar feature flag: `--use-fusion-only` ou similar
- Permitir switch entre modos via API ou UI
- Útil para comparação contínua

### ❌ Manter Main (Padrão)
- Manter `feature/fusion-only-classification` como branch experimental
- Usar para debugging de casos específicos
- Considerar melhorias ao DataJud-first

---

## 📝 Documentação Adicional

- **TESTE-FUSION-ONLY.md** — Guia prático de teste
- **backend/services/process_service.py** — Lógica implementada
- **frontend/src/components/FusionOnlyBanner.jsx** — Banner informativo
