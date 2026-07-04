# Design Spec: Adaptação das Regras do `fase-processual-doctree` ao `DocumentPhaseClassifier`

Data: 2026-07-04
Status: Draft — insumo para planejamento de implementação (writing-plans)
Autor: sessão de brainstorming com o usuário + investigação de código

## 1. Contexto e motivação

O sistema classifica a fase processual (códigos `01`–`15`) de processos PGM-Rio
consultando três fontes, com prioridade de consolidação: **DataJud (CNJ)** →
**Fusion PAV (andamentos)** → **Árvore PAV (peças/documentos)**. A consolidação
tri-fonte acontece em `_consolidar_tres_fontes()`
(`backend/services/process_service.py:35-92`), chamada a partir de
`_parse_datajud_response()` (linha ~579).

As classificações de Fusion e de Árvore PAV são produzidas pela mesma classe,
`DocumentPhaseClassifier` (`backend/services/document_phase_classifier.py`), através
do método público `classify_with_trace(movimentos, classe_processual)`. Os dois
caminhos de chamada são:

- Fusion (andamentos): `process_service.py:244-248`
- Árvore PAV (peças): `process_service.py:320-322`

Nenhum dos dois caminhos passa qualquer indicação de origem ao classificador — do
ponto de vista do código, "movimento do Fusion" e "documento da árvore PAV" são a
mesma coisa: uma lista de `FusionMovimento`.

Existe hoje, em paralelo, a skill `fase-processual-doctree/`, que formaliza um
conjunto de regras determinísticas (RE-01 a RE-12, pipeline R0-R7, fronteiras
F-01 a F-13) para classificar fase **exclusivamente a partir da árvore de
documentos**, com uma banda de confiança explícita e um código de abstenção
`16` ("Indeterminado — Revisão Humana") quando a confiança fica abaixo de 0.75.
Essas regras foram derivadas do CPC/2015, da LEF e do CTN e são mais rigorosas e
mais completas do que a lógica hoje embutida no classificador de produção.

### A lacuna funcional

O branch de execução do classificador atual, `_classify_execucao_traced`
(`document_phase_classifier.py:611-689`), resolve apenas três desfechos:

- `E1_arquivamento` → fase 15
- `E2_suspensao` → fase 11 (suspensão total)
- `E3_fallback` → fase 10 (execução em andamento)

Ele **nunca** produz fase `12` (execução suspensa parcialmente) nem fase `14`
(conversão em renda). Isso não é uma lacuna de "rigor adicional" do doctree — é uma
capacidade ausente hoje: não existe caminho de código, em nenhuma circunstância,
que devolva `12` ou `14` como fase consolidada. As regras RE-03.2 (suspensão total
vs. parcial) e RE-06 (conversão em renda) do doctree preenchem exatamente essa
lacuna.

Este documento especifica como portar as regras determinísticas do doctree
(RE-01 a RE-12, exceto a etapa de leitura de teor/PDF) para dentro do
`DocumentPhaseClassifier`, em Python puro, sem qualquer chamada a LLM em runtime.

## 2. Decisões de escopo já tomadas

Estas decisões foram tomadas em sessão de brainstorming com o usuário e não estão
em aberto para esta fase. Alternativas não devem ser propostas.

### 2.1 Portar regras determinísticas para dentro do classificador existente

RE-01 a RE-12 do doctree (exceto a parte de leitura de teor de PDF — ver §9) são
implementadas como lógica Python pura dentro de
`backend/services/document_phase_classifier.py`. Nenhuma chamada a LLM ocorre em
tempo de execução nesta fase.

### 2.2 Introduzir o código de fase "16"

O pipeline passa a poder retornar `phase = "16"` ("Indeterminado — Revisão
Humana"), com banda de confiança e abstenção calibrada, no espírito de RE-07 do
doctree. Ver §5 para os detalhes de threshold e de propagação na consolidação
tri-fonte.

### 2.3 Evoluir a classe compartilhada, não criar um classificador dedicado

**Decisão explícita do usuário, contra a recomendação técnica dada, mas
vinculante:** `DocumentPhaseClassifier` continua sendo uma única classe
compartilhada entre o caminho Fusion (andamentos) e o caminho Árvore PAV
(documentos/peças). O usuário optou por evoluir essa classe em vez de criar um
classificador dedicado exclusivo para árvore de documentos (que seria o desenho
mais próximo do que a skill `fase-processual-doctree` pressupõe, já que ela é
declaradamente "autônoma" e opera só sobre árvore de peças).

Consequência aceita e assumida pelo usuário: como as regras RE-01 a RE-12 passam a
valer para a mesma classe, **o comportamento do caminho Fusion também é
recalibrado** — não apenas o caminho Árvore PAV. Não há como introduzir, por
exemplo, a trava de despacho genérico (RE-12) ou a autoria como sinal (RE-04)
"só para árvore" sem tocar no branch que também atende andamentos do Fusion,
porque é o mesmo código.

Por isso, a suíte de testes existente (agnóstica de origem, porque testa a classe
diretamente com listas sintéticas de `FusionMovimento`) vira **guarda de
regressão obrigatória** — ver §8.

### 2.4 Leitura de teor fica fora de escopo nesta fase

Investigação inicial confirmou que não existe, no **backend deste projeto**,
nenhum endpoint que devolva conteúdo/arquivo de peça. O endpoint de árvore
(`/services/arquivos/arvore-processo-by-sistema/{cnj}`, consumido em
`backend/services/fusion_api_client.py:217-305`) devolve apenas metadados por
documento (`nomeArquivo`, `tipo`, `dataAutuacao`, `id`/`numeroFolha`) — não o
conteúdo do PDF.

**Atualização (2026-07-04):** o usuário apontou a existência de um servidor MCP
interno ("MCP-PAV", `http://10.32.96.226:8010/mcp`, IP privado — só alcançável a
partir da rede interna/máquina local, não do endpoint de nuvem do Claude) que expõe,
via bridge OpenAPI (`http://10.32.96.226:8010/mcp/openapi.json`), os seguintes
endpoints confirmados:

- `GET /api/mcp/pavs?numero_processo=` — metadados do processo (PAV)
- `GET /api/mcp/arvore_pav?numero_processo=` — árvore de documentos do PAV
- `GET /api/mcp/arvore_autos?numero_processo=` — árvore de documentos dos autos eletrônicos (PJe/eproc/etc.)
- `GET /api/mcp/pav_document?document_id=` — **candidato a endpoint de conteúdo** de documento do PAV por id
- `GET /api/mcp/autos_document?id_documento=&numero_judicial=` — **candidato a endpoint de conteúdo** de documento dos autos eletrônicos

Os dois últimos parecem preencher exatamente a lacuna que motivou marcar a leitura
de teor como fora de escopo. **Porém o formato real do payload (texto extraído vs.
apenas mais metadados vs. base64 do PDF) ainda não foi confirmado** — o único teste
realizado, com o número `3053631-86.2026.8.19.0001`, retornou 404 em todos os
endpoints (processo não encontrado na base PAV/Fusion, não uma falha do serviço).
Ver referência de memória `reference_mcp_pav_server` para o registro completo.

A Etapa 1.5/1.6 do doctree (leitura de teor de peças opacas, fallback de teor para
os até 5 documentos mais recentes antes de consolidar `16`) continua fora do
escopo **desta** fase de implementação, mas a natureza do trabalho pendente mudou:
não é mais um "spike para descobrir se existe endpoint" — é confirmar o formato de
`pav_document`/`autos_document` com um número de processo real existente na base, e
então desenhar a integração (incluindo como o backend chamaria esse MCP: via
cliente HTTP direto aos endpoints REST, ou via protocolo MCP nativo pelos endpoints
`/sse`+`/messages`). Ver §9 para o detalhamento do que fica de fora desta fase.

### 2.5 Gancho reservado para LLM futuro

Reserva-se um ponto de extensão para permitir plugar uma segunda opinião via LLM
no ramo de baixa confiança/abstenção (`16`), na linha da variante documentada em
`fase-processual-doctree/references/system-prompt-llm.md`. Não implementado agora
— apenas a interface é reservada. Ver §7.

## 3. Mapeamento regra-a-regra

| Regra doctree | Onde entra no código atual | Mudança concreta |
|---|---|---|
| **RE-01** — Gate de domínio (título extrajudicial → execução desde a origem; senão, trânsito do mérito separa conhecimento de execução) | `classify_with_trace()` já bifurca em `_classify_execucao_traced` / `_classify_conhecimento_traced` via `_is_classe_execucao(classe_norm)` (linhas 319-355, 194-202) | Lógica já existe em espírito. Ajuste: garantir que a bifurcação por classe (RE-01 título extrajudicial) e a trava de classe expandida (RE-11, ver linha própria abaixo) fiquem inequivocamente separadas — hoje `_is_classe_execucao` mistura as duas responsabilidades num único predicado de string. |
| **RE-02** — Estado atual (peça determinante mais recente; ruído nunca determina fase) | Ambos os branches já percorrem `ordered` do mais recente para o mais antigo e usam índices (`arq_idx`, `transito_idx`, etc.) | Reforçar explicitamente a exclusão de ruído (RE-12: despachos genéricos) do cálculo desses índices — hoje nenhuma âncora filtra "Despacho" batizado. |
| **RE-03.1** — 14 > 15 (conversão prevalece sobre arquivamento posterior) | Não existe: `_classify_execucao_traced` não tem noção de fase 14 | Nova âncora de conversão em renda (ver taxonomia doctree: termo/decisão de conversão, DAM de conversão, comprovante de resgate com polaridade positiva) verificada **antes** de `E1_arquivamento`, análoga à precedência já implementada para trânsito+sentença no branch de conhecimento. |
| **RE-03.2** — Suspensão total (11) × parcial (12), nunca 15 | Parcialmente existe: `E2_suspensao` só produz 11 | Nova âncora de suspensão **parcial** (embargos/impugnação com efeito suspensivo parcial, garantia parcial — taxonomia doctree) que produz fase 12 antes do fallback E3. |
| **RE-03.3** — Sobrestamento sobrepõe conhecimento (→13) | Já existe: `P5_suspensao` no branch de conhecimento produz 13 | Sem mudança estrutural; validar que a âncora de suspensão distingue sobrestamento de conhecimento (→13) de suspensão de execução (→11/12), o que hoje já é feito pela bifurcação de branch. |
| **RE-03.4** — Domínio de execução é pegajoso (incidentes não retornam a 01-09) | Implícito na bifurcação por classe processual | Sem peça de trava explícita hoje; ao introduzir RE-11 (trava expandida), este comportamento passa a ser garantido também quando a classe muda de rótulo dentro da árvore. |
| **RE-04** — Autoria como sinal (parte=postulação, órgão julgador=julgamento, serventia=certificação) | Não existe: `FusionMovimento` não tem campo de autor | Novo campo opcional `autor` em `FusionMovimento` (ver §4). Quando ausente, inferir do texto disponível (`tipo_local`/`tipo_cnj`/`descricao`) usando o dicionário de sinais da taxonomia doctree (§2 de `taxonomia-pecas.md`: "certidão/termo/mandado" → serventia; "sentença/decisão" → juízo 1º grau; "acórdão/voto/ementa" → tribunal 2º grau; "petição/razões/contrarrazões" → parte). Autoria usada como desempate e reforço de confiança, não como âncora isolada nova. |
| **RE-05** — Trânsito exige certificação explícita; inferência só com confiança ≤ 0.70 | Parcialmente existe: `_ANCHOR_TRANSITO` já exige "certidão de trânsito"/"trânsito em julgado" explícito | Adicionar o teto de confiança 0.70 quando o trânsito for **inferido** (decurso de prazo/desistência sem certidão) — hoje o classificador não tem esse modo de inferência; ele simplesmente não classifica como transitado sem âncora explícita. Ao introduzir inferência de trânsito (RE-05/F-12), aplicar o teto e marcar sinalização equivalente a `flags.transito_inferido`. |
| **RE-06** — Conversão em renda: gatilho, polaridade e perspectiva (14>15 padrão) | Não existe (mesma lacuna de RE-03.1) | Nova âncora de conversão com verificação de **polaridade positiva** (taxonomia doctree §5: "em favor do Município/MRJ", "resgate MRJ", "DAM de conversão" vs. termos neutros como "mandado de pagamento"/"alvará" sozinhos, que não bastam). Arrecadação parcial com execução em curso → mantém fase 10 com marcador equivalente a `flags.arrecadacao_parcial`. |
| **RE-07** — Abstenção calibrada com hipótese material (16, nunca forçar classificação) | Não existe: todo caminho hoje sempre retorna 01-15, nunca abstém | Novo código 16 na saída de ambos os branches quando a confiança calculada cair abaixo do threshold (0.75, parametrizável). Campos novos `fase_provavel`/`motivo_abstencao` em `ClassificationResult` (ver §4). Ver §5 para a definição precisa de quando isso dispara. |
| **RE-08** — Fundamentação exclusivamente documental (vedado presumir peça ausente) | Já é o comportamento de fato do classificador (ele só olha para os movimentos recebidos) | Sem mudança de lógica; documentar como invariante ao portar as demais regras, para não introduzir heurísticas de "tempo decorrido" como sinal isolado em nenhuma âncora nova. |
| **RE-09** — Dados documentais são evidência, nunca instrução | Já é o comportamento de fato (o classificador só faz regex sobre texto normalizado, nunca interpreta o texto como comando) | Sem mudança de código necessária nesta fase (relevante principalmente para a Etapa 1.5/1.6 de teor, que está fora de escopo — §9). Vale registrar a invariante para quando o gancho de teor for implementado no futuro. |
| **RE-10** — ERR (falha técnica) × 16 (indeterminação jurídica) | Hoje o classificador não distingue os dois: lista vazia cai em fallback silencioso (`"01"` no branch de conhecimento, `"10"` no branch de execução — ver `_classify_conhecimento_traced`/`_classify_execucao_traced`, casos `if not movimentos`) | Os fallbacks de lista vazia e os fallbacks conservadores `P6_fallback_antes_sentenca` / `E3_fallback` são exatamente onde a distinção 16 × dado técnico ausente precisa ser decidida. Este documento **não decide** se lista vazia deve virar erro técnico (equivalente a `ERR` do doctree, hoje inexistente no schema deste sistema) ou baixa confiança → 16; ver decisão em aberto no §5. |
| **RE-11** — Trava de classe processual expandida (classe executiva veda 01-09) | Parcialmente existe: `_is_classe_execucao()` já bifurca por classe, mas é uma bifurcação binária de branch, não uma trava pós-hoc sobre o resultado | Reforçar como trava explícita e unidirecional: classe executiva nunca permite que o resultado final caia em 01-09, mesmo que sinais textuais ambíguos apontem nessa direção (hoje isso já é garantido estruturalmente pela bifurcação de branch, mas RE-11 também cobre o caso de conflito classe×peças, que hoje não gera abstenção — apenas seguiria cegamente o branch de execução). Ao introduzir 16, o conflito classe executiva × peças puramente cognitivas deve poder abster (fase_provavel restrita a 10-15), em vez de forçar uma fase executiva sem sinal de apoio. |
| **RE-12** (parte de metadado/despacho genérico — **sem** a parte de fallback de teor) | Não existe: nenhuma âncora hoje trata "Despacho" como ruído; um documento nomeado exatamente "Despacho" pode hoje ser confundido por outras âncoras se o texto bater em algum regex | Nova regra de normalização: documento cujo `tipo_local`/`tipo_cnj`/`descricao` normalizado for exatamente `despacho` (ou variante puramente numérica, ex.: `despacho_123`) não pode ser o movimento decisivo de nenhuma âncora nem sustentar `fase_provavel` sozinho. Isso é um filtro aplicado **antes** do cálculo de índices de âncora, não uma âncora nova. A parte de "fallback de teor quando resultado seria 16" (RE-12, segunda metade) fica fora de escopo — §9. |

Fronteiras (F-01 a F-13) não são portadas como regras próprias nesta fase — elas
são, na prática, o resultado esperado da combinação de RE-01 a RE-12 acima. Onde a
tabela cita comportamento de fronteira (ex.: F-07 para 14×15, F-05 para 11×12×15),
isso já está refletido na regra RE correspondente.

## 4. Modelo de dados enriquecido

### 4.1 `FusionMovimento` — novo campo `autor`

```python
@dataclass
class FusionMovimento:
    data: datetime
    tipo_local: str
    tipo_cnj: str
    descricao: str = ""
    autor: Optional[str] = None   # NOVO — "parte" | "serventia" | "juizo_1grau" |
                                   # "tribunal_2grau" | "tribunal_superior" | "terceiro" | None
```

O campo é opcional com default `None` para não quebrar os ~124 testes existentes
que constroem `FusionMovimento` sem esse argumento (contagem confirmada:
`test_document_phase_classifier.py` com 66 funções de teste,
`test_document_phase_classifier_acordao.py` com 7,
`test_document_phase_classifier_execucao.py` com 11,
`test_hierarchical_classification.py` com 40).

Hoje nenhuma das duas fontes de movimentos (`FusionService`/`fusion_api_client.py`)
popula `autor` — nem o caminho de andamentos Fusion nem o caminho de árvore PAV
(`get_arvore_processo`, linhas 217-305, só extrai `nomeArquivo`/`tipo`/
`dataAutuacao`). Portanto `autor` será, na prática, **sempre inferido** pelo
classificador a partir do texto disponível quando as regras RE-04 precisarem dele,
seguindo o dicionário de sinais da taxonomia doctree (§3 acima). Não há mudança
necessária nos clientes de API para esta fase.

### 4.2 `ClassificationResult` — novos campos `fase_provavel` e `motivo_abstencao`

```python
@dataclass
class ClassificationResult:
    phase: str                                    # agora também pode ser "16"
    branch: str
    classe_normalizada: str
    total_movimentos: int
    rule_applied: str
    decisive_movement: Optional[str] = None
    decisive_movement_date: Optional[str] = None
    anchor_matches: dict = field(default_factory=dict)
    confidence: Optional[float] = None
    context_summary: dict = field(default_factory=dict)
    stage: int = 1
    substage: Optional[str] = None
    transit_julgado: str = "nao"

    fase_provavel: Optional[str] = None           # NOVO — só preenchido quando phase == "16"
    motivo_abstencao: Optional[str] = None        # NOVO — enum: opacidade | transito_nao_certificado |
                                                    # contradicao_documental | polaridade_indeterminada |
                                                    # pendencia_financeira | confianca_insuficiente
```

Ambos os campos têm default `None`/opcional — não quebram a suíte existente nem o
serializador `to_dict()`, que precisa apenas incluir as duas chaves novas.

## 5. Confiança e abstenção (código 16)

Existem dois níveis de abstenção a distinguir, e este é o ponto mais delicado da
adaptação:

### 5.1 Por fonte (dentro de `DocumentPhaseClassifier`)

`_compute_confidence()` (linhas 281-317) já calcula um score contínuo de 0.40 a
0.95 e o guarda em `ClassificationResult.confidence`, mas **nenhuma regra atual usa
esse valor para decidir a fase** — o pipeline sempre retorna uma fase substantiva
(01-15), calculada e depois "etiquetada" com uma confiança, nunca o inverso.

Introduzir o threshold de abstenção (0.75) significa que, quando a confiança
calculada para o resultado preliminar ficar abaixo de 0.75, `phase` passa a ser
`"16"`, com a fase substantiva que teria sido retornada preenchendo
`fase_provavel` (nunca `phase`), na linha de RE-07.

**Decisão em aberto para a fase de planejamento — colisão de escala de
confiança.** Os valores hoje produzidos por `_compute_confidence()` não foram
calibrados contra o threshold de 0.75 do doctree; eles foram calibrados apenas
para ordenação relativa entre regras. Casos concretos já identificados no código
atual:

- `P0_execucao_posterior_transito` sempre retorna confiança fixa **0.70**
  (abaixo do threshold);
- `E3_fallback`/`P6_fallback_antes_sentenca` retornam **0.40** ou **0.60**
  (sempre abaixo);
- `E2_suspensao` e sentenças com poucos movimentos (`P3_sentenca_*` com
  `total <= 3`) caem em **0.70** pelo branch genérico final de
  `_compute_confidence` — inclusive por um efeito colateral: a checagem
  `"suspenso" in rule_lower` nunca é atingida porque o nome da regra é
  `"E2_suspensao"` e o código testa substrings como `"arquivamento"`,
  `"transito"`, `"sentenca"`, `"fallback"`, nessa ordem, sem branch para
  `"suspensao"` — caindo no `return 0.70` final por omissão, não por decisão.

Se o gate de 0.75 for aplicado ingenuamente sobre os valores de confiança de hoje,
uma fração considerável dos processos hoje classificados — sobretudo no caminho
Fusion compartilhado — passaria a virar `"16"` só por causa da escala, não por
indeterminação real. Como essa fração indevida seria exatamente o tipo de mudança
que a suíte de regressão (§8) deve capturar, a decisão de **como recalibrar
`_compute_confidence()` para a escala do doctree** (ou, alternativamente, introduzir
um score de confiança paralelo, calculado só para o gate de abstenção, sem alterar
o campo `confidence` legado) fica para o planejamento de implementação. Este
documento não prescreve qual dos dois caminhos tomar.

### 5.2 Consolidado (em `_consolidar_tres_fontes`)

`_consolidar_tres_fontes()` (`process_service.py:35-92`) decide puramente por
prioridade fixa de fonte — nunca olha para `confidence`. Hoje ela já trata uma
fonte com valor `"Indefinido"` como "pular" na cascata de prioridade, mas essa
guarda **não é uniforme**: apenas `cod_pav` é protegido explicitamente
(`cod_pav = _extrair_codigo_fase(fase_pav_tree) if fase_pav_tree != "Indefinido"
else ""`, linha 50). `cod_dj` e `cod_fu` não recebem a mesma proteção — o único
motivo de isso não causar problema hoje é que `"Indefinido"` nunca aparece nos
conjuntos `_FASES_EXECUCAO`/`_FASES_CONHECIMENTO`, então ele nunca vence a Regra 1
(execução>conhecimento) nem a Regra 2 (concordância), apenas eventualmente vence
a Regra 3/4 por fallback — devolvendo o próprio `"Indefinido"` como fase, o que é
inofensivo porque `"Indefinido"` já é o resultado esperado nesse caso.

Ao introduzir `"16"`, essa assimetria deixa de ser inofensiva: a Regra 3 hoje é
`if cod_pav and fase_pav_tree != "Indefinido":` — isso NÃO exclui
`fase_pav_tree == "16"`. Sem correção, uma Árvore PAV que abstém (`"16"`) venceria
a Regra 3 e sobrescreveria uma fase válida vinda do Fusion ou do DataJud, o que é
o oposto do comportamento desejado.

A mudança necessária em `_consolidar_tres_fontes()` é:

1. Tratar uma fonte com `phase == "16"` como "pular" na cascata de prioridade —
   com a mesma exclusão hoje aplicada só a `"Indefinido"`, mas agora aplicada de
   forma **uniforme às três fontes** (DataJud, Fusion, Árvore PAV), não só à
   Árvore PAV;
2. Só produzir `phase == "16"` no resultado **consolidado** quando todas as
   fontes válidas (i.e., que retornaram algum dado) tiverem terminado em `"16"`
   — ou estiverem ausentes/indefinidas.

### 5.3 Distinção semântica: "16" × "Indefinido"

Esta distinção deve ficar explícita em qualquer implementação e em qualquer
mensagem exposta ao usuário: **"Indefinido" significa que a fonte não retornou
dado nenhum** (falha técnica, ausência de resposta, exceção na chamada de API —
ver os vários `_meta_fo["fusion_phase_override"] = "Indefinido"` em
`process_service.py` associados a `except Exception` ou "não encontrado").
**"16" significa que a fonte retornou dados legíveis, mas os sinais são
insuficientes para uma classificação segura** — é indeterminação jurídica, não
ausência técnica. É a mesma distinção que RE-10 do doctree estabelece entre `16` e
`ERR`: nunca confundir os dois. Um "16" nunca deve ser silenciosamente tratado como
"Indefinido" (ou vice-versa) em nenhuma camada — consolidação, persistência ou
frontend.

## 6. Persistência e frontend

### 6.1 Sem migração de schema

`Process.phase` (`backend/models.py:44`) é `Column(String, nullable=True)`, sem
`CHECK` nem enum — aceita a string `"16"` sem qualquer migração. As três fases de
fonte (`datajud_phase`, `fusion_phase_override`, `pav_tree_phase`) e seus campos de
trace já vivem inteiramente dentro do JSON `raw_data.__meta__`
(`Process.raw_data`, coluna `JSON` livre, linha 55) — não há colunas de banco
dedicadas para elas hoje.

Os novos campos `fase_provavel` e `motivo_abstencao` seguem o mesmo padrão: entram
dentro dos dicionários de log já persistidos em `raw_data.__meta__` (ex.:
`fusion_classification_log`, `pav_tree_classification_log`, que já são o
`to_dict()` de `ClassificationResult` serializado — ver `process_service.py:258,
324`), não como novas colunas em `models.py`.

### 6.2 Mapeamento hierárquico (stage/substage) para "16"

`_computar_hierarquia()` (`document_phase_classifier.py:357-376`) resolve
`(stage, substage)` via `PHASE_TO_STAGE_SUBSTAGE.get(result.phase, (Stage.CONHECIMENTO,
Substage.ANTES_SENTENCA))` — ou seja, qualquer `phase` que não esteja no dicionário
`PHASE_TO_STAGE_SUBSTAGE` (`backend/services/hierarchical_classification.py:218-234`)
cai silenciosamente em `(Stage.CONHECIMENTO, Substage.ANTES_SENTENCA)`, isto é,
stage 1 / substage "1.1" (fase legada `01`). Isso significa que, sem uma entrada
explícita para `"16"`, um resultado de abstenção seria erroneamente mapeado para
"Conhecimento — Antes da Sentença" na visão hierárquica — e o mesmo aconteceria em
`derive_legacy_phase()` (`hierarchical_classification.py:149-163`), cujo fallback
absoluto também é `"01"`. O script `backend/scripts/reclassify_hierarchical.py`
(usado para reclassificação em lote) percorre exatamente esses mesmos mapas, então
herdaria o mesmo problema.

**Decisão em aberto para a fase de planejamento:** como `"16"` deve se comportar
no modelo hierárquico de 3 campos (stage/substage/transit) — por exemplo, um novo
`Stage` dedicado (ex.: "Controle / Revisão Humana") com `substage=None`, análogo ao
tratamento hoje dado a `13` e `15`; ou alguma forma de bypass do modelo hierárquico
para esse código específico. Este documento não prescreve qual das duas
abordagens adotar; qualquer implementação deve, no mínimo, garantir que `"16"`
nunca caia no fallback silencioso de `"01"`/stage 1 por omissão de entrada no
mapa.

### 6.3 Frontend

`frontend/src/constants/phases.js` (objeto `VALID_PHASES`, `PHASE_BY_CODE`) e
`frontend/src/utils/phaseColors.js` (mapa `colorMap` em `getPhaseColorClasses`)
precisam de uma entrada nova para o código `"16"` — nome ("Indeterminado — Revisão
Humana"), tipo (ex.: "Controle", distinto de "Conhecimento"/"Execução"/
"Transversal"/"Final") e cor própria, distinta da cor/tratamento que a string
especial `"Indefinido"` já recebe hoje (que é tratada à parte, como um caso
"phase_override" em `normalizePhaseWithMovements()`, linhas 328-341 de
`phases.js`, não como um código de fase entre as 15 oficiais). A escolha exata de
cor e rótulo de tipo fica para a implementação; a exigência funcional é apenas que
`"16"` seja visualmente distinguível de `"Indefinido"` na UI, coerente com a
distinção semântica do §5.3.

## 7. Gancho para LLM futuro

Reserva-se, sem implementar, um ponto de extensão para permitir que uma segunda
opinião via LLM seja plugada no ramo de baixa confiança/abstenção, na linha da
variante `fase-processual-doctree/references/system-prompt-llm.md` (que já define
um contrato de entrada/saída para essa função: árvore normalizada → JSON com
`fase_codigo`, `confianca`, `fase_provavel`, `motivo_abstencao`, `raciocinio`, sob
as mesmas regras RE-01 a RE-12, nunca como decisor livre).

Concretamente, isso significa: `classify_with_trace()` (ou uma variante dela)
recebe um parâmetro opcional, por exemplo `abstention_resolver`, com assinatura
prevista mas não chamada em runtime — algo como
`Optional[Callable[[List[FusionMovimento], ClassificationResult], ClassificationResult]]`,
cujo default é `None`/no-op (o comportamento atual, sem LLM, é preservado
integralmente). Quando o resultado preliminar for `"16"`, se um resolver for
fornecido, ele teria a oportunidade de revisar a decisão antes da consolidação
final; sem resolver, o `"16"` é devolvido como está.

A implementação real dessa chamada — provider, prompt exato, tratamento de retry/
parse, custo, latência — não é decidida aqui. É trabalho futuro, condicionado
também à Fase 2 de leitura de teor (§9), já que o principal caso de uso do LLM na
skill original é justamente resolver peças opacas via teor.

## 8. Testes e validação

### 8.1 Suíte existente como guarda de regressão obrigatória

A suíte atual é agnóstica de origem — ela testa `DocumentPhaseClassifier`
diretamente com listas sintéticas de `FusionMovimento`, sem distinguir se
simulam andamentos Fusion ou documentos de árvore PAV:

| Arquivo | Nº de testes |
|---|---|
| `backend/tests/test_document_phase_classifier.py` | 66 |
| `backend/tests/test_document_phase_classifier_acordao.py` | 7 |
| `backend/tests/test_document_phase_classifier_execucao.py` | 11 |
| `backend/tests/test_hierarchical_classification.py` | 40 (parametrizados) |

Como a Decisão 2.3 evolui a classe compartilhada — e não cria um classificador
paralelo —, qualquer alteração de regra recalibra os dois caminhos (Fusion e
Árvore PAV) ao mesmo tempo. Portanto: **qualquer teste da suíte acima que mudar de
resultado após a adaptação precisa de justificativa explícita, documentada caso a
caso** (por que a nova fase/confiança está correta e a antiga estava errada, ou
qual regra RE-xx motivou a mudança). Uma mudança de resultado sem essa
justificativa não é uma regressão aceitável silenciosamente — é bloqueante.

Não existe hoje nenhum teste dedicado especificamente a dados reais de árvore
PAV (todos os testes atuais usam dados sintéticos), o que reforça a necessidade
do item seguinte.

### 8.2 Importar `testes-minimos.json` como novo arquivo de teste pytest

`fase-processual-doctree/tests/testes-minimos.json` contém 11 casos rotulados de
validação (alguns derivados de processos reais anonimizados, ex. `T-01-conversao-
renda-real`; outros sintéticos de fronteira, ex. `T-02-arvore-opaca-abstencao`, que
testa exatamente o conceito de abstenção/16 hoje inexistente no backend). Este
arquivo é um artefato da skill, não integrado ao pytest do backend. A adaptação
deve incluir um novo arquivo de teste (ex.:
`backend/tests/test_document_phase_classifier_doctree_cases.py`) que carrega
`testes-minimos.json` e roda cada caso contra `DocumentPhaseClassifier`,
adaptando o formato de entrada (`arvore` com `ordem`/`data`/`tipo_peca`/
`nome_arquivo`) para `FusionMovimento`, e verificando `fase_codigo`/
`confianca_min` esperados.

### 8.3 Diff em produção antes do rollout

`backend/scripts/reclassify_hierarchical.py` já é um script de reclassificação em
lote que lê `raw_data.__meta__` já armazenado (sem re-chamar APIs externas) e
recalcula `stage`/`substage`/`transit_julgado`, registrando divergências entre a
fase antiga e a nova derivada. Este script deve ser reaproveitado (rodando em
modo `--dry-run`) para gerar um diff fase-antiga × fase-nova sobre a base de
produção antes do rollout da adaptação — permitindo quantificar o impacto real
(quantos processos mudam de fase, para onde, e quantos passam a cair em `"16"`)
antes de aplicar em produção. O script precisará ser estendido para também
re-executar `DocumentPhaseClassifier.classify_with_trace()` com as novas regras
sobre os movimentos já persistidos, não apenas para re-derivar stage/substage a
partir de fases já calculadas — esse ajuste é detalhe de implementação, não
decidido aqui.

## 9. Fora de escopo / trabalho futuro

- **Leitura de teor de peças (PDF/conteúdo).** Etapas 1.5 e 1.6 do doctree
  (leitura de teor para peças opacas; fallback de teor dos até 5 documentos mais
  recentes antes de consolidar `16`) e a segunda metade de RE-12 (aproveitamento
  de "Despacho" quando o conteúdo, não o rótulo, traz ato decisório). O backend
  deste projeto não tem hoje nenhum endpoint próprio de conteúdo de documento, mas
  existe um servidor MCP interno ("MCP-PAV", `http://10.32.96.226:8010/mcp` — ver
  §2.4 e a memória de referência `reference_mcp_pav_server`) com dois endpoints
  candidatos (`pav_document`, `autos_document`) cujo formato de payload ainda não
  foi confirmado (o teste realizado em 2026-07-04 com um número de processo não
  encontrou dados). Antes de desenhar qualquer fallback de teor, é necessário: (a)
  confirmar o formato real desses dois endpoints com um processo existente na
  base, e (b) decidir como o backend consumiria o MCP-PAV (cliente HTTP direto aos
  endpoints REST descobertos, ou protocolo MCP nativo via `/sse`+`/messages`). Essa
  confirmação e o desenho do fallback que dela decorrer são uma Fase 2 separada,
  fora do escopo deste documento — nenhum algoritmo de extração/leitura de teor é
  proposto aqui.
- **Chamada real a LLM.** O gancho de extensão descrito no §7 é reservado, mas a
  implementação da chamada (provider, prompt, parsing, custo) não faz parte desta
  fase, e depende também da Fase 2 de teor.
- **Recalibração exata da escala de confiança** (§5.1) e **home hierárquico do
  código "16"** (stage/substage — §6.2) são decisões técnicas em aberto,
  deliberadamente não resolvidas neste spec; ficam para a fase de planejamento de
  implementação (writing-plans), que deve escolher uma abordagem concreta antes de
  qualquer código ser escrito.
- **Extensão do script `reclassify_hierarchical.py`** para re-executar a
  classificação completa (não só re-derivar stage/substage) é mencionada como
  necessária no §8.3, mas seu desenho detalhado também fica para o planejamento.
