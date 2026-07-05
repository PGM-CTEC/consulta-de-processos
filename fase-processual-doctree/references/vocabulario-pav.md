# Vocabulário PAV e dos Autos Eletrônicos — dicionário empírico (v0.2)

Valores reais do campo `tipo_peca`/`tipoDePeca` observados em exports PAV (casos de
teste 07/2026). Aplicar como dicionário determinístico antes do fuzzy da seção 4:

| `tipo_peca` PAV | Tipo normalizado | Observações |
|---|---|---|
| Capa | ruído | — |
| Petição Inicial | `peticao_inicial` | — |
| Despacho | ruído obrigatório por metadado | ignorar para classificação da fase; não pode ser peça determinante nem sustentar `fase_provavel` sozinho. Só pode ser aproveitado no fallback de teor (RE-12) se o conteúdo efetivo trouxer ato inequívoco decisório/certificatório/satisfativo. |
| Mandado de Pagamento | `destinacao_financeira` | polaridade indeterminada por si; só conta para 14 com beneficiário-ente identificado (taxonomia §5) |
| Comprovante de Resgate MRJ | `conversao_renda` | resgate de depósito em favor do Município do Rio |
| Aprovação (arquivo "DAM conversão …") | `conversao_renda` | DAM emitido para conversão — sinal forte de fase 14 |
| Andamento Processual / Documento Processo | ruído **opaco** | consulta de andamento em PDF; PODE conter acórdão/sentença — se for a peça mais recente com múltiplas folhas e nome referindo tribunal, tratar como potencialmente decisória irresoluta (→ contribui para 16) |
| Publicação / Comunicação - Intimação Eletrônica / Publicação em diário oficial / Comunicação Externa | ruído | — |
| Petição / protocolo de petição / Protocolo / Anexo de Petição | `peticao_generica` (ruído, salvo nome_arquivo decisório) | inspecionar `nome_arquivo` para recurso/cumprimento |
| Carta Precatória / Aviso de Recebimento / Certidão (mandado negativo) | atos de citação/localização | sinal fraco de execução em fase inicial |
| Pesquisa Parte / Cartão CNPJ / Documentos / Email / Ofício / Ofício Resposta | ruído | — |

**Regra de opacidade PAV**: a árvore PAV é frequentemente o dossiê de trabalho do
procurador, não o espelho dos autos. Ausência de peça decisória nominada NÃO autoriza
inferir fase inicial; na dúvida entre fase e abstenção, acionar o fallback de teor
dos até 5 documentos mais recentes quando o teor estiver disponível; se ainda
insuficiente, abster (16) e recomendar a obtenção da árvore dos autos judiciais ou
conteúdo das peças opacas restantes.

O restante do vocabulário PAV e o vocabulário dos autos eletrônicos permanecem
**[A DEFINIR]**; expandir este dicionário a cada lote validado.

## Governança do dicionário

- Cada lote validado deve retroalimentar esta tabela (`tipo_peca` novo → tipo normalizado + observações).
- Entradas devem registrar a data/lote de observação quando possível.
- Conflitos entre este dicionário e o fuzzy resolvem-se pelo dicionário (determinístico prevalece).
