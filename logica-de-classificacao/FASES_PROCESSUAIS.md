# Fases Processuais — Guia Completo

**Versão:** 2.0 — Fevereiro 2026
**Baseado em:** Classificação oficial PGM-Rio
**Aplicação:** Sistema de Consulta Processual

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [As 15 Fases Processuais](#as-15-fases-processuais)
3. [Fases de Conhecimento (01-09)](#fases-de-conhecimento-01-09)
4. [Fases de Execução (10-12, 14)](#fases-de-execução-10-12-14)
5. [Fases Transversais e Finais (13, 15)](#fases-transversais-e-finais-13-15)
6. [Regras de Transição](#regras-de-transição)
7. [Determinação Automática de Fases](#determinação-automática-de-fases)
8. [Baixa Definitiva e Arquivamento](#baixa-definitiva-e-arquivamento)

---

## Visão Geral

O sistema classifica processos em **15 fases oficiais**, agrupadas em 3 categorias:

| Categoria | Fases | Descrição |
|-----------|-------|-----------|
| **Conhecimento** | 01-09 | Processo em julgamento (1ª, 2ª instância, superiores) |
| **Execução** | 10-12, 14 | Processo em fase de cumprimento de sentença |
| **Transversal/Final** | 13, 15 | Suspensão ou arquivamento |

---

## As 15 Fases Processuais

### Fases de Conhecimento (01-09)

Processos que ainda estão em julgamento ou aguardando recursos.

#### **01 — Conhecimento — Antes da Sentença**
- **Código:** 01
- **Tipo:** Conhecimento
- **Descrição:** Processo em 1ª instância, anterior à sentença.
- **Características:**
  - Fase inicial do processo
  - Audiências, perícias, produção de provas
  - Ainda não há sentença
- **Próximas fases possíveis:** 02, 13, 15
- **Cor no sistema:** Azul claro (sky)

#### **02 — Conhecimento — Sentença sem Trânsito em Julgado**
- **Código:** 02
- **Tipo:** Conhecimento
- **Descrição:** Sentença proferida, mas recurso ainda é possível.
- **Características:**
  - Sentença de 1ª instância já foi proferida
  - Prazo para recurso ainda está aberto
  - Processo não é definitivo
- **Próximas fases possíveis:** 03, 04, 13, 15
- **Cor no sistema:** Azul (blue)

#### **03 — Conhecimento — Sentença com Trânsito em Julgado**
- **Código:** 03
- **Tipo:** Conhecimento
- **Descrição:** Sentença de 1ª instância definitiva, sem recursos pendentes.
- **Características:**
  - Prazos recursais esgotados
  - Sentença é imutável
  - Pronta para execução (se cobrada)
- **Próximas fases possíveis:** 10, 14, 13, 15
- **Cor no sistema:** Indigo (indigo)

#### **04 — Conhecimento — Recurso 2ª Instância — Pendente Julgamento**
- **Código:** 04
- **Tipo:** Conhecimento
- **Descrição:** Recurso foi interposto para 2ª instância; julgamento ainda pendente.
- **Características:**
  - Apelação ou Agravo de Instrumento em tramitação
  - Processo aguarda julgamento do tribunal
  - Pode haver sustentação oral
- **Próximas fases possíveis:** 05, 13, 15
- **Cor no sistema:** Violeta (violet)

#### **05 — Conhecimento — Recurso 2ª Instância — Julgado sem Trânsito**
- **Código:** 05
- **Tipo:** Conhecimento
- **Descrição:** 2ª instância julgou, mas novo recurso (para superiores) ainda é possível.
- **Características:**
  - Tribunal julgou a apelação
  - Prazo para recurso extraordinário/especial ainda está aberto
  - Sentença de 2ª não é definitiva
- **Próximas fases possíveis:** 06, 07, 13, 15
- **Cor no sistema:** Roxo (purple)

#### **06 — Conhecimento — Recurso 2ª Instância — Transitado em Julgado**
- **Código:** 06
- **Tipo:** Conhecimento
- **Descrição:** Julgamento em 2ª instância é definitivo; sem recursos pendentes.
- **Características:**
  - Prazos para STF/STJ esgotados
  - Decisão de 2ª instância é imutável
  - Pronta para execução (se cobrada)
- **Próximas fases possíveis:** 10, 14, 13, 15
- **Cor no sistema:** Fucsia (fuchsia)

#### **07 — Conhecimento — Recurso Tribunais Superiores — Pendente Julgamento**
- **Código:** 07
- **Tipo:** Conhecimento
- **Descrição:** Recurso interposto para STF/STJ; julgamento ainda pendente.
- **Características:**
  - Recurso extraordinário ou especial em tramitação
  - Processo aguarda julgamento em tribunal superior
  - Análise de questões constitucionais ou federais
- **Próximas fases possíveis:** 08, 13, 15
- **Cor no sistema:** Rosa (pink)

#### **08 — Conhecimento — Recurso Tribunais Superiores — Julgado sem Trânsito**
- **Código:** 08
- **Tipo:** Conhecimento
- **Descrição:** Tribunal superior julgou, mas novo recurso ainda é possível.
- **Características:**
  - STF/STJ julgaram o recurso
  - Pode haver interposição de novo recurso ou embargos
  - Decisão pode ser contestada ainda
- **Próximas fases possíveis:** 09, 13, 15
- **Cor no sistema:** Rosa buscado (rose)

#### **09 — Conhecimento — Recurso Tribunais Superiores — Transitado em Julgado**
- **Código:** 09
- **Tipo:** Conhecimento
- **Descrição:** Decisão de tribunal superior é definitiva e imutável.
- **Características:**
  - Última instância foi esgotada
  - Julgamento é absolutamente irrecorrível
  - Pronta para execução (se cobrada)
- **Próximas fases possíveis:** 10, 14, 13, 15
- **Cor no sistema:** Vermelho (red)

---

### Fases de Execução (10-12, 14)

Processos em fase de cumprimento de sentença/decisão.

#### **10 — Execução**
- **Código:** 10
- **Tipo:** Execução
- **Descrição:** Processo em fase de execução/cumprimento normal.
- **Características:**
  - Sentença já transitou em julgado
  - Executado está pagando ou bens estão sendo penhorados
  - Processo segue seu curso normal
- **Próximas fases possíveis:** 11, 12, 13, 15
- **Cor no sistema:** Laranja (orange)

#### **11 — Execução Suspensa**
- **Código:** 11
- **Tipo:** Execução
- **Descrição:** Execução foi suspensa (ex: por acordo parcial, decisão judicial).
- **Características:**
  - Execução temporariamente paralisada
  - Pode ser retomada quando condição cessar
  - Comum em casos de parcelamento
- **Próximas fases possíveis:** 10, 12, 13, 15
- **Cor no sistema:** Âmbar (amber)

#### **12 — Execução Suspensa Parcialmente (Impugnação Parcial)**
- **Código:** 12
- **Tipo:** Execução
- **Descrição:** Parte da execução foi suspensa (impugnação de parte do valor).
- **Características:**
  - Parte do valor é executada normalmente
  - Parte é suspensa por discussão/impugnação
  - Execução dual (prossigue parcialmente)
- **Próximas fases possíveis:** 10, 11, 13, 15
- **Cor no sistema:** Amarelo (yellow)

#### **14 — Conversão em Renda**
- **Código:** 14
- **Tipo:** Execução
- **Descrição:** Processo foi convertido em renda (arresto de bens para gerar renda).
- **Características:**
  - Bens foram arrestados para produzir renda
  - Não venda do bem, mas aluguel/fruição
  - Alternativa ao pagamento em dinheiro
- **Próximas fases possíveis:** 10, 13, 15
- **Cor no sistema:** Verde (green)

---

### Fases Transversais e Finais (13, 15)

#### **13 — Suspenso / Sobrestado**
- **Código:** 13
- **Tipo:** Transversal
- **Descrição:** Processo suspenso ou sobrestado por decisão judicial.
- **Características:**
  - Suspensão por ordem judicial (ex: prejudicialidade, decisão pendente)
  - Não é a mesma que execução suspensa
  - Pode afetar processos em qualquer fase
  - Requerida por decisão do juiz
- **Próximas fases possíveis:** Qualquer fase (após desobrestamento)
- **Cor no sistema:** Lima (lime)

#### **15 — Arquivado Definitivamente**
- **Código:** 15
- **Tipo:** Final
- **Descrição:** Processo foi encerrado e arquivado definitivamente.
- **Características:**
  - Sentença foi cumprida completamente
  - OU baixa definitiva foi decretada
  - OU prescrito
  - Processo encerrado judicialmente
  - Não há retorno a esta fase
- **Próximas fases possíveis:** NENHUMA (fase final)
- **Cor no sistema:** Cinza ardósia (slate)

---

## Regras de Transição

### Fluxo Conhecimento → Execução

```
01 → 02 → 03 → [10/14] (pronto para executar)
           ↓
        04 → 05 → 06 → [10/14]
           ↓
           07 → 08 → 09 → [10/14]
```

**Regra:** Qualquer fase de conhecimento pode ir direto para execução se a sentença transitar.

### Fluxo de Suspensão/Arquivamento

```
[Qualquer fase] → 13 (suspenso/sobrestado)
[Qualquer fase] → 15 (arquivado definitivamente)
```

**Regra:** Suspensão e arquivamento são transversais (podem ocorrer em qualquer fase).

### Transições Bloqueadas

- **De 15:** Nenhuma (processo encerrado)
- **Para 13/15:** Requer ato judicial explícito

---

## Determinação Automática de Fases

O sistema determina a fase automaticamente baseado em:

### 1. **Classe Processual**
Classes de **Execução** indicam fases 10-12, 14:
- "Execução", "Cumprimento de Sentença", "Cumprimento de Sentenca"
- "Execução Fiscal", "Execucao Fiscal"
- "Execução de Título", "Execucao de Titulo"

### 2. **Movimentos Processuais**
- Código 22, 246, 861, 865, 10965-10967, 12618 = **Baixa Definitiva (Fase 15)**
- Código 900, 12617 = **Desarquivamento (anula Fase 15)**

### 3. **Descrição da Fase**
Palavras-chave mapeadas:
- "Sentença", "Transitado", "Recurso" → Conhecimento (01-09)
- "Execução", "Cumprimento" → Execução (10-12, 14)
- "Suspenso", "Sobrestado" → Fase 13
- "Arquivado", "Baixa Definitiva" → Fase 15

### 4. **Instância**
- 1ª Instância (G1/JE) → Fases 01-03
- 2ª Instância (G2/TR) → Fases 04-06
- Tribunais Superiores → Fases 07-09

### 5. **Árvore de Documentos PAV (3ª Fonte — Março 2026)**

**Endpoint:** `GET /services/arquivos/arvore-processo-by-sistema/{cnj}`

Cada documento juntado ao processo (`nomeArquivo` + `dataAutuacao`) é tratado como um
"batismo" e processado pelo `DocumentPhaseClassifier`, da mesma forma que os movimentos
do Fusion. Por representar os documentos **realmente juntados aos autos**, esta fonte
é particularmente precisa para:

| Documento na árvore | Inferência de fase |
|--------------------|--------------------|
| "Sentença de Mérito", "Sentença" | Fase 02 (sem trânsito) ou 03 (com certidão) |
| "Apelação", "Agravo de Instrumento" | Fase 04 (recurso em 2ª instância) |
| "Acórdão", "Certidão de Julgamento" | Fase 05 (julgado na 2ª instância) |
| "Certidão de Trânsito em Julgado" | Fase 03 ou superior |
| "Arquivamento", "Baixa Definitiva" | Fase 15 |
| Documentos G1 após "Remessa" | Remessa foi lateral — NÃO é fase 04 |

**Ordenação interna por tribunal:**
- DCP (TJRJ legado): por `numeroFolha` ASC
- PJe, eProc, STJ, STF, TRT, TRF2: por `id` (numérico) ASC

**Consolidação tri-fonte (prioridade decrescente):**
1. Execução sobrescreve Conhecimento em qualquer das 3 fontes
2. PAV Tree + Fusion concordam → PAV Tree (alta confiança)
3. PAV Tree disponível → PAV Tree preferida sobre Fusion e DataJud
4. Somente Fusion → Fusion
5. Somente DataJud → DataJud (fallback final)

Esta fonte também é exibida visualmente na interface acima das "Movimentações Fusion"
e das "Movimentações DataJud", permitindo ao usuário verificar os documentos ao avaliar
a fase do processo.

---

## Baixa Definitiva e Arquivamento

### O que é Baixa Definitiva?

**Baixa Definitiva** é um ato judicial que encerra permanentemente o processo.

**Códigos CNJ que indicam Baixa:**
- 22 — Baixa da Distribuição
- 246 — Baixa do Sistema
- 861 — Encerramento do Processo
- 865 — Reabertura de Autos
- 10965 — Arquivamento
- 10966 — Retirada de Arquivo
- 10967 — Julgamento por Desistência
- 12618 — Encerramento por Resolução

### Anulação de Baixa

A baixa pode ser **revertida** por:
- Código 900 — Retomada de Autos
- Código 12617 — Reabertura/Relocação

Se houver movimento de anulação **após** a baixa, o processo NÃO está mais em Fase 15.

### Regra do Sistema

```python
if há movimento de Baixa (código 22, 246, etc):
    if há movimento de Anulação (código 900, 12617) APÓS a Baixa:
        fase = normalizePhase(...)  # Volta à fase anterior
    else:
        fase = 15  # Arquivado Definitivamente
```

---

## 📊 Mapa Visual das Fases

```
┌─────────────────────────────────────────────────────────────┐
│                    PROCESSO JUDICIAL                         │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
          ┌─────▼──────┐            ┌──────▼─────┐
          │ CONHECIMENTO│            │ EXECUÇÃO   │
          │   (01-09)   │            │  (10-14)   │
          └─────┬──────┘            └──────┬─────┘
                │                           │
    ┌───────────┼───────────┐             │
    │           │           │             │
   01          04          07            10
  (antes)     (2ª pend)   (SUP pend)    (normal)
    │           │           │             │
   02          05          08            11
 (sem transit) (2ª jugado) (SUP jugado) (suspensa)
    │           │           │             │
   03          06          09            12
 (com transit) (2ª transit)(SUP transit) (parcial)
    │           │           │             │
    └───────────┴───────────┴─────────────┘
                │
        ┌───────┴───────┐
        │               │
       13              14
    (suspenso)    (conversão)
        │               │
        └───────┬───────┘
                │
               15
          (ARQUIVADO)
            [FIM]
```

---

## Exemplo: Fluxo Típico de um Processo

### Cenário 1: Processo Contencioso Normal
```
1. Cliente inicia ação        → Fase 01 (Antes da Sentença)
2. Sentença proferida         → Fase 02 (Sem Trânsito)
3. Prazos recursais expiram   → Fase 03 (Com Trânsito)
4. Executado paga             → Fase 10 (Execução Normal)
5. Processo encerrado         → Fase 15 (Arquivado)
```

### Cenário 2: Processo com Recurso
```
1. Sentença sem trânsito      → Fase 02
2. Apelação interposta        → Fase 04 (2ª Pend.)
3. TJ julga a apelação        → Fase 05 (2ª Jugado)
4. Prazos para STJ expiram    → Fase 06 (2ª Transit)
5. Cumprimento de sentença    → Fase 10 (Execução)
6. Arquivamento               → Fase 15
```

### Cenário 3: Processo Suspenso
```
1. Processo em conhecimento   → Fase 02
2. Juiz decreta suspensão     → Fase 13 (Suspenso)
3. Condição cessa             → Retorna à Fase anterior
4. Julgamento prossegue       → Fase 03, 04, etc.
```

---

## 🔧 Implementação Técnica

### Arquivo de Configuração
- **Frontend:** `frontend/src/constants/phases.js`
- **Backend:** Validação de fases em `backend/services/phase_analyzer.py`

### Função de Normalização
```javascript
normalizePhase(phaseInput, classNature)
  → Retorna: Nome oficial da fase (01-15)
  → Entrada: Código, descrição ou nome da API
```

### Função com Movimentos
```javascript
normalizePhaseWithMovements(phaseInput, classNature, movements)
  → Verifica movimentos de Baixa/Arquivamento
  → Força Fase 15 se há Baixa não revertida
```

---

## 📌 Resumo das Regras

| Aspecto | Regra |
|---------|-------|
| **Transições** | Conhecimento → Execução → Arquivo; Suspensão é transversal |
| **Baixa Definitiva** | Código 22 + ausência de anulação (900, 12617) = Fase 15 |
| **Classe vs Instância** | Classe "Execução" define fases 10-14 independente de instância |
| **Fase Padrão** | Se indeterminado: Fase 01 (Conhecimento) ou 10 (Execução) |
| **Fase Final** | 15 (Arquivado) é irreversível no contexto do sistema |

---

## 📞 Suporte

Para dúvidas sobre fases processuais ou implementação:
- Consulte `frontend/src/constants/phases.js` para detalhes técnicos
- Verifique `backend/services/phase_analyzer.py` para lógica de análise
- Veja `CLAUDE.md` para instruções de desenvolvimento

---

**Versão:** 2.0 (Fevereiro 2026)
**Última atualização:** 2026-03-06
