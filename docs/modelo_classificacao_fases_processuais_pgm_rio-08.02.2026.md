# MODELO DE CLASSIFICAÇÃO DE FASES PROCESSUAIS
## Procuradoria-Geral do Município do Rio de Janeiro

**Coordenação de Tecnologia**

**Regras de Classificação baseadas em Classes, Movimentos e Documentos**  
**Tabelas Processuais Unificadas do CNJ (Res. 46/2007 e 326/2020)**

**Versão 2.0 — Fevereiro de 2026**

---

## Sumário

1. [Visão Geral do Modelo](#1-visão-geral-do-modelo)
2. [Arquitetura do Sistema de Classificação](#2-arquitetura-do-sistema-de-classificação)
3. [Identificação do Grau de Jurisdição](#3-identificação-do-grau-de-jurisdição)
4. [Regras de Classificação Detalhadas](#4-regras-de-classificação-detalhadas)
5. [Tabelas Consolidadas de Códigos CNJ](#5-tabelas-consolidadas-de-códigos-cnj)
6. [Algoritmo de Classificação](#6-algoritmo-de-classificação)
7. [Integração com MNI/DEJT](#7-integração-com-mnidejt)
8. [Exemplos de Classificação](#8-exemplos-de-classificação)
9. [Glossário e Referências](#9-glossário-e-referências)

---

## 1. Visão Geral do Modelo

### 1.1 Objetivo

Este documento estabelece as regras de classificação automática de fases processuais para o sistema de acompanhamento de processos judiciais da PGM-Rio, baseado na análise combinada de **Classes**, **Movimentos** e **Documentos** da Tabela Processual Unificada do CNJ.

### 1.2 Fases Processuais Definidas

| Código | Fase Processual | Tipo |
|:------:|-----------------|------|
| **01** | Conhecimento — Antes da Sentença | Conhecimento |
| **02** | Conhecimento — Sentença sem Trânsito em Julgado | Conhecimento |
| **03** | Conhecimento — Sentença com Trânsito em Julgado | Conhecimento |
| **04** | Conhecimento — Recurso 2ª Instância — Pendente Julgamento | Conhecimento |
| **05** | Conhecimento — Recurso 2ª Instância — Julgado sem Trânsito | Conhecimento |
| **06** | Conhecimento — Recurso 2ª Instância — Transitado em Julgado | Conhecimento |
| **07** | Conhecimento — Recurso Tribunais Superiores — Pendente Julgamento | Conhecimento |
| **08** | Conhecimento — Recurso Tribunais Superiores — Julgado sem Trânsito | Conhecimento |
| **09** | Conhecimento — Recurso Tribunais Superiores — Transitado em Julgado | Conhecimento |
| **10** | Execução | Execução |
| **11** | Execução Suspensa | Execução |
| **12** | Execução Suspensa Parcialmente (Impugnação Parcial) | Execução |
| **13** | Suspenso / Sobrestado | Transversal |
| **14** | Conversão em Renda | Execução |
| **15** | Arquivado Definitivamente | Final |

### 1.3 Hierarquia de Prioridades

O algoritmo aplica as verificações na seguinte ordem de prioridade (a primeira condição satisfeita determina a fase):

```
PRIORIDADE 1 → Fase 15 (Arquivado Definitivamente)
PRIORIDADE 2 → Fase 13 (Suspenso/Sobrestado)
PRIORIDADE 3 → Fase 14 (Conversão em Renda) — se Execução
PRIORIDADE 4 → Fases 11/12 (Execução Suspensa) — se Execução
PRIORIDADE 5 → Fase 10 (Execução) — se Classe Executiva
PRIORIDADE 6 → Fases 01-09 (Conhecimento) — por grau e julgamento
```

---

## 2. Arquitetura do Sistema de Classificação

### 2.1 Tríade CMD

A classificação baseia-se na análise conjunta de três elementos padronizados pelo CNJ:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          TRÍADE CMD                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   C - CLASSE PROCESSUAL                                                  │
│       ├── Determina se Conhecimento ou Execução                          │
│       └── Define contexto processual (JEC, Fazenda, Comum)               │
│                                                                          │
│   M - MOVIMENTO PROCESSUAL                                               │
│       ├── Identifica eventos que alteram estado                          │
│       ├── Possui complementos textuais (análise semântica)               │
│       └── Vinculado a grau de jurisdição                                 │
│                                                                          │
│   D - DOCUMENTO PROCESSUAL                                               │
│       ├── Confirma ou desambigua movimentos genéricos                    │
│       └── Auxilia na detecção de defesas e recursos                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Pipeline de Classificação

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Dados MNI   │────▶│  Conversor   │────▶│ Classificador│────▶│  Resultado   │
│  (JSON/XML)  │     │  (Parsing)   │     │ Determinístico│    │ Estruturado  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │ Validação LLM│ (Opcional)
                                          │  (Contexto)  │
                                          └──────────────┘
```

### 2.3 Classes Processuais

#### Classes de CONHECIMENTO

| Código | Descrição | Observação |
|--------|-----------|------------|
| 7 | Procedimento Comum Cível | Principal classe de conhecimento |
| 65 | Ação Civil Pública | Tutela coletiva |
| 120 | Mandado de Segurança Cível | Rito especial |
| 1707 | Procedimento do Juizado Especial | JEC |
| 175 | Ação Popular | Tutela coletiva |
| 26 | Ação Anulatória | Tributário |
| 1310 | Ação de Improbidade Administrativa | Lei 8.429/92 |
| 27 | Ação Rescisória | Competência originária |
| 66 | Ação de Exigir Contas | Especial |
| 1386 | Reclamação | STF/STJ |

#### Classes de EXECUÇÃO

| Código | Descrição | Observação |
|--------|-----------|------------|
| 1116 | Execução Fiscal | LEF — Fazenda como AU |
| 156 | Cumprimento de Sentença | CPC/2015 |
| 12078 | Cumprimento de Sentença contra Fazenda Pública | Art. 534-535 CPC |
| 159 | Execução de Título Extrajudicial | Genérica |
| 229 | Execução de Alimentos | Especial |
| 1727 | Cumprimento de Sentença - JEC | Juizado |
| 165 | Execução contra a Fazenda Pública | Art. 910 CPC |
| 127 | Ação Monitória | Rito especial |

---

## 3. Identificação do Grau de Jurisdição

### 3.1 Graus Definidos

| Código | Grau | Órgãos Típicos |
|--------|------|----------------|
| G1 | 1ª Instância | Varas, JECs, Juízos de Execução |
| JE | Juizado Especial | JECs, Turmas Recursais |
| G2 | 2ª Instância | TJs, TRFs, Câmaras, Turmas |
| SUP | Tribunais Superiores | STF, STJ, TST |

### 3.2 Algoritmo de Identificação

A identificação do grau segue ordem de prioridade:

```python
def identificar_grau(processo):
    # PRIORIDADE 1: Grau explícito no processo
    if processo.grau_atual != DESCONHECIDO:
        return processo.grau_atual
    
    # PRIORIDADE 2: Classe processual determina grau
    if processo.classe_codigo in CLASSES_ORIGINARIAS_G2:
        return G2
    if processo.classe_codigo in CLASSES_ORIGINARIAS_SUP:
        return SUP
    if processo.classe_codigo in CLASSES_JEC:
        return JE
    
    # PRIORIDADE 3: Código do órgão julgador
    if processo.codigo_orgao:
        return identificar_grau_por_orgao(processo.codigo_orgao)
    
    # PRIORIDADE 4: Análise dos movimentos
    for mov in processo.movimentos_ordenados_desc:
        if mov.grau != DESCONHECIDO:
            return mov.grau
    
    # PRIORIDADE 5: Default
    return G1
```

### 3.3 Mapeamento de Órgãos Julgadores

| Prefixo Código | Grau | Exemplo |
|----------------|------|---------|
| 8.19.0001.* | G1 | Varas do TJRJ |
| 8.19.9000.* | G2 | Câmaras Cíveis TJRJ |
| 8.19.9100.* | G2 | Órgão Especial TJRJ |
| 2.1.0000.* | SUP | STF |
| 2.2.0000.* | SUP | STJ |
| 2.5.0000.* | SUP | TST |

### 3.4 Classes de Competência Originária

```python
# Classes originárias de G2 (Tribunais de Justiça)
CLASSES_ORIGINARIAS_G2 = {
    27,    # Ação Rescisória
    125,   # Mandado de Segurança (competência originária TJ)
    126,   # Habeas Corpus
    128,   # Habeas Data
    190,   # Conflito de Competência
    203,   # Correição Parcial
    # ... outras
}

# Classes originárias de Tribunais Superiores
CLASSES_ORIGINARIAS_SUP = {
    1386,  # Reclamação (STF/STJ)
    11529, # ADPF
    11528, # ADI
    11530, # ADC
    # ... outras
}

# Classes de Juizado Especial
CLASSES_JEC = {
    1707,  # Procedimento do Juizado Especial
    1727,  # Cumprimento de Sentença JEC
    436,   # Carta Precatória JEC
    # ... outras
}
```

---

## 4. Regras de Classificação Detalhadas

### 4.1 Fase 15 — Arquivado Definitivamente

**Prioridade:** MÁXIMA (verificar primeiro)

**Descrição:** Processo com baixa definitiva — arquivamento final após satisfação, extinção ou cumprimento integral.

#### Critérios de Identificação

| Critério | Condição |
|----------|----------|
| Situação | `situacao IN ('BAIXADO', 'ARQUIVADO', 'ARQUIVADO DEFINITIVAMENTE')` |
| Movimento | `EXISTS(movimento.codigo IN MOVIMENTOS_BAIXA_DEFINITIVA)` |

#### Códigos CNJ — Movimentos de Baixa Definitiva

| Código | Descrição |
|--------|-----------|
| 22 | Baixa Definitiva |
| 246 | Arquivamento Definitivo (com complemento de extinção) |
| 861 | Arquivados os Autos |
| 865 | Remetido ao Arquivo |
| 10965 | Processo Arquivado |
| 10966 | Arquivamento com Resolução de Mérito |
| 10967 | Arquivamento sem Resolução de Mérito |
| 12618 | Baixa/Arquivamento |

#### Regra Lógica

```
SE situacao ∈ {'BAIXADO', 'ARQUIVADO', 'ARQUIVADO DEFINITIVAMENTE'}
   OU EXISTS(movimento ∈ MOVIMENTOS_BAIXA_DEFINITIVA)
ENTÃO fase = 15
```

---

### 4.2 Fase 13 — Suspenso / Sobrestado

**Prioridade:** 2 (após verificar arquivamento)

**Descrição:** Processo (conhecimento ou execução) suspenso por determinação judicial — repercussão geral, recurso repetitivo, IRDR, IAC, decisão judicial externa.

#### Critérios de Identificação

| Critério | Condição |
|----------|----------|
| Movimento | `EXISTS(movimento ∈ MOVIMENTOS_SOBRESTAMENTO)` |
| Condição | `NOT EXISTS(movimento_levantamento POSTERIOR ao sobrestamento)` |

#### Códigos CNJ — Movimentos de Sobrestamento

| Código | Descrição | Tipo |
|--------|-----------|------|
| 265 | Processo Suspenso por Repercussão Geral | STF |
| 893 | Suspenso por Prejudicialidade Externa | Genérico |
| 898 | Suspenso ou Sobrestado por Decisão Judicial | Genérico |
| 12099 | Sobrestado por Recurso Repetitivo | STJ |
| 12100 | Suspenso por IRDR | TJ |
| 12155 | Sobrestado por IAC | Tribunais |
| 12224 | Sobrestado Aguardando Grupo de Representativos | Repetitivos |
| 14975 | Sobrestado — RE com RG Reconhecida | STF |
| 11975 | Sobrestado — Recurso Repetitivo | STJ |
| 14976 | Sobrestado — REsp Repetitivo | STJ |
| 12098 | Sobrestado — IRDR | TJ |
| 14985 | Sobrestado — IRDR (alternativo) | TJ |
| 14968 | Sobrestado — IAC | Tribunais |
| 14979 | Sobrestado — IAC (alternativo) | Tribunais |
| 12066 | Sobrestado — Outro Motivo | Subsidiário |

#### Códigos CNJ — Movimentos de Levantamento/Dessobrestamento

| Código | Descrição |
|--------|-----------|
| 899 | Levantamento de Suspensão |
| 900 | Levantamento de Sobrestamento |
| 12107 | Dessobrestamento por Julgamento de Mérito |
| 12108 | Dessobrestamento por Cancelamento |
| 12109 | Dessobrestamento por Revisão de Tese |
| 12153 | Levantamento de Suspensão — Recurso Repetitivo |
| 12154 | Levantamento de Suspensão — IRDR |
| 11994 | Dessobrestamento — RE/RG |
| 11995 | Dessobrestamento — REsp Repetitivo |
| 11996 | Dessobrestamento — Genérico |
| 14990 | Dessobrestamento — Específico |
| 14991 | Dessobrestamento — Específico (alternativo) |

#### Regra Lógica

```
SE EXISTS(mov_sobrestamento)
   E NOT EXISTS(mov_levantamento.data_hora > mov_sobrestamento.data_hora)
ENTÃO fase = 13
```

---

### 4.3 Fase 14 — Conversão em Renda

**Prioridade:** 3 (apenas para classes de execução com Fazenda como autora)

**Descrição:** Depósito judicial convertido em renda da Fazenda Pública.

#### Critérios de Identificação

| Critério | Condição |
|----------|----------|
| Classe | `classe ∈ CLASSES_EXECUCAO` |
| Polo | `polo_fazenda = 'AU'` (Fazenda como Autora/Exequente) |
| Movimento | `EXISTS(movimento ∈ MOVIMENTOS_CONVERSAO_RENDA)` |
| Complemento | Análise textual indica beneficiário = Fazenda |

#### Códigos CNJ — Movimentos de Conversão em Renda

| Código | Descrição |
|--------|-----------|
| 7087 | Conversão em Renda da União/Ente |
| 7961 | Receita Dívida Ativa — Depósito Judicial |
| 11380 | Depósito Judicial Realizado |
| 11381 | Depósito em Garantia do Juízo |
| 11382 | Depósito para Suspensão de Exigibilidade |
| 11383 | Depósito Recursal |
| 11390 | Conversão de Depósito em Renda |
| 11391 | Alvará de Levantamento — Fazenda |
| 11392 | Transferência para Conta do Ente |
| 11393 | Ofício de Conversão em Renda |
| 60700 | Expedição de Alvará |
| 60701 | Alvará Expedido |
| 60702 | Alvará Cumprido |
| 864 | Depósito Judicial |
| 867 | Levantamento de Depósito |

#### Análise de Complemento

```python
BENEFICIARIOS_FAZENDA = [
    "fazenda", "município", "exequente", "ente público",
    "pgm", "procuradoria", "rio de janeiro", "fisco",
    "tesouro", "receita", "credor"
]

def verificar_conversao_renda(movimento):
    complemento = (movimento.complemento or "").lower()
    return any(benef in complemento for benef in BENEFICIARIOS_FAZENDA)
```

#### Regra Lógica

```
SE classe ∈ EXECUÇÃO
   E polo_fazenda = 'AU'
   E EXISTS(mov ∈ MOVIMENTOS_CONVERSAO_RENDA)
   E (mov.codigo IN {11390, 11391, 11392, 11393, 7087}
      OU complemento_indica_fazenda(mov))
ENTÃO fase = 14
```

---

### 4.4 Fase 11 — Execução Suspensa

**Prioridade:** 4 (para classes de execução)

**Descrição:** Execução com tramitação suspensa — embargos recebidos com efeito suspensivo, Art. 40 LEF, impugnação total.

#### Critérios de Identificação

| Critério | Condição |
|----------|----------|
| Classe | `classe ∈ CLASSES_EXECUCAO` |
| Movimento | `EXISTS(movimento ∈ MOVIMENTOS_SUSPENSAO_EXECUCAO)` |
| Condição | `NOT EXISTS(levantamento POSTERIOR)` |

#### Códigos CNJ — Movimentos de Suspensão de Execução

| Código | Descrição | Motivo |
|--------|-----------|--------|
| 861 | Suspensão da Execução | Genérico |
| 898 | Suspenso por Decisão Judicial | Genérico |
| 11372 | Suspensão — Art. 40 LEF | Sem bens |
| 11373 | Suspensão — Art. 921 CPC | Sem bens |
| 11374 | Suspensão — Embargos com Efeito Suspensivo | Defesa |
| 11375 | Suspensão — Impugnação Recebida | Defesa |
| 12167 | Arquivamento Provisório — Art. 40 LEF | Prescrição |
| 12168 | Arquivamento Provisório — Não Localização | Prescrição |

#### Códigos CNJ — Movimentos de Levantamento

| Código | Descrição |
|--------|-----------|
| 899 | Levantamento de Suspensão |
| 900 | Desarquivamento |
| 11376 | Levantamento — Bens Localizados |
| 11377 | Levantamento — Embargos Rejeitados |
| 11378 | Levantamento — Pagamento |
| 12617 | Desarquivamento Provisório |

#### Regra Lógica

```
SE classe ∈ EXECUÇÃO
   E EXISTS(mov_suspensao ∈ MOVIMENTOS_SUSPENSAO_EXECUCAO)
   E NOT EXISTS(mov_levantamento.data_hora > mov_suspensao.data_hora)
ENTÃO fase = 11
```

---

### 4.5 Fase 12 — Execução Suspensa Parcialmente

**Prioridade:** 4 (alternativa à Fase 11)

**Descrição:** Execução com impugnação/embargos parciais — parte do crédito em discussão, parte em execução normal.

#### Critérios de Identificação

| Critério | Condição |
|----------|----------|
| Classe | `classe ∈ CLASSES_EXECUCAO` |
| Movimento | `EXISTS(movimento_impugnacao_parcial)` |
| Complemento | Análise textual indica parcialidade |

#### Análise de Complemento

```python
INDICADORES_PARCIALIDADE = [
    "parcial", "parte", "apenas", "somente",
    "exceto", "salvo", "montante de", "valor de",
    "período de", "competências", "parcelas"
]

def verificar_suspensao_parcial(movimento):
    complemento = (movimento.complemento or "").lower()
    return any(ind in complemento for ind in INDICADORES_PARCIALIDADE)
```

#### Regra Lógica

```
SE classe ∈ EXECUÇÃO
   E EXISTS(mov_suspensao)
   E complemento_indica_parcialidade(mov_suspensao)
   E NOT suspensao_total
ENTÃO fase = 12
```

---

### 4.6 Fase 10 — Execução

**Prioridade:** 5 (para classes executivas não suspensas)

**Descrição:** Processo em fase de execução ou cumprimento de sentença, em tramitação normal.

#### Critérios de Identificação

| Critério | Condição |
|----------|----------|
| Classe | `classe ∈ CLASSES_EXECUCAO` |
| Condição | `NOT EXISTS(suspensao_ativa)` |
| Condição | `NOT EXISTS(baixa_definitiva)` |

#### Regra Lógica

```
SE classe ∈ EXECUÇÃO
   E NOT fase_11
   E NOT fase_12
   E NOT fase_14
   E NOT fase_15
ENTÃO fase = 10
```

---

### 4.7 Fases de Conhecimento (01-09)

#### 4.7.1 Fase 01 — Conhecimento: Antes da Sentença

**Descrição:** Processo de conhecimento em 1ª instância sem sentença proferida.

| Critério | Condição |
|----------|----------|
| Classe | `classe ∈ CONHECIMENTO` |
| Grau | `grau = G1` |
| Movimento | `NOT EXISTS(movimento ∈ MOVIMENTOS_SENTENCA)` |

#### Códigos CNJ — Movimentos de Sentença

| Código | Descrição |
|--------|-----------|
| 193 | Julgamento (hierarquia) |
| 198 | Julgado Procedente o Pedido |
| 200 | Julgado Improcedente o Pedido |
| 219 | Extinto o Processo com Resolução do Mérito |
| 220 | Extinto o Processo sem Resolução do Mérito |
| 235 | Julgado Procedente em Parte o Pedido |
| 236 | Homologação de Acordo |
| 246 | Proferida Sentença |
| 388 | Sentença Condenatória |
| 389 | Sentença Absolutória |
| 455 | Sentença ou Acórdão não Condenatório |

#### Regra Lógica

```
SE classe ∈ CONHECIMENTO
   E grau = G1
   E NOT EXISTS(mov ∈ MOVIMENTOS_SENTENCA com grau = G1)
ENTÃO fase = 01
```

---

#### 4.7.2 Fase 02 — Conhecimento: Sentença sem Trânsito

**Descrição:** Processo com sentença proferida em 1ª instância, aguardando prazo recursal.

| Critério | Condição |
|----------|----------|
| Classe | `classe ∈ CONHECIMENTO` |
| Grau | `grau = G1` |
| Movimento | `EXISTS(sentença em G1)` |
| Condição | `NOT EXISTS(trânsito em julgado)` |
| Condição | `NOT EXISTS(remessa a tribunal)` |

#### Códigos CNJ — Movimentos de Remessa

| Código | Descrição |
|--------|-----------|
| 22881 | Remetidos os Autos |
| 123 | Redistribuído para Órgão Julgador |
| 970 | Remetidos os Autos para Tribunal |
| 132 | Recebido no Tribunal |
| 60303 | Remessa a Tribunal |

#### Regra Lógica

```
SE classe ∈ CONHECIMENTO
   E EXISTS(sentença em G1)
   E NOT EXISTS(848 - Trânsito em Julgado)
   E NOT EXISTS(remessa_efetiva para G2)
ENTÃO fase = 02
```

---

#### 4.7.3 Fase 03 — Conhecimento: Sentença com Trânsito

**Descrição:** Processo de conhecimento em 1ª instância com sentença transitada em julgado.

| Critério | Condição |
|----------|----------|
| Movimento | `EXISTS(848 - Trânsito em Julgado)` |
| Grau | `último_grau_julgamento = G1` |
| Condição | `NOT mudou_para_execução` |

#### Código CNJ — Trânsito em Julgado

| Código | Descrição |
|--------|-----------|
| 848 | Trânsito em Julgado |

#### Regra Lógica

```
SE EXISTS(848 - Trânsito em Julgado)
   E último_grau_julgamento = G1
   E NOT classe_atual ∈ EXECUÇÃO
ENTÃO fase = 03
```

---

#### 4.7.4 Fase 04 — Recurso 2ª Instância: Pendente

**Descrição:** Recurso em tramitação no Tribunal de Justiça, aguardando julgamento.

| Critério | Condição |
|----------|----------|
| Grau | `grau_atual = G2` |
| Movimento | `EXISTS(remessa para G2)` |
| Condição | `NOT EXISTS(acórdão em G2)` |

#### Códigos CNJ — Movimentos de Acórdão

| Código | Descrição |
|--------|-----------|
| 50 | Proferido Acórdão |
| 942 | Julgado Agravo de Instrumento |
| 943 | Julgada Apelação |
| 12198 | Acórdão Publicado |

#### Regra Lógica

```
SE grau_atual = G2
   E EXISTS(remessa_efetiva para G2)
   E NOT EXISTS(acórdão em G2)
ENTÃO fase = 04
```

---

#### 4.7.5 Fase 05 — Recurso 2ª Instância: Julgado sem Trânsito

**Descrição:** Acórdão proferido pelo Tribunal, aguardando prazo para recursos.

| Critério | Condição |
|----------|----------|
| Grau | `grau_atual = G2` |
| Movimento | `EXISTS(acórdão em G2)` |
| Condição | `NOT EXISTS(trânsito em julgado)` |
| Condição | `NOT EXISTS(remessa para SUP)` |

#### Regra Lógica

```
SE grau_atual = G2
   E EXISTS(acórdão em G2)
   E NOT EXISTS(848 - Trânsito em Julgado)
   E NOT EXISTS(remessa_efetiva para SUP)
ENTÃO fase = 05
```

---

#### 4.7.6 Fase 06 — Recurso 2ª Instância: Transitado

**Descrição:** Acórdão do Tribunal com certificação de trânsito em julgado.

| Critério | Condição |
|----------|----------|
| Movimento | `EXISTS(acórdão em G2)` |
| Movimento | `EXISTS(848 - Trânsito em Julgado)` |
| Condição | `último_grau_julgamento = G2` |

#### Regra Lógica

```
SE EXISTS(acórdão em G2)
   E EXISTS(848 - Trânsito em Julgado)
   E último_grau_julgamento = G2
   E NOT EXISTS(remessa para SUP)
ENTÃO fase = 06
```

---

#### 4.7.7 Fase 07 — Recurso Tribunais Superiores: Pendente

**Descrição:** Recurso Especial (STJ) ou Extraordinário (STF) em tramitação.

| Critério | Condição |
|----------|----------|
| Grau | `grau_atual = SUP` |
| Movimento | `EXISTS(remessa para SUP)` |
| Condição | `NOT EXISTS(julgamento em SUP)` |

#### Códigos CNJ — Movimentos de Decisão Monocrática

| Código | Descrição |
|--------|-----------|
| 940 | Proferida Decisão Monocrática |
| 941 | Negado Seguimento ao Recurso |
| 12197 | Decisão Monocrática — Provimento |
| 12196 | Decisão Monocrática — Não Conhecimento |

#### Regra Lógica

```
SE grau_atual = SUP
   E EXISTS(remessa_efetiva para SUP)
   E NOT EXISTS(julgamento em SUP)
ENTÃO fase = 07
```

---

#### 4.7.8 Fase 08 — Recurso Tribunais Superiores: Julgado sem Trânsito

**Descrição:** Recurso julgado pelo STJ ou STF, aguardando prazo.

| Critério | Condição |
|----------|----------|
| Grau | `grau_atual = SUP` |
| Movimento | `EXISTS(julgamento em SUP)` |
| Condição | `NOT EXISTS(trânsito em julgado)` |

#### Regra Lógica

```
SE grau_atual = SUP
   E EXISTS(julgamento em SUP)
   E NOT EXISTS(848 - Trânsito em Julgado)
ENTÃO fase = 08
```

---

#### 4.7.9 Fase 09 — Recurso Tribunais Superiores: Transitado

**Descrição:** Recurso em Tribunal Superior com trânsito em julgado.

| Critério | Condição |
|----------|----------|
| Movimento | `EXISTS(julgamento em SUP)` |
| Movimento | `EXISTS(848 - Trânsito em Julgado)` |
| Condição | `último_grau_julgamento = SUP` |

#### Regra Lógica

```
SE EXISTS(julgamento em SUP)
   E EXISTS(848 - Trânsito em Julgado)
   E último_grau_julgamento = SUP
ENTÃO fase = 09
```

---

## 5. Tabelas Consolidadas de Códigos CNJ

### 5.1 Movimentos por Fase

| Fase | Códigos Principais | Finalidade |
|------|-------------------|------------|
| 01 | 26, 123, 85, 25 | Distribuição, Citação, Petições |
| 02 | 193, 198, 200, 219, 220, 235, 246 | Sentenças |
| 03 | 848 | Trânsito em Julgado |
| 04 | 970, 22881, 132 | Remessa a Tribunal |
| 05 | 50, 942, 943 | Acórdãos |
| 06 | 848 + Acórdão em G2 | Trânsito em 2ª Instância |
| 07 | 970, 132 (para STJ/STF) | Remessa a Tribunais Superiores |
| 08 | 50, 940, 941 (em SUP) | Julgamentos em SUP |
| 09 | 848 + Julgamento em SUP | Trânsito em SUP |
| 10 | Classes 1116, 156, 159, etc. | Execução em Tramitação |
| 11 | 861, 898, 11372-11375, 12167-12168 | Suspensão de Execução |
| 12 | Suspensão + Complemento "parcial" | Suspensão Parcial |
| 13 | 265, 893, 898, 12099, 12100, 12155 | Sobrestamento |
| 14 | 11390-11393, 7087, 60700-60702 | Conversão em Renda |
| 15 | 22, 246, 861, 865, 10965-10967 | Baixa Definitiva |

### 5.2 Documentos Relevantes

| Código | Documento | Fase Relacionada |
|--------|-----------|-----------------|
| 60 | Petição Inicial | 01 |
| 50 | Contestação | 01 |
| 80 | Sentença | 02, 03 |
| 81 | Acórdão | 05, 06, 08, 09 |
| 7 | Apelação | 04 |
| 5 | Agravo de Instrumento | 04 |
| 67 | Recurso Especial | 07 |
| 66 | Recurso Extraordinário | 07 |
| 56 | Embargos à Execução | 11 |
| 59 | Impugnação ao Cumprimento | 11, 12 |
| 1290 | Exceção de Pré-Executividade | 11 |

---

## 6. Algoritmo de Classificação

### 6.1 Pseudocódigo Principal

```python
FUNÇÃO classificar_fase(processo):
    
    # ═══════════════════════════════════════════════════════════════════
    # PRIORIDADE 1: Arquivamento Definitivo
    # ═══════════════════════════════════════════════════════════════════
    SE processo.situacao IN {'BAIXADO', 'ARQUIVADO', 'ARQUIVADO DEFINITIVAMENTE'}:
        RETORNAR Fase_15, confiança=0.95
    
    SE existe_movimento(processo, MOVIMENTOS_BAIXA_DEFINITIVA):
        RETORNAR Fase_15, confiança=0.92
    
    # ═══════════════════════════════════════════════════════════════════
    # PRIORIDADE 2: Sobrestamento Genérico
    # ═══════════════════════════════════════════════════════════════════
    SE existe_sobrestamento_ativo(processo):
        SE NOT processo.classe IN CLASSES_EXECUCAO:
            RETORNAR Fase_13, confiança=0.90
    
    # ═══════════════════════════════════════════════════════════════════
    # PRIORIDADE 3: Classes de Execução
    # ═══════════════════════════════════════════════════════════════════
    SE processo.classe IN CLASSES_EXECUCAO:
        RETORNAR classificar_fase_execucao(processo)
    
    # ═══════════════════════════════════════════════════════════════════
    # PRIORIDADE 4: Classes de Conhecimento
    # ═══════════════════════════════════════════════════════════════════
    grau = identificar_grau_atual(processo)
    RETORNAR classificar_fase_conhecimento(processo, grau)


FUNÇÃO classificar_fase_execucao(processo):
    
    # Verificar Conversão em Renda (Fase 14)
    SE processo.polo_fazenda = 'AU':
        SE existe_conversao_renda(processo):
            RETORNAR Fase_14, confiança=0.85
    
    # Verificar Suspensão (Fases 11/12)
    suspensao = verificar_suspensao_execucao(processo)
    SE suspensao.ativa:
        SE suspensao.parcial:
            RETORNAR Fase_12, confiança=0.80
        SENÃO:
            RETORNAR Fase_11, confiança=0.85
    
    # Execução em tramitação normal
    RETORNAR Fase_10, confiança=0.85


FUNÇÃO classificar_fase_conhecimento(processo, grau):
    
    tem_transito = existe_movimento(processo, {848})
    tem_sentenca_g1 = existe_sentenca_em_grau(processo, G1)
    tem_acordao_g2 = existe_acordao_em_grau(processo, G2)
    tem_julgamento_sup = existe_julgamento_em_grau(processo, SUP)
    tem_remessa_g2 = verificar_remessa_efetiva(processo, G2)
    tem_remessa_sup = verificar_remessa_efetiva(processo, SUP)
    
    # ─────────────────────────────────────────────────────────────────
    # Tribunais Superiores (STJ, STF)
    # ─────────────────────────────────────────────────────────────────
    SE grau = SUP OU tem_remessa_sup:
        SE tem_transito E tem_julgamento_sup:
            RETORNAR Fase_09, confiança=0.92
        SE tem_julgamento_sup:
            RETORNAR Fase_08, confiança=0.88
        SE tem_remessa_sup:
            RETORNAR Fase_07, confiança=0.85
    
    # ─────────────────────────────────────────────────────────────────
    # Segunda Instância (TJ, TRF)
    # ─────────────────────────────────────────────────────────────────
    SE grau = G2 OU tem_remessa_g2:
        SE tem_transito E tem_acordao_g2:
            RETORNAR Fase_06, confiança=0.92
        SE tem_acordao_g2:
            RETORNAR Fase_05, confiança=0.88
        SE tem_remessa_g2:
            RETORNAR Fase_04, confiança=0.85
    
    # ─────────────────────────────────────────────────────────────────
    # Primeira Instância
    # ─────────────────────────────────────────────────────────────────
    SE tem_transito E tem_sentenca_g1:
        RETORNAR Fase_03, confiança=0.90
    
    SE tem_sentenca_g1:
        RETORNAR Fase_02, confiança=0.88
    
    RETORNAR Fase_01, confiança=0.85


FUNÇÃO verificar_remessa_efetiva(processo, grau_destino):
    """
    Verifica se houve remessa efetiva para o grau de destino,
    sem retorno posterior.
    """
    movimentos_remessa = filtrar_movimentos(processo, MOVIMENTOS_REMESSA)
    movimentos_retorno = filtrar_movimentos(processo, MOVIMENTOS_RETORNO)
    
    ultima_remessa = None
    PARA mov IN movimentos_remessa ORDENADOS POR data_hora DESC:
        SE mov.grau_destino = grau_destino:
            ultima_remessa = mov
            PARAR
    
    SE ultima_remessa = None:
        RETORNAR False
    
    # Verificar se há retorno posterior
    PARA mov IN movimentos_retorno:
        SE mov.data_hora > ultima_remessa.data_hora:
            RETORNAR False
    
    RETORNAR True
```

### 6.2 Fluxograma de Decisão

```
                              ┌─────────────────┐
                              │ INÍCIO          │
                              │ Receber Processo│
                              └────────┬────────┘
                                       │
                                       ▼
                         ┌─────────────────────────┐
                         │ Situação = BAIXADO?     │
                         └────────────┬────────────┘
                                      │
                            ┌─────────┴─────────┐
                            │                   │
                           SIM                 NÃO
                            │                   │
                            ▼                   ▼
                     ┌──────────┐    ┌─────────────────────┐
                     │ FASE 15  │    │ Movimento Baixa?    │
                     │ Arquivado│    └──────────┬──────────┘
                     └──────────┘               │
                                      ┌────────┴────────┐
                                     SIM               NÃO
                                      │                 │
                                      ▼                 ▼
                               ┌──────────┐  ┌─────────────────────┐
                               │ FASE 15  │  │ Sobrestamento Ativo?│
                               └──────────┘  └──────────┬──────────┘
                                                        │
                                              ┌────────┴────────┐
                                             SIM               NÃO
                                              │                 │
                                              ▼                 ▼
                                       ┌──────────┐  ┌─────────────────────┐
                                       │ FASE 13  │  │ Classe = Execução?  │
                                       │Sobrestado│  └──────────┬──────────┘
                                       └──────────┘             │
                                                      ┌────────┴────────┐
                                                     SIM               NÃO
                                                      │                 │
                                                      ▼                 ▼
                                         ┌────────────────┐   ┌────────────────┐
                                         │ Classificar    │   │ Classificar    │
                                         │ Fase Execução  │   │ Fase Conhecim. │
                                         │ (10, 11, 12,14)│   │ (01-09)        │
                                         └────────────────┘   └────────────────┘
```

---

## 7. Integração com MNI/DEJT

### 7.1 Modelo Nacional de Interoperabilidade

O sistema consome dados estruturados conforme a Resolução CNJ 455/2022.

#### Estrutura de Dados MNI

```json
{
  "numero": "0000000-00.0000.8.19.0001",
  "classeProcessual": {
    "codigo": 1116,
    "descricao": "Execução Fiscal"
  },
  "orgaoJulgador": {
    "codigo": "8.19.0042",
    "descricao": "3ª Vara de Execução Fiscal"
  },
  "poloAtivo": [...],
  "poloPassivo": [...],
  "movimentos": [
    {
      "codigo": 26,
      "descricao": "Distribuído",
      "dataHora": "2024-01-15T10:30:00",
      "complementos": [...]
    }
  ],
  "documentos": [...]
}
```

### 7.2 Conversão de Dados

```python
def converter_processo_mni(dados_mni: dict) -> Processo:
    """Converte dados MNI para estrutura interna."""
    
    return Processo(
        numero=dados_mni["numero"],
        classe_codigo=dados_mni["classeProcessual"]["codigo"],
        classe_descricao=dados_mni["classeProcessual"]["descricao"],
        codigo_orgao=dados_mni.get("orgaoJulgador", {}).get("codigo"),
        polo_fazenda=identificar_polo_fazenda(dados_mni),
        situacao=dados_mni.get("situacao", "MOVIMENTO"),
        movimentos=[
            converter_movimento(m) for m in dados_mni.get("movimentos", [])
        ],
        documentos=[
            converter_documento(d) for d in dados_mni.get("documentos", [])
        ]
    )
```

---

## 8. Exemplos de Classificação

### 8.1 Exemplo: Execução Fiscal em Tramitação

**Entrada:**
```json
{
  "numero": "0001234-56.2024.8.19.0042",
  "classeProcessual": {"codigo": 1116, "descricao": "Execução Fiscal"},
  "situacao": "MOVIMENTO",
  "movimentos": [
    {"codigo": 26, "descricao": "Distribuído", "dataHora": "2024-01-15"},
    {"codigo": 14, "descricao": "Expedição de Mandado", "dataHora": "2024-02-01"},
    {"codigo": 981, "descricao": "Mandado Devolvido - Citado", "dataHora": "2024-03-01"}
  ]
}
```

**Resultado:**
```
Fase: 10 (Execução)
Confiança: 85%
Justificativa: Classe de execução (1116) em tramitação normal, sem suspensão
```

### 8.2 Exemplo: Processo Sobrestado por Repetitivo

**Entrada:**
```json
{
  "numero": "0005678-90.2023.8.19.0001",
  "classeProcessual": {"codigo": 7, "descricao": "Procedimento Comum"},
  "situacao": "SUSPENSO",
  "movimentos": [
    {"codigo": 26, "descricao": "Distribuído", "dataHora": "2023-06-01"},
    {"codigo": 12099, "descricao": "Sobrestado - Recurso Repetitivo", 
     "dataHora": "2023-08-15", "complemento": "Tema 1234 STJ"}
  ]
}
```

**Resultado:**
```
Fase: 13 (Suspenso/Sobrestado)
Confiança: 90%
Justificativa: Movimento 12099 (Recurso Repetitivo) sem levantamento posterior
```

### 8.3 Exemplo: Conhecimento com Sentença Transitada

**Entrada:**
```json
{
  "numero": "0009999-00.2022.8.19.0001",
  "classeProcessual": {"codigo": 7, "descricao": "Procedimento Comum"},
  "situacao": "MOVIMENTO",
  "movimentos": [
    {"codigo": 26, "descricao": "Distribuído", "dataHora": "2022-01-10"},
    {"codigo": 246, "descricao": "Proferida Sentença", "dataHora": "2023-06-01"},
    {"codigo": 848, "descricao": "Trânsito em Julgado", "dataHora": "2023-08-01"}
  ]
}
```

**Resultado:**
```
Fase: 03 (Conhecimento - Sentença com Trânsito em Julgado)
Confiança: 90%
Justificativa: Movimento 848 (Trânsito) presente, último julgamento em G1
```

---

## 9. Glossário e Referências

### 9.1 Glossário

| Termo | Definição |
|-------|-----------|
| **CNJ** | Conselho Nacional de Justiça |
| **MNI** | Modelo Nacional de Interoperabilidade |
| **TPU** | Tabela Processual Unificada |
| **LEF** | Lei de Execuções Fiscais (Lei 6.830/1980) |
| **CPC** | Código de Processo Civil (Lei 13.105/2015) |
| **G1** | Primeira Instância |
| **G2** | Segunda Instância (Tribunais de Justiça/Regionais) |
| **SUP** | Tribunais Superiores (STF, STJ, TST) |
| **IRDR** | Incidente de Resolução de Demandas Repetitivas |
| **IAC** | Incidente de Assunção de Competência |
| **RG** | Repercussão Geral |

### 9.2 Referências Normativas

1. Resolução CNJ nº 46/2007 — Tabelas Processuais Unificadas
2. Resolução CNJ nº 326/2020 — Atualização das TPUs
3. Resolução CNJ nº 455/2022 — Modelo Nacional de Interoperabilidade
4. Lei nº 6.830/1980 — Lei de Execuções Fiscais
5. Lei nº 13.105/2015 — Código de Processo Civil
6. Lei nº 5.172/1966 — Código Tributário Nacional

### 9.3 Histórico de Versões

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 | Fev/2026 | Versão inicial |
| 2.0 | Fev/2026 | Expansão de códigos CNJ, algoritmo completo, integração MNI |

---

**Elaborado por:** Coordenação de Tecnologia — PGM-Rio  
**Versão:** 2.0  
**Data:** Fevereiro de 2026
