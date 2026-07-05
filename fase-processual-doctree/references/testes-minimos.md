# Testes Mínimos — Validação da Skill

Suíte rotulada em [`../tests/testes-minimos.json`](../tests/testes-minimos.json).
Executar integralmente: (i) antes do primeiro uso produtivo; (ii) após qualquer
alteração em `regras.md`, `casos-fronteira.md` ou `taxonomia-pecas.md`; (iii) ao
expandir `vocabulario-pav.md` com entradas que alterem mapeamentos existentes.

## Estrutura de cada caso

- `arvore`: árvore documental de entrada (formato PAV simplificado);
- `esperado.fase_codigo`: fase obrigatória;
- `esperado.fase_proibida`: fase cuja atribuição constitui falha grave (erro de
  fronteira);
- `esperado.flags` / `motivo_abstencao`: asserções acessórias;
- `esperado.regras`: regras que devem constar de `regra_determinante`.

## Critério de aprovação

Aprovação exige 14/14 em `fase_codigo` e zero ocorrências de `fase_proibida`.
Divergência em flags/motivos é falha leve (registrar e corrigir); divergência de
fase ou atribuição de fase proibida é falha grave (bloqueia uso produtivo).

## Cobertura

| Caso | Fronteira/Regra exercitada |
|---|---|
| T-01 | RE-06/F-07 — conversão em renda com polaridade positiva (caso real) |
| T-02 | RE-07 — abstenção por opacidade com `fase_provavel` (caso real, exemplo negativo) |
| T-03 | F-01 — cumprimento provisório não promove a 10 |
| T-04 | RE-03.2/F-05 — art. 40 LEF → 11, jamais 15 |
| T-05 | F-03 — remessa necessária com peça → 04 |
| T-06 | F-03 negativo — sentença contra a Fazenda sem peça de remessa → 02 |
| T-07 | F-09/RE-06 — precatório pago → 15, jamais 14 (polaridade negativa) |
| T-08 | RE-06/F-13 — peça financeira sem polaridade → 16, jamais 14 |
| T-09 | F-06/RE-08 — sobrestamento sem peça de retomada permanece 13 |
| T-10 | RE-09 — instrução injetada em nome de arquivo é ignorada |
| T-11 | RE-11 — classe executiva veda 01–09 mesmo com árvore pobre |
| T-12 | RE-11 × F-01 — cumprimento provisório apartado → 10 + flag |
| T-13 | RE-12 — documentos batizados de "Despacho" são ruído por metadado |
| T-14 | RE-12 — fallback de teor consulta até 5 documentos mais recentes antes de consolidar 16 |

## Expansão recomendada

Incorporar progressivamente casos reais anonimizados das fronteiras ainda sem
exemplar real: F-02 (capítulos), F-04 (retratação), F-11 (contradição
certidão × recurso) e F-12 (desistência/inadmissão).

