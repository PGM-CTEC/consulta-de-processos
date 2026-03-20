# Adaptando Autoresearch para Legal Tech

O repositório `autoresearch` original foca em melhorar o treinamento de um GPT no dataset Shakespeare. Para usá-lo no contexto da PGM-CTEC (ex: melhorar a classificação de fases processuais), siga estes passos:

## 1. Preparação dos Dados (`prepare.py`)
Atualmente, o `prepare.py` baixa o dataset Shakespeare. Você deve modificá-lo para:
- Carregar exemplos de movimentos processuais e suas classificações corretas (ex: de `consulta_processual.db`).
- Tokenizar esses dados de forma apropriada para o seu modelo de classificação.

## 2. Modelo e Treinamento (`train.py`)
O `train.py` contém um GPT pequeno. Se o seu objetivo é classificação:
- Mude a cabeça do modelo de "próximo token" para "classificação".
- Ajuste a função de perda (Loss) para CrossEntropy focada nas fases processuais (1-15).

## 3. Instruções do Agente (`program.md`)
Altere o `program.md` para descrever o novo objetivo:
> "Seu objetivo é encontrar a melhor arquitetura de Transformer e hiperparâmetros para classificar movimentos processuais nas 15 fases definidas na Skill do projeto."

## Hardware e Performance
Como o hardware local possui uma **MX110 (2GB)**:
- Mantenha o `batch_size` e o número de camadas (`n_layer`) baixos.
- Use precisão `bfloat16` ou `float16` para economizar memória.
- Considere rodar experimentos curtos (ex: 2 minutos por iteração) para validar mudanças rapidamente.
