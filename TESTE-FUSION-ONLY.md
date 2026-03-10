# Teste: Classificação de Fase Exclusivamente via Fusion PAV

## Status Atual ✅

Ambos os servidores estão rodando em paralelo:

### Main (DataJud-first com Fusion enrichment)
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Branch:** `main`
- **Classificação:** PhaseAnalyzer (DataJud) → Fusion (fallback/enrichment)

### Fusion-Only (Fusion como única fonte)
- **Frontend:** http://localhost:5174
- **Backend API:** http://localhost:8001
- **Branch:** `feature/fusion-only-classification`
- **Classificação:** DocumentPhaseClassifier (Fusion PAV) exclusivamente

---

## Como Testar

### 1. Abra ambas as aplicações em abas diferentes

```
Main:        http://localhost:5173
Fusion-Only: http://localhost:5174
```

### 2. Teste com um processo que existe em ambas as fontes

**Exemplo:** `0195298-87.2021.8.19.0001`

Abra em ambas as abas e compare:

| Aspecto | Main (5173) | Fusion-Only (5174) |
|---------|------------|------------------|
| **Fase** | Deve vir do DataJud (PhaseAnalyzer) | Deve vir do Fusion (DocumentPhaseClassifier) |
| **Badge** | "DataJud" ou "Fusion" (se enriquecido) | "Fusion" sempre |
| **Dados cadastrais** | Completos (tribunal, vara, classe, etc) | Completos (tribunal, vara, classe, etc) |
| **Movimentações** | CNJ codes do DataJud | Batismos Fusion (tipo_local) |
| **Phase Source** | "datajud" ou "fusion_api" | "fusion_api" ou "fusion_sql" |

### 3. Processe a busca em lote com 5-10 números

Teste o bulk search em ambas as versões para validar que o paralelismo funciona.

### 4. Teste com processo que está **apenas no DataJud**

Procure um processo muito novo que ainda não foi indexado no Fusion:
- **Main:** Deve retornar a fase via DataJud normalmente
- **Fusion-Only:** Deve retornar fase como "Indefinido" com warning

### 5. Teste com processo que está **apenas no Fusion**

Alguns processos mais antigos podem estar no Fusion mas não no DataJud público:
- **Main:** Pode retornar "não encontrado" ou fase via Fusion fallback
- **Fusion-Only:** Deve retornar a fase via Fusion (sucesso esperado)

---

## O Que Observar

### Na versão Main (5173)
- Bloco "Movimentações" contém **códigos CNJ** (ex: 22, 246, 861)
- Bloco "Movimentações Fusion" só aparece se Fusion foi usado para enriquecimento
- `phase_source` = `"datajud"` normalmente, ou `"fusion_api"` se enriquecido

### Na versão Fusion-Only (5174)
- Bloco "Movimentações" contém **códigos CNJ** do DataJud (dados cadastrais)
- Bloco "Movimentações Fusion" sempre aparece (é a fonte da fase)
- `phase_source` sempre = `"fusion_api"` ou `"fusion_sql"`
- Aviso se processo não encontrado no Fusion

---

## Logs para Debugging

Se algo não funcionar, verifique os logs:

```bash
# Backend Main
tail -f /tmp/backend-main.log

# Backend Fusion-Only
tail -f /tmp/backend-fusion.log

# Frontend Main
tail -f /tmp/frontend-main.log

# Frontend Fusion-Only
tail -f /tmp/frontend-fusion.log
```

Procure por linhas com `[Fusion-only]` para ver decisões de classificação na branch experimental.

---

## Parar os Servidores

```bash
# Matar todos os processos Node e Python desta sessão
pkill -f "npm run dev"
pkill -f "uvicorn"
```

---

## Próximas Ações

1. ✅ Branch criada e pushada
2. ✅ Servidores rodando em paralelo
3. **Próximo:** Teste os cenários acima e tome decisão sobre qual abordagem manter

Se a branch Fusion-Only funcionar bem, você pode:
- Mergear para `main` (substituindo o comportamento padrão)
- Manter como branch de experimentação permanente
- Adicionar toggle/feature flag para switch entre modos
