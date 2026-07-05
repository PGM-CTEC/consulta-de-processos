# Output Schema — Contrato JSON da Classificação

Contrato obrigatório da saída, individual ou por item de lote.

## Campos

| Campo | Tipo | Regra |
|---|---|---|
| `numero` | string | número CNJ do processo (ou identificador fornecido) |
| `fase_codigo` | enum `"01"–"15"`, `"16"`, `"ERR"` | `16` se confiança < 0.75 (RE-07); `ERR` só para falha técnica (RE-10) |
| `fase_nome` | string | nome oficial da fase; em ERR, descrição do erro |
| `confianca` | number 0–1 | confiança da classificação (em 16, a confiança da própria abstenção não se aplica: reportar a maior confiança alcançada pela hipótese) |
| `fase_provavel` | enum ou null | hipótese material plausível quando `fase_codigo = "16"`; nunca preenchida quando há fase substantiva |
| `motivo_abstencao` | enum ou null | `opacidade` \| `transito_nao_certificado` \| `contradicao_documental` \| `polaridade_indeterminada` \| `pendencia_financeira` \| `confianca_insuficiente` |
| `modo_evidencia` | enum | `metadados_apenas` \| `metadados_e_teor`; usar `metadados_e_teor` quando o fallback de teor for acionado |
| `perspectiva_classificacao` | enum | `processual_arrecadatoria` (default) \| `fase_processual_atual` (RE-06) |
| `qualidade_arvore` | enum | `suficiente` \| `parcial` \| `opaca` \| `contraditoria` \| `tecnicamente_invalida` (esta última implica ERR) |
| `regra_determinante` | string | regra(s) do pipeline/fronteira que decidiram (ex.: `"R3.1 / RE-06"`, `"F-03"`) |
| `classe_processual` | string ou null | classe informada no payload da árvore, quando presente (RE-11); null se ausente |
| `marcadores` | object | marcadores econômicos independentes da fase: `houve_conversao_em_renda` (bool); extensível |
| `documentos_determinantes` | array de int | `ordem` das peças que sustentam a fase; vazio em 16 por opacidade |
| `flags` | object | ver abaixo |
| `raciocinio` | string | 1–4 frases citando peças (ordem/data) e a regra determinante |
| `mensagem` | string (só ERR/16) | explicação da falha técnica ou da indeterminação |

## Flags

`execucao_provisoria`, `execucao_definitiva_parcial`, `arrecadacao_parcial`,
`transito_inferido`, `transito_parcial`, `remessa_necessaria`,
`pendencia_financeira`, `arvore_opaca`, `conteudo_suspeito`, `fallback_teor_acionado` (booleanos);
`fase_subjacente` (enum de fase ou null); `tema_vinculado` (string ou null);
`documentos_lidos_fallback` (array de ordens, máximo 5); `campos_inferidos` (array de `{ordem, campo, valor_inferido, fundamento}`).

## Invariantes

1. `fase_codigo = "16"` ⟺ classificação substantiva não alcançou o threshold; `fase_provavel` opcionalmente preenchida.
2. `fase_provavel != null` ⟹ `fase_codigo = "16"`.
3. `fase_codigo ∈ 10–15` (título judicial) ⟹ existe peça de trânsito/título/ato executivo em `documentos_determinantes`.
4. `fase_codigo = "14"` ⟹ polaridade positiva comprovada (taxonomia §5).
5. `flags.transito_inferido = true` ⟹ `confianca ≤ 0.70` ⟹ `fase_codigo = "16"` com `fase_provavel` (RE-05 + RE-07).
6. `qualidade_arvore = "tecnicamente_invalida"` ⟺ `fase_codigo = "ERR"`.
7. Em lote, itens ERR/16 não abortam os demais.
8. `classe_processual` executiva ⟹ `fase_codigo` ∉ {"01"…"09"} e `fase_provavel` ∉ {"01"…"09"} (RE-11).
9. `flags.fallback_teor_acionado = true` ⟹ `modo_evidencia = "metadados_e_teor"` e `flags.documentos_lidos_fallback` contém no máximo 5 ordens, em ordem do documento mais recente para o mais antigo (RE-12).
10. Documento batizado de "Despacho" não pode aparecer como determinante por metadado; só pode aparecer em `documentos_determinantes` se o teor lido no fallback trouxer ato inequívoco (RE-12).

## Exemplo — abstenção com hipótese

```json
{
  "numero": "0004999-66.2015.8.19.0001",
  "fase_codigo": "16",
  "fase_nome": "Indeterminado — Revisão Humana",
  "confianca": 0.35,
  "fase_provavel": "10",
  "motivo_abstencao": "opacidade",
  "modo_evidencia": "metadados_apenas",
  "perspectiva_classificacao": "processual_arrecadatoria",
  "qualidade_arvore": "opaca",
  "regra_determinante": "RE-07(iv)",
  "marcadores": { "houve_conversao_em_renda": false },
  "documentos_determinantes": [],
  "flags": { "arvore_opaca": true, "fallback_teor_acionado": false, "documentos_lidos_fallback": [], "campos_inferidos": ["autor/grau de todas as peças"] },
  "raciocinio": "Árvore é dossiê de trabalho sem peça decisória nominada; sinais fracos de citação/localização sugerem execução em curso, insuficientes para classificar.",
  "mensagem": "Recomenda-se obter a árvore dos autos judiciais ou o teor das peças opacas."
}
```
