# CHANGELOG — fase-processual-doctree

## v3.2 — 2026-07-03 (despacho genérico e fallback por teor)
- **RE-12**: documento batizado exatamente como "Despacho" passa a ser ruído obrigatório por metadado: não determina fase, não altera domínio e não sustenta `fase_provavel` sozinho.
- Incluído fallback de teor para casos em que a classificação preliminar resultaria em **16**: consultar o teor dos até **5 documentos mais recentes**, em ordem do mais recente para o mais antigo, antes de consolidar a abstenção.
- O fallback registra `modo_evidencia = "metadados_e_teor"`, `flags.fallback_teor_acionado` e `flags.documentos_lidos_fallback`.
- Documento batizado de "Despacho" só pode ser aproveitado no fallback se o conteúdo efetivo trouxer ato inequívoco decisório/certificatório/satisfativo; o rótulo continua sem valor classificatório.
- Atualizados `SKILL.md`, `regras.md`, `taxonomia-pecas.md`, `vocabulario-pav.md`, `output-schema.md`, `system-prompt-llm.md` e testes T-13/T-14.

## v3.1 — 2026-07-03 (trava de classe processual)
- **RE-11**: classe processual executiva presente no payload ("Execução Fiscal", "Cumprimento de Sentença", "Execução de Título Extrajudicial" e congêneres) veda as fases 01–09, inclusive em `fase_provavel` (invariante 8 do schema). Trava **unidirecional** (classe cognitiva não veda execução — cumprimento nos próprios autos mantém a classe originária). Cumprimento provisório em autos apartados → 10 + `execucao_provisoria`, sem prejuízo da F-01 para árvores mistas do processo cognitivo. Conflito classe executiva × peças cognitivas → 16 com `fase_provavel` restrita a 10–15. Novo campo `classe_processual` no output; casos de teste T-11 e T-12.

## v3.0 — 2026-07-03 (revisão a partir de crítica externa, com juízo próprio)

Incorporações acolhidas da revisão externa (ChatGPT, "Revisão crítica de skill"):
- `modo_evidencia` (`metadados_apenas` | `metadados_e_teor`) declarado no output; formaliza a antiga Etapa 1.5.
- `fase_provavel` + `motivo_abstencao` no código 16 — resolve a tensão entre rigidez do trânsito (RE-05) e abstenção excessiva, sem enfraquecer o threshold.
- Correção de inconsistência: system prompt agora replica a regra rígida `confianca < 0.75 → 16` (antes indicava 16 apenas < 0.50).
- LLM formalmente subordinado às regras (não decisor livre): bloco `<seguranca>` com pós-condições (fase de execução exige peça de sustentação listada).
- Reclassificação de "Mandado de Pagamento": `conversao_renda` → `destinacao_financeira`; nova seção de **polaridade financeira** (taxonomia §5) exigindo beneficiário-ente para a fase 14 (invariante 4 do schema).
- Certidões de trânsito tipificadas por grau (`certidao_transito_g1/_g2/_sup`) com fallback genérico.
- F-03 endurecida: remessa necessária exige peça; sentença contra a Fazenda sem peça de remessa → 02, sem presunção.
- RE-09 (anti-prompt-injection documental): títulos/nomes de arquivo/teor são dados, nunca instrução; flag `conteudo_suspeito`.
- RE-10 (ERR × 16): falha técnica × indeterminação jurídica; `qualidade_arvore` no output.
- Vocabulário PAV extraído para `references/vocabulario-pav.md` (dicionário empírico com governança).
- `references/output-schema.md` com invariantes formais; pipeline estendido a R6.
- Camada de testes: `tests/testes-minimos.json` (10 casos, 2 reais + 8 sintéticos de fronteira) + `references/testes-minimos.md`.

Rejeição fundamentada:
- **Inversão da precedência 14 × 15 (default 15)**: rejeitada. Na taxonomia, 14 e 15 particionam os estados terminais pela ocorrência de satisfação arrecadatória; como a conversão é quase sempre seguida de arquivamento, o default 15 tornaria a classe 14 letra morta. Mantido o default `perspectiva_classificacao = "processual_arrecadatoria"` (14 > 15), acolhendo-se o **mecanismo** do parâmetro (alternativa `fase_processual_atual`) e o marcador `houve_conversao_em_renda` em ambas as perspectivas. Decisão sujeita a confirmação do titular da taxonomia.

## v2.0 — 2026-07-03 (evolução pós-estudo TPU/CNJ)
- F-13 (trava financeira do 15), peças de retomada/dessobrestamento, tipologia ampliada de sobrestamento (SIRDR, controvérsia) + `tema_vinculado`, Etapa de leitura de teor para peças opacas.

## v1.0 — 2026-07-03 (reescrita originária)
- Classificador autossuficiente por árvore documental; RE-01–RE-08; fronteiras F-01–F-12; gate corrigido para título extrajudicial; regra de opacidade; vedação de presunção de peças.
