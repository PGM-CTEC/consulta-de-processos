# Research Module

Esta pasta contém ferramentas e experimentos para aprimorar a inteligência do projeto **Consulta de Processos PGM-CTEC**.

## Conteúdo
- `autoresearch/`: O repositório original do Andrej Karpathy para pesquisa autônoma de modelos GPT.
- `AUTORESEARCH_FOR_LEGAL_TECH.md`: Guia de como adaptar o `autoresearch` para os problemas de classificação jurídica deste projeto.

## Como usar o Autoresearch
O `autoresearch` é um loop que permite que um agente de IA (como eu) tente melhorar o código de treinamento (`train.py`) de forma autônoma, baseado em instruções em `program.md`.

Para iniciar:
1. Navegue até `research/autoresearch`.
2. Configure seu `program.md` com o objetivo desejado.
3. Peça ao seu agente de IA para iniciar o loop de pesquisa.

> [!NOTE]
> Este ambiente foi configurado com `uv` e possui as dependências necessárias instaladas em um ambiente virtual gerenciado pelo `uv`.
