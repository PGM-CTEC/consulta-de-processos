---
name: fase-processual
description: >
  Classificação autônoma de fase processual de processos judiciais brasileiros a partir das
  APIs do Fusion PAV e DataJud (CNJ). Determina a fase única consolidada (01–15) do processo,
  com suporte a consultas individuais e em lote, log de auditoria detalhado, e mapeamento
  fuzzy de movimentos não padronizados. Prioridade: Fusion PAV → DataJud (fallback).
  Triggers: "fase do processo", "classificar fase", "batch de processos", "qual a fase",
  "Fusion PAV", "DataJud", "movimentos processuais", "consulta processual", "fases processuais".
---

# Skill: Classificação de Fase Processual

Skill para determinação automática da fase processual de processos judiciais brasileiros,
integrando APIs do **Fusion PAV** (sistema interno PGM-Rio) e **DataJud** (CNJ), com
suporte a consultas individuais e em lote, log de auditoria e mapeamento de movimentos.

## Referências internas

- [`references/fases.md`](references/fases.md) — As 15 fases processuais e suas regras
- [`references/movimentos-cnj.md`](references/movimentos-cnj.md) — Códigos CNJ de movimentos
- [`references/fusion-pav.md`](references/fusion-pav.md) — Estrutura de dados e fases do Fusion PAV
- [`references/algoritmo.md`](references/algoritmo.md) — Lógica de decisão e edge cases

---

## Workflow Principal

### Fase 1 — Intake: Identificar modo de operação

```
Input individual:  número CNJ único (ex: 0001234-56.2020.8.19.0001)
Input em lote:     lista de números CNJ (CSV, JSON, array)
```

Sempre verificar:
- Formato CNJ válido: `NNNNNNN-DD.AAAA.J.TT.OOOO` (20 dígitos)
- Para lote: confirmar quantidade e solicitar confirmação se > 100 processos

---

### Fase 2 — Estratégia de Consulta (Dual-API)

**REGRA DE OURO: Fusion PAV primeiro; DataJud apenas como fallback.**

```
PARA CADA processo:
  1. Consultar Fusion PAV
     ├─ SE retornar fase identificável → usar fase do Fusion PAV [LOG: fonte=fusion]
     └─ SE não retornar ou fase indeterminada → ir para passo 2

  2. Consultar DataJud
     ├─ SE retornar dados completos → aplicar algoritmo de classificação
     │   └─ Verificar ausência de 1ª instância (ver Regra Especial #1)
     └─ SE DataJud falhar → registrar erro, retornar "Indeterminado"
```

**Regra Especial #1 — Ausência de 1ª instância no DataJud:**
> Processos com número CNJ terminando em `0000` (campo OOOO) ou `9000` são
> processos originários do tribunal. Os demais (`≠ 0000`) tramitaram em 1ª instância.
> Quando o DataJud retorna **somente** instâncias G2/TR com baixa/arquivamento para
> processo com final ≠ 0000, significa que os autos foram baixados para a origem mas
> a 1ª instância ainda não atualizou. Nesses casos: retornar
> `"Ausência retorno DataJud 1ª instância"` e NÃO usar o DataJud como fonte.

---

### Fase 3 — Algoritmo de Classificação (DataJud)

Aplicar as regras **em ordem de prioridade**:

#### P1 — Baixa Definitiva → Fase 15
```
SE movimento com código ∈ {22, 861, 865, 10965, 10966, 10967, 12618}
   E NÃO há movimento ∈ {900, 12617, 849, 36} POSTERIOR à última baixa
→ Fase 15 (Arquivado Definitivamente)
```

#### P2 — Sobrestamento Ativo → Fase 13 (ou 11/12)
```
SE movimento ∈ {265, 893, 898, 12099, 12100, 12155, 12224} (sobrestamento)
   E NÃO há movimento ∈ {12107, 12108, 12109, 12153, 12154, 12156, 12225} POSTERIOR
→ SE classe = execução → Fase 11 ou 12 (suspensão total ou parcial)
→ SE classe = conhecimento → Fase 13 (Suspenso/Sobrestado)
```

#### P3 — Classe de Execução → Fases 10–14
```
SE classe ∈ {1116, 156, 12078, 159, 229, 1727, 165, 90, ...}
→ Subclassificar: 10 (normal) / 11 (suspensa) / 12 (suspensa parcial) / 14 (conversão)
```

#### P4 — Conhecimento por Instância → Fases 01–09
```
Determinar grau efetivo = maior grau ativo (G1 < G2 < SUP)

SUP ativo:
  + trânsito (848) → Fase 09
  + acórdão (50) sem trânsito → Fase 08
  + sem acórdão → Fase 07

G2 ativo:
  + trânsito (848) → Fase 06
  + acórdão (50) sem trânsito → Fase 05
  + sem acórdão → Fase 04

G1 ativo:
  + trânsito (848) → Fase 03
  + sentença ∈ {246, 198, 200, 219, 220, 235, 236} sem trânsito → Fase 02
  + sem sentença → Fase 01
```

---

### Fase 4 — Mapeamento Fuzzy (Fusion PAV → Fases)

O Fusion PAV retorna descrições textuais de movimentos/fases que podem
**não corresponder exatamente** aos códigos CNJ. Aplicar mapeamento semântico:

Ver [`references/fusion-pav.md`](references/fusion-pav.md) para a tabela completa.

**Regra geral de mapeamento Fusion:**
```
1. Verificar se há campo de fase explícito → mapear diretamente
2. Se não, analisar último movimento significativo:
   - Palavras "sentença" / "julgamento" / "procedente" / "improcedente" → contexto de sentença
   - Palavras "recurso" / "apelação" / "agravo" → contexto recursal
   - Palavras "cumprimento" / "execução" / "penhora" → contexto de execução
   - Palavras "arquivado" / "baixado" / "encerrado" → Fase 15
   - Palavras "suspenso" / "sobrestado" → Fase 13
3. Combinar com grau da instância para determinar fase exata
```

---

### Fase 5 — Output

#### Output padrão (individual)
```json
{
  "numero": "0001234-56.2020.8.19.0001",
  "fase_codigo": "04",
  "fase_nome": "Conhecimento - Recurso 2ª Instância - Pendente Julgamento"
}
```

#### Output em lote
```json
[
  { "numero": "...", "fase_codigo": "04", "fase_nome": "..." },
  { "numero": "...", "fase_codigo": "15", "fase_nome": "Arquivado Definitivamente" },
  { "numero": "...", "fase_codigo": "ERR", "fase_nome": "Erro: [mensagem]" }
]
```

#### Log de auditoria (por processo)
O log é sempre gerado internamente e disponibilizado quando solicitado:
```json
{
  "numero": "...",
  "timestamp": "2026-03-11T10:00:00Z",
  "fonte_primaria": "fusion | datajud | indeterminado",
  "fonte_utilizada": "fusion | datajud",
  "fusion": {
    "consultado": true,
    "fase_retornada": "...",
    "fase_identificavel": true,
    "movimentos_analisados": ["..."],
    "razao_descarte": null
  },
  "datajud": {
    "consultado": false,
    "instancias_retornadas": 0,
    "grau_efetivo": null,
    "situacao": null,
    "regras_aplicadas": [],
    "alertas": []
  },
  "resultado": {
    "fase_codigo": "04",
    "fase_nome": "Conhecimento - Recurso 2ª Instância - Pendente Julgamento",
    "confianca": 0.85,
    "raciocinio": "Processo em G2 sem acórdão identificado. Fonte: Fusion PAV."
  }
}
```

---

## Para geração de código Python

Ao gerar ou corrigir código de classificação, sempre:

1. Ler [`references/algoritmo.md`](references/algoritmo.md) para entender os edge cases documentados
2. Manter a estrutura `ClassificadorFases` + `PhaseAnalyzer` do projeto existente
3. Preservar o contrato de interface: `analyze_unified(all_instances, process_number, tribunal)`
4. Adicionar logging detalhado em cada decisão para fins de auditoria
5. Nunca lançar exceção para o chamador — sempre retornar fase ou mensagem de erro
6. Para Fusion PAV: criar `FusionPAVAnalyzer` paralelo ao `PhaseAnalyzer`, mesmo padrão

### Estrutura esperada dos módulos
```
backend/services/
├── phase_analyzer.py          # DataJud → Fase (existente)
├── classification_rules.py    # Regras determinísticas CNJ (existente)
├── fusion_pav_analyzer.py     # Fusion PAV → Fase (NOVO)
├── phase_orchestrator.py      # Orquestrador dual-API (NOVO)
└── phase_audit_logger.py      # Log estruturado de auditoria (NOVO)
```

---

## Para análise de processos individuais (conversacional)

Quando o usuário fornecer dados de um processo (movimentos, classe, grau):

1. Identificar a fonte dos dados (Fusion PAV ou DataJud)
2. Aplicar o algoritmo da Fase 3 ou Fase 4 conforme a fonte
3. Apresentar o resultado no formato: `[CÓDIGO] Nome da Fase`
4. Incluir raciocínio resumido (qual regra determinou a fase)
5. Alertar sobre casos especiais (DCP/TJRJ, ausência de 1ª instância, baixa confiança)

---

## Edge Cases e Alertas

| Situação | Tratamento |
|----------|-----------|
| Processo DCP/TJRJ (sistema legado, >5 anos) | Retornar fase + sufixo `*` com aviso |
| Final do número = 0000 ou 9000 | Processo originário; DataJud pode não ter G1 |
| Final ≠ 0000, só G2 com baixa no DataJud | `"Ausência retorno DataJud 1ª instância"` |
| Múltiplas instâncias | Usar maior grau **ativo** (sem baixa não revertida) |
| Instância com baixa + reativação posterior | Instância está ativa; incluir movimentos |
| Fusion PAV retorna fase não mapeável | Fallback para DataJud |
| Ambas APIs falham | Fase `"ERR"` com mensagem de erro no log |
| Classe não identificada | Default: conhecimento (G1 → Fase 01) |

---

## Checklist antes de responder

- [ ] Consultei Fusion PAV primeiro?
- [ ] Precisei usar DataJud como fallback?
- [ ] Verifiquei final do número CNJ (0000/9000 vs outros)?
- [ ] Apliquei prioridades na ordem correta (P1→P2→P3→P4)?
- [ ] Verifiquei baixa + reativação para todas as instâncias?
- [ ] Gerei log de auditoria com razões da decisão?
- [ ] O output está no formato `fase_codigo` + `fase_nome`?
