# Taxonomia de Peças — Peça × Autor × Grau → Fase

Base de mapeamento para classificação de fase a partir da árvore documental.
Fonte normativa: CPC/2015, LEF (Lei 6.830/80), Tabela Processual Unificada CNJ (tipos de documento).

## 1. Tabela principal (peça determinante → fase)

| Peça (tipo normalizado) | Títulos típicos (fuzzy) | Autor | Grau | Fase indicada |
|---|---|---|---|---|
| `peticao_inicial` | petição inicial, exordial, inicial | parte | G1 | 01 |
| `citacao` | mandado de citação, AR de citação, carta de citação | serventia | G1 | 01 |
| `contestacao` | contestação, defesa, resposta do réu | parte | G1 | 01 |
| `replica` | réplica, manifestação sobre contestação | parte | G1 | 01 |
| `saneador` | decisão de saneamento, despacho saneador | juizo_1grau | G1 | 01 |
| `pericia` | laudo pericial, quesitos, esclarecimentos do perito | terceiro | G1 | 01 |
| `audiencia` | ata/termo de audiência (instrução, conciliação) | juizo_1grau | G1 | 01 |
| `alegacoes_finais` | alegações finais, memoriais | parte | G1 | 01 |
| `sentenca` | sentença (mérito ou terminativa: procedência, improcedência, extinção sem mérito, homologatória) | juizo_1grau | G1 | 02 (sem certidão de trânsito posterior) |
| `embargos_declaracao` | embargos de declaração | parte | G1/G2/SUP | mantém a fase do julgado embargado (02/05/08); não é recurso de devolução ampla |
| `certidao_transito_g1` | certidão de trânsito em julgado (1º grau), certidão de decurso de prazo recursal + trânsito | serventia | G1 | 03 |
| `apelacao` | apelação, razões de apelação | parte | G2 | 04 |
| `remessa_necessaria` | remessa necessária, reexame necessário, duplo grau obrigatório (art. 496 CPC) | serventia / juizo_1grau | G2 | 04 + flag `remessa_necessaria` (F-03) |
| `agravo_instrumento` | agravo de instrumento (art. 1.015 CPC) | parte | G2 | **não altera a fase-base** — incidente contra interlocutória (regras §3) |
| `decisao_parcial_merito` | julgamento antecipado parcial do mérito (art. 356 CPC) | juizo_1grau | G1 | fase do capítulo pendente + `transito_parcial` quando certificado (F-02) |
| `retratacao` | juízo de retratação, adequação ao paradigma (arts. 1.030 II / 1.040 II CPC) | juizo_1grau / tribunal_2grau | G1/G2 | 02/04 — reativação do julgamento no órgão de origem (F-04) |
| `desistencia_inadmissao` | homologação de desistência de recurso, decisão de inadmissão/não conhecimento, certidão de decurso de prazo | tribunal / serventia | — | conduz ao trânsito do último julgado (F-12) |
| `contrarrazoes` | contrarrazões de apelação/recurso | parte | G2 | 04 |
| `distribuicao_g2` | termo de distribuição no tribunal, conclusão ao relator | serventia | G2 | 04 |
| `acordao_g2` | acórdão, voto, ementa (TJ/TRF) | tribunal_2grau | G2 | 05 (sem certidão de trânsito posterior) |
| `certidao_transito_g2` | certidão de trânsito em julgado (pós-acórdão G2) | serventia | G2 | 06 |
| `resp_re` | recurso especial, recurso extraordinário, AREsp, agravo em REsp/RE | parte | SUP | 07 |
| `juizo_admissibilidade` | decisão de admissibilidade de REsp/RE (vice-presidência) | tribunal_2grau | SUP | 07 |
| `acordao_sup` | acórdão/decisão monocrática STJ/STF | tribunal_superior | SUP | 08 (sem certidão de trânsito posterior) |
| `certidao_transito_sup` | certidão de trânsito em julgado (pós-STJ/STF) | serventia | SUP | 09 |
| `inicio_cumprimento` | petição de cumprimento de sentença (art. 523 CPC), petição inicial de execução, CDA + inicial de execução fiscal | parte | — | 10 |
| `atos_constritivos` | mandado de penhora, auto de penhora, termo de penhora, arresto, Sisbajud/BacenJud, Renajud, avaliação, edital de leilão, arrematação, adjudicação | serventia / juizo_1grau | — | 10 |
| `impugnacao_embargos_exec` | impugnação ao cumprimento (art. 525), embargos à execução (art. 914 / LEF art. 16), exceção de pré-executividade | parte | — | 10 (efeito suspensivo total → 11; parcial → 12) |
| `suspensao_execucao` | decisão de suspensão da execução (art. 921 CPC; art. 40 LEF), arquivamento provisório, homologação de parcelamento (art. 151 VI CTN; art. 922 CPC) | juizo_1grau | — | 11 |
| `precatorio_rpv` | ofício requisitório, expedição de precatório ou RPV (art. 535 §3º CPC), comprovante de depósito requisitório | serventia / juizo_1grau | — | 10; pagamento + extinção → 15, **nunca** 14 (F-09) |
| `suspensao_parcial` | decisão de suspensão parcial (impugnação parcial com efeito suspensivo; garantia parcial) | juizo_1grau | — | 12 |
| `sobrestamento` | decisão de sobrestamento (Tema repetitivo, repercussão geral, IRDR, IAC, SIRDR, suspensão por controvérsia, art. 313 CPC, art. 921 III fora da execução) | juizo_1grau / tribunal | — | 13 |
| `retomada` | decisão de dessobrestamento, levantamento da suspensão, revogação da suspensão, desarquivamento com prosseguimento, determinação de aplicação do paradigma | juizo_1grau / tribunal / serventia | — | encerra 11/12/13 → devolve à fase subjacente ou a 10 (F-06) |
| `deposito_judicial` | guia/comprovante de depósito judicial, abertura de conta judicial, caução em dinheiro | parte / serventia | — | não determina fase por si; ativa a trava financeira do 15 se sem destinação posterior (F-13) |
| `certidao_saldo` | certidão de inexistência de saldo em conta judicial, certidão de encerramento de conta | serventia | — | habilita 15 quando conjugada à extinção definitiva |
| `conversao_renda` | termo/decisão de conversão de depósito em renda, alvará/guia de levantamento em favor do Município, sentença de extinção pela satisfação (art. 924, II CPC) com arrecadação | juizo_1grau | — | 14 |
| `extincao_definitiva` | sentença de extinção definitiva da execução sem arrecadação (prescrição intercorrente, cancelamento de CDA, pagamento administrativo), certidão de baixa definitiva, termo de arquivamento definitivo | juizo_1grau / serventia | — | 15 |

**Nota — certidões de trânsito**: quando o título não permitir identificar o grau,
normalizar como `certidao_transito` genérica e resolver o grau pelo contexto (posição
na árvore e último julgado anterior); irresoluto → grau do último julgado, com
`campos_inferidos` e redução de 0.10 na confiança.

## 2. Regras de inferência de `autor` e `grau` (quando ausentes)

| Sinal no título | Inferência |
|---|---|
| "certidão", "termo", "juntada", "mandado", "AR", "edital" | autor = serventia |
| "sentença", "decisão" (sem menção a tribunal) | autor = juizo_1grau, grau = G1 |
| "acórdão", "voto", "ementa", "relator", "câmara", "turma" | autor = tribunal_2grau, grau = G2 |
| "STJ", "STF", "ministro", "recurso especial", "extraordinário" | grau = SUP; se decisório, autor = tribunal_superior |
| "petição", "razões", "contrarrazões", "manifestação", "embargos" | autor = parte |
| "laudo", "parecer técnico", "ofício de terceiro" | autor = terceiro |

Registrar toda inferência em `flags.campos_inferidos` (lista de `{ordem, campo, valor_inferido}`).

## 3. Peças NÃO determinantes (ruído)

Ignorar para fins de classificação por metadado (mas manter na análise de contexto):
qualquer documento batizado exatamente como "Despacho"; despachos de mero expediente
("intime-se", "cumpra-se", "dê-se vista"); certidões de publicação, guias de custas,
procurações, substabelecimentos, ofícios de comunicação, juntadas genéricas, petições
de habilitação de advogado, pedidos de vista/carga. Documento batizado de "Despacho"
só pode ser aproveitado no fallback por teor se o conteúdo efetivo trouxer ato
inequívoco decisório/certificatório/satisfativo (RE-12).

## 4. Mapeamento fuzzy título→tipo

Procedimento quando o título da peça não corresponde a nenhum tipo da tabela:

1. Normalizar: minúsculas, sem acentos, remover números de sequência e datas do título.
2. Buscar radical/expressão-chave conforme colunas "Títulos típicos" acima (matching por
   substring e sinônimos regionais TJRJ: "assentada" = ata de audiência; "conclusos" =
   conclusão; "BDA/baixa definitiva" = baixa).
3. Ambiguidade entre 2 tipos → escolher o de menor impacto de fase (o que NÃO promove
   mudança de domínio) e reduzir a confiança em 0.10.
4. Irresoluto → tratar como peça não determinante; se a peça irresoluta for a mais recente
   e potencialmente decisória (contém "sentença", "decisão", "acórdão", "certidão"),
   abster-se (16), salvo fallback de teor bem-sucedido nos termos da RE-12.
5. O termo isolado "despacho" não é expressão-chave apta a classificar fase.

## 5. Polaridade financeira — requisito da fase 14

Peças de movimentação financeira são **neutras** até prova da polaridade (a quem o
valor se destina). Tipo normalizado: `destinacao_financeira` (mandado de pagamento,
alvará, ordem de levantamento, transferência, resgate). A fase 14 exige polaridade
positiva ao ente credor.

| Polaridade | Sinais | Efeito |
|---|---|---|
| **Positiva** (→ conta para 14) | "em favor do Município/MRJ", "Fazenda credora", DAM de conversão, "resgate MRJ", "conversão em renda", "satisfação do crédito fiscal" | peça satisfativa (F-07) |
| **Indeterminada** | "mandado de pagamento", "alvará", "levantamento", "transferência", "resgate", sem beneficiário identificável | NÃO conta para 14; conta para a trava financeira do 15 (F-13); se decisiva e irresoluta → 16 |
| **Negativa** | precatório/RPV pago pelo ente, levantamento em favor da parte adversa, honorários da parte contrária, devolução de caução/depósito ao particular | jamais 14 (F-09); satisfação contra o ente → 15 quando extinta |

## 6. Vocabulário PAV e dos autos eletrônicos

Dicionário empírico mantido em arquivo próprio, expansível a cada lote validado:
ver [`vocabulario-pav.md`](vocabulario-pav.md). Aplicá-lo como camada determinística
ANTES do matching fuzzy da seção 4.
