# Casos de Fronteira — Matriz Decisória F-01 a F-12

Hipóteses em que sinais documentais de mais de uma fase coexistem na árvore. Cada
fronteira indica: sinais típicos na árvore, regra de resolução, fase resultante,
flags e teto de confiança quando aplicável.

## F-01 — Cumprimento provisório × fase recursal (10 × 04/05/07/08)

**Sinais**: petição de cumprimento provisório (art. 520 CPC), caução, atos
constritivos, coexistindo com apelação/REsp/RE pendente ou acórdão sem trânsito.
**Resolução**: a posição recursal do mérito **domina**. A fase permanece recursal
(04/05/07/08) e o cumprimento provisório é registrado como
`flags.execucao_provisoria = true`.
**Fundamento**: sem trânsito do mérito não há domínio de execução (RE-01); o
cumprimento provisório é efeito da eficácia imediata, não mudança de fase.

## F-02 — Trânsito parcial por capítulos (art. 356 e 1.013 CPC)

**Sinais**: certidão de trânsito **parcial**, decisão parcial de mérito (art. 356),
recurso que impugna apenas capítulo(s) da sentença, cumprimento **definitivo** de
capítulo incontroverso concomitante a recurso pendente sobre outro capítulo.
**Resolução**: a fase segue a posição recursal do capítulo **pendente**
(04/05/07/08); o cumprimento definitivo do capítulo transitado registra-se como
`flags.execucao_definitiva_parcial = true` e `flags.transito_parcial = true`.
**Observação**: se TODOS os capítulos transitaram e o que resta é só execução →
domínio de execução (10).

## F-03 — Remessa necessária (art. 496 CPC) — essencial para a Fazenda

**Sinais**: sentença contra a Fazenda Pública; peças "remessa necessária", "reexame
necessário", "subida dos autos ao tribunal" **sem** petição de apelação da parte.
**Resolução**: a remessa necessária equivale, para fins de fase, a recurso pendente
de julgamento em 2ª instância → **04**, com `flags.remessa_necessaria = true` —
**desde que exista peça de remessa na árvore**. Sentença contra a Fazenda SEM peça
de remessa e sem apelação → permanece **02** (não presumir a remessa: as dispensas
do art. 496, §§ 3º e 4º, são invisíveis ao metadado). Julgada a remessa (acórdão)
sem trânsito → 05; com certidão → 06.
**Cautela**: a sentença contra a Fazenda sujeita a reexame **não transita** sem a
confirmação pelo tribunal (Súmula 423/STF); é vedado inferir trânsito (RE-05) na
presença de sinais de sujeição ao art. 496 sem peça que ateste dispensa (§§ 3º e 4º).

## F-04 — Juízo de retratação e devolução ao órgão de origem (arts. 1.030, II; 1.040, II, CPC)

**Sinais**: decisão de devolução ao órgão de origem para retratação após julgamento
de repetitivo/repercussão geral; "juízo de retratação"; "adequação ao paradigma".
**Resolução**: a devolução **reativa** o julgamento no grau de origem → **04**
(novo julgamento pendente em G2) ou 02 (se a retratação couber ao juízo de 1º grau).
Realizada a retratação/mantida a decisão (novo acórdão) → 05, reabrindo o ciclo.
**Nota**: não confundir com o sobrestamento que a antecede (F-06).

## F-05 — Suspensão da execução: total × parcial × extinção (11 × 12 × 15)

**Sinais e resolução**:
- Suspensão do art. 921 CPC ou do art. 40, caput/§2º, LEF (não localização do
  devedor/bens; arquivamento provisório sem baixa) → **11**.
- Parcelamento do crédito (art. 151, VI, CTN; art. 922 CPC) → **11** enquanto
  vigente; inadimplemento com retomada → 10.
- Embargos à execução ou impugnação ao cumprimento **com efeito suspensivo total**
  (art. 919, §1º; art. 525, §6º, CPC) → **11**; **efeito suspensivo parcial**
  (parcela incontroversa prossegue) → **12**.
- Exceção de pré-executividade: **não suspende** por si → **10**, salvo decisão
  expressa atribuindo efeito suspensivo (→ 11/12 conforme a extensão).
- **15 exige extinção definitiva**: sentença extintiva (art. 924/925 CPC; prescrição
  intercorrente — art. 40, §4º, LEF, após contraditório) **com trânsito/baixa
  definitiva**. Arquivamento provisório nunca é 15.

## F-06 — Sobrestamento × fase recursal subjacente (13 × 04/07)

**Sinais**: decisão de sobrestamento por afetação — Tema Repetitivo, Repercussão Geral,
IRDR, IAC, SIRDR (suspensão nacional determinada pelo STF/STJ em incidente), grupo de
recursos representativos de controvérsia, suspensão por controvérsia — incidindo sobre
processo com recurso em tramitação; suspensão do art. 313 CPC (morte, convenção das
partes, prejudicialidade). Quando a peça identificar o número do Tema/incidente,
registrar em `flags.tema_vinculado`.
**Resolução**: fora da execução, o sobrestamento **sobrepõe** → **13**, registrando
a fase que subjaz em `flags.fase_subjacente` (ex.: "07").
**Retomada**: a saída da fase 13 exige peça de **dessobrestamento/retomada**
(decisão de levantamento da suspensão, revogação da suspensão, desarquivamento com
prosseguimento, determinação de aplicação do paradigma). Presente a peça de retomada
como último evento determinante, volta a valer a fase subjacente ou a que resultar do
julgamento subsequente (ex.: F-04 — retratação). Sem peça de retomada, o processo
permanece 13 ainda que o paradigma já tenha sido julgado — é vedado presumir a
retomada (RE-08).
**Na execução**: suspensão resolve em 11/12 (RE-03.3), jamais 13; a retomada
documentada devolve a 10.

## F-07 — Conversão em renda × arquivamento (14 × 15) e arrecadação parcial (14 × 10)

**Sinais**: termo/decisão de conversão de depósito em renda; DAM de conversão;
mandado de pagamento e comprovantes de resgate/levantamento em favor do ente;
sentença de extinção pela satisfação (art. 924, II, CPC).
**Resolução**: satisfação com arrecadação comprovadamente ao ente credor
(polaridade positiva — taxonomia §5) → **14**, prevalecendo sobre arquivamento
posterior na perspectiva padrão (`processual_arrecadatoria`, RE-06); sob
`perspectiva_classificacao = "fase_processual_atual"`, arquivamento definitivo
válido posterior → 15. Em ambas, registrar
`marcadores.houve_conversao_em_renda = true`. Arrecadação **parcial** com execução
prosseguindo → **10** + `flags.arrecadacao_parcial = true`. Transação/acordo com
pagamento integral ao ente → 14; extinção por cancelamento do título, prescrição ou
renúncia, sem arrecadação → 15. Peça financeira sem polaridade identificável não
sustenta 14 (→ F-13 ou 16 + `motivo_abstencao = "polaridade_indeterminada"`).

## F-08 — Adjudicação, arrematação e alienação (10 × 14)

**Sinais**: edital de leilão, auto de arrematação, auto de adjudicação, carta de
arrematação/adjudicação.
**Resolução**: a expropriação em si mantém **10**; a fase evolui a **14** somente
quando o produto reverte ao ente credor (mandado de levantamento; conversão do
produto; termo de quitação/satisfação). Adjudicação **pelo próprio ente credor**
do bem penhorado equivale a satisfação → 14 (total) ou 10 + `arrecadacao_parcial`
(parcial).

## F-09 — Fazenda executada: precatório e RPV (10 × 14 × 15)

**Sinais**: ofício requisitório, expedição de precatório (art. 535, §3º, I, CPC) ou
RPV (inciso II), comprovante de depósito/pagamento requisitório.
**Resolução**: expedição do requisitório → **10** (execução em curso contra o ente).
Pagamento do precatório/RPV → satisfação **contra** o ente: **não é 14** (RE-06 —
polaridade); com extinção e baixa → **15**.
**Flag**: quando a árvore evidenciar polo passivo fazendário, registrar no
raciocínio para evitar falso 14.

## F-10 — Ação rescisória e impugnações autônomas (não regridem a fase)

**Sinais**: peças de ação rescisória (art. 966 CPC), querela nullitatis, mandado de
segurança contra ato judicial — normalmente em autos apartados, mas por vezes
refletidas na árvore.
**Resolução**: a existência de impugnação autônoma **não altera** a fase do
processo originário (03/06/09/15 permanecem), salvo peça que documente concessão de
tutela suspendendo a execução do julgado (→ 11/13 conforme o domínio). Sinais de
rescisória na árvore do próprio processo → registrar no raciocínio; se houver
confusão de autos → RE-07 (desambiguação).

## F-11 — Certidão de trânsito seguida de peça recursal posterior

**Sinais**: certidão de trânsito e, após, petição de recurso, embargos de declaração
com efeito modificativo, ou decisão que desconstitui a certidão ("torno sem efeito").
**Resolução**: contradição documental. Se houver peça que desconstitua expressamente
a certidão → prevalece o estado reaberto (fase recursal correspondente). Sem peça
desconstitutiva → **16** (RE-07, contradição insanável no metadado).

## F-12 — Desistência, não conhecimento e trânsito superveniente

**Sinais**: homologação de desistência do recurso (art. 998 CPC), decisão de não
conhecimento/inadmissão sem novo recurso, certidão de decurso de prazo.
**Resolução**: a inadmissão/desistência do último recurso pendente conduz ao
trânsito: com certidão → 03/06/09 conforme o grau do último julgado; sem certidão →
inferência limitada (RE-05, confiança ≤ 0.70, `transito_inferido = true`). Agravo
interno/agravo em REsp pendente contra a inadmissão mantém 07.

## F-13 — Pendência financeira × arquivamento definitivo (15 × 16)

**Sinais**: peças de depósito judicial (guia/comprovante de depósito, abertura de
conta judicial, caução em dinheiro) **sem** peça posterior de destinação — alvará de
levantamento, mandado de pagamento, conversão em renda, ou certidão de inexistência
de saldo — seguidas de arquivamento/baixa.
**Resolução**: o arquivamento definitivo com saldo potencialmente ativo em conta
judicial é **inválido como fase 15**. Havendo peça de arquivamento/baixa mas com
depósito documentado sem destinação visível na árvore:
- se a última peça satisfativa indica arrecadação ao ente credor → 14 (F-07);
- caso contrário → **16** + `flags.pendencia_financeira = true`, recomendando
  saneamento financeiro antes da baixa real.
**Fundamento estrutural**: paradigma dos regimes de destinação de depósitos
judiciais (na esfera federal, Resolução CJF 708/2021 — ofício de conversão em renda
com relatório de saldo remanescente; a baixa pressupõe saldo zero). Na esfera
estadual/municipal aplica-se o instrumental próprio (alvará, mandado de pagamento,
DAM de conversão), mas a lógica de trava é idêntica.
**Cautela**: a mera existência de depósito no curso do processo não rebaixa fase
alguma — a trava incide apenas sobre a pretensão de classificar 15.

---

## Tabela-síntese de resolução

| Fronteira | Conflito | Resolve para | Flag principal |
|---|---|---|---|
| F-01 | 10 × recursal | recursal | `execucao_provisoria` |
| F-02 | capítulos | recursal do capítulo pendente | `transito_parcial`, `execucao_definitiva_parcial` |
| F-03 | remessa necessária | 04 somente com peça de remessa; sem peça → 02 | `remessa_necessaria` |
| F-04 | retratação | 04/02 (reativação) | — |
| F-05 | 11 × 12 × 15 | conforme extensão/definitividade | — |
| F-06 | 13 × recursal | 13; saída exige peça de retomada | `fase_subjacente`, `tema_vinculado` |
| F-07 | 14 × 15 × 10 | 14 se satisfação ao ente (perspectiva padrão); 15 sob fase_processual_atual | `arrecadacao_parcial`, marcador de conversão |
| F-08 | expropriação | 10; 14 só com reversão ao ente | `arrecadacao_parcial` |
| F-09 | precatório/RPV | 10; pago → 15 (nunca 14) | — |
| F-10 | rescisória | fase originária inalterada | — |
| F-11 | trânsito × recurso posterior | 16 (salvo desconstituição expressa) | — |
| F-12 | desistência/inadmissão | trânsito (03/06/09) | `transito_inferido` |
| F-13 | 15 × saldo em conta judicial | 14 (se satisfação ao ente) ou 16 | `pendencia_financeira` |
