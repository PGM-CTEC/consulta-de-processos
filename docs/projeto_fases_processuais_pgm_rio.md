# PROJETO DE CLASSIFICAÇÃO DE FASES PROCESSUAIS

**PROCURADORIA-GERAL DO MUNICÍPIO DO RIO DE JANEIRO**  
**Coordenação de Tecnologia**

**Integração MNI/DEJT com Tabelas Processuais Unificadas do CNJ**

*Documento Técnico - Janeiro de 2026*

---

## Sumário

1. [Introdução](#1-introdução)
2. [Estrutura Hierárquica das Fases Processuais](#2-estrutura-hierárquica-das-fases-processuais)
3. [Mapeamento de Classes Processuais (CNJ)](#3-mapeamento-de-classes-processuais-cnj)
4. [Mapeamento de Movimentos Processuais (CNJ)](#4-mapeamento-de-movimentos-processuais-cnj)
5. [Mapeamento de Documentos Processuais (CNJ)](#5-mapeamento-de-documentos-processuais-cnj)
6. [Regras de Transição entre Fases](#6-regras-de-transição-entre-fases)
7. [Aplicações Práticas do Sistema de Fases](#7-aplicações-práticas-do-sistema-de-fases)
8. [Considerações para Implementação](#8-considerações-para-implementação)
9. [Próximos Passos](#9-próximos-passos)

---

## 1. Introdução

Este documento apresenta a proposta de estruturação das fases processuais para o sistema de acompanhamento de processos judiciais da PGM-Rio, considerando a integração via MNI (Modelo Nacional de Interoperabilidade) e Domicílio Eletrônico Judicial (Res. CNJ 455/2022), utilizando como base a tríade de informações padronizadas pelo CNJ: Classes, Movimentos e Documentos.

### 1.1 Objetivos do Projeto

- Automatizar a identificação das fases processuais a partir dos dados recebidos via MNI
- Padronizar a gestão de prazos e alertas conforme a fase processual
- Alimentar dashboards gerenciais com indicadores por fase
- Viabilizar triagem e distribuição automática de tarefas
- Fornecer contexto estruturado para modelos de IA na geração de minutas

### 1.2 Escopo

A classificação contempla os dois cenários de atuação da Fazenda Pública Municipal:

- **Fazenda Pública como Autora**: Execuções Fiscais, Ações de Cobrança, Ações Possessórias
- **Fazenda Pública como Ré**: Procedimentos Comuns, Mandados de Segurança, Ações Civis Públicas

---

## 2. Estrutura Hierárquica das Fases Processuais

A estrutura proposta organiza as fases em três níveis hierárquicos principais, permitindo tanto visões macro para gestão executiva quanto granularidade para operação e automação.

### 2.1 Visão Geral da Hierarquia

| Nível 1 (Macro) | Nível 2 (Instância) | Nível 3 (Subfase) |
|-----------------|---------------------|-------------------|
| **1. FASE COGNITIVA** | **1.1 Primeira Instância** | 1.1.1 Postulatória (Petição Inicial → Citação) |
| | | 1.1.2 Defesa (Prazo → Contestação/Exceções) |
| | | 1.1.3 Réplica/Especificação de Provas |
| | | 1.1.4 Saneamento e Organização |
| | | 1.1.5 Instrução (Perícia, Audiências) |
| | | 1.1.6 Decisória (Sentença) |
| | **1.2 Segunda Instância** | 1.2.1 Interposição de Recurso |
| | | 1.2.2 Contrarrazões |
| | | 1.2.3 Processamento no Tribunal |
| | | 1.2.4 Julgamento (Acórdão) |
| | **1.3 Instâncias Superiores** | 1.3.1 STJ (REsp, AREsp) |
| | | 1.3.2 STF (RE, ARE) |
| | | 1.3.3 Sobrestamento por Repercussão Geral/Repetitivos |
| **2. TRÂNSITO EM JULGADO** | **2.1 Certificação** | 2.1.1 Aguardando Prazo Recursal |
| | | 2.1.2 Certidão de Trânsito em Julgado |
| **3. FASE SATISFATIVA** | **3.1 Cumprimento de Sentença** | 3.1.1 Liquidação (se necessário) |
| | | 3.1.2 Intimação para Cumprimento |
| | | 3.1.3 Impugnação ao Cumprimento |
| | | 3.1.4 Precatório/RPV (contra Fazenda) |
| | | 3.1.5 Satisfação da Obrigação |
| | **3.2 Execução (Título Extrajudicial)** | 3.2.1 Citação do Executado |
| | | 3.2.2 Penhora/Garantia do Juízo |
| | | 3.2.3 Embargos à Execução |
| | | 3.2.4 Expropriação/Satisfação |
| **4. ARQUIVAMENTO** | **4.1 Baixa Definitiva** | 4.1.1 Arquivamento Definitivo |
| | | 4.1.2 Arquivamento Provisório (Exec. Fiscal) |

---

## 3. Mapeamento de Classes Processuais (CNJ)

As classes processuais do CNJ indicam o tipo de procedimento e são fundamentais para determinar a sequência esperada de fases. A tabela abaixo apresenta as principais classes de interesse da PGM-Rio.

### 3.1 Classes Prioritárias - Fazenda Pública como Ré

| Código | Classe Processual | Fases Aplicáveis |
|--------|-------------------|------------------|
| 7 | Procedimento Comum Cível | Postulatória → Defesa → Réplica → Saneamento → Instrução → Sentença → Recursos → Cumprimento |
| 120 | Mandado de Segurança Cível | Petição Inicial → Notificação → Informações → Parecer MP → Sentença → Recursos |
| 65 | Ação Civil Pública | Postulatória → Defesa → Instrução → Sentença → Recursos → Cumprimento |
| 1707 | Procedimento do Juizado Especial Cível | Petição → Audiência de Conciliação → Instrução → Sentença → Turma Recursal |
| 12078 | Cumprimento de Sentença contra Fazenda | Intimação → Impugnação → Decisão → Precatório/RPV → Satisfação |

### 3.2 Classes Prioritárias - Fazenda Pública como Autora

| Código | Classe Processual | Fases Aplicáveis |
|--------|-------------------|------------------|
| 1116 | Execução Fiscal | Distribuição → Citação → Penhora → Embargos → Instrução → Sentença Embargos → Expropriação → Satisfação |
| 156 | Cumprimento de Sentença | Requerimento → Intimação → Impugnação → Decisão → Expropriação → Satisfação |
| 159 | Ação de Cobrança | Postulatória → Defesa → Instrução → Sentença → Recursos → Cumprimento |

---

## 4. Mapeamento de Movimentos Processuais (CNJ)

Os movimentos processuais são os gatilhos para transição entre fases. A estrutura hierárquica do CNJ divide os movimentos em categorias por autor do ato (Magistrado/Serventuário) e natureza (Decisão/Despacho/Julgamento).

### 4.1 Movimentos de Transição de Fase - Categoria Magistrado

#### 4.1.1 Hierarquia: Despacho (Código CNJ: 11009)

| Código | Movimento | Transição de Fase | Observação |
|--------|-----------|-------------------|------------|
| 11010 | Despacho de Mero Expediente | Não altera fase | Apenas impulsiona |
| 15216 | Determinação de Citação | Postulatória → Defesa | Marco inicial do prazo |
| 60 | Expedição de Documento | Varia conforme complemento | Verificar tipo_documento |

#### 4.1.2 Hierarquia: Decisão (Código CNJ: 3)

| Código | Movimento | Transição de Fase | Observação |
|--------|-----------|-------------------|------------|
| 11 | Deferida Tutela de Urgência/Evidência | Não altera fase principal | Gera subfase de cumprimento |
| 25 | Saneador | Defesa → Instrução | Define pontos controvertidos |
| 12197 | Conversão em Diligência | Suspende fase atual | Aguarda cumprimento |

#### 4.1.3 Hierarquia: Julgamento (Código CNJ: 193)

| Código | Movimento | Transição de Fase | Observação |
|--------|-----------|-------------------|------------|
| 22 | Baixa Definitiva | Qualquer → Arquivamento | Encerra tramitação |
| 198 | Julgamento - Procedente | Instrução → Decisória | Requer complemento resultado |
| 200 | Julgamento - Improcedente | Instrução → Decisória | Requer complemento resultado |
| 219 | Julgamento Sem Resolução de Mérito | Qualquer → Extinção | Art. 485 CPC |
| 848 | Trânsito em Julgado | Cognitiva → Transitada | Habilita fase satisfativa |
| 246 | Proferida Sentença | Instrução → Decisória | Verificar tipo sentença |

### 4.2 Movimentos de Transição - Categoria Serventuário

| Código | Movimento | Transição de Fase | Observação |
|--------|-----------|-------------------|------------|
| 26 | Distribuído | Início → Postulatória | Marco inicial |
| 85 | Juntada de Petição | Varia conforme tipo_petição | Verificar complemento |
| 12177 | Juntada de Contestação | Defesa → Réplica/Saneamento | Inicia prazo de réplica |
| 970 | Remessa ao Tribunal | 1ª Instância → 2ª Instância | Subida de recurso |
| 123 | Citação Realizada | Postulatória → Defesa | Inicia prazo de contestação |
| 60303 | Retorno dos Autos | 2ª Instância → 1ª Instância | Baixa do recurso |

---

## 5. Mapeamento de Documentos Processuais (CNJ)

Os documentos processuais complementam a identificação da fase, especialmente quando associados a movimentos genéricos como "Juntada de Petição". A Resolução CNJ 326/2020 padronizou a tabela de documentos.

### 5.1 Documentos que Indicam Transição de Fase

| Código | Tipo de Documento | Indica Fase | Prazo PGM |
|--------|-------------------|-------------|-----------|
| 60 | Petição Inicial | Postulatória | - |
| 50 | Contestação | Defesa realizada | 30 dias (Fazenda) |
| 80 | Sentença | Decisória (1ª Instância) | Recurso: 30 dias |
| 81 | Acórdão | Decisória (2ª Instância) | REsp/RE: 30 dias |
| 7 | Apelação | Recursal | Contrarrazões: 30 dias |
| 67 | Recurso Especial | Instâncias Superiores | Contrarrazões: 30 dias |
| 66 | Recurso Extraordinário | Instâncias Superiores | Contrarrazões: 30 dias |
| 56 | Embargos à Execução | Fase Satisfativa - Defesa | 30 dias |
| 59 | Impugnação ao Cumprimento | Fase Satisfativa - Defesa | 30 dias (Fazenda) |

---

## 6. Regras de Transição entre Fases

As regras de transição definem a lógica para identificação automática da fase processual com base nos eventos recebidos via MNI. O sistema deve aplicar estas regras em ordem de prioridade.

### 6.1 Algoritmo de Classificação

1. Identificar a **Classe Processual** (determina o fluxo base)
2. Verificar último **Movimento** relevante (gatilho de transição)
3. Analisar **Complementos do Movimento** (especifica o contexto)
4. Verificar **Documentos Juntados** (confirma/ajusta a fase)
5. Aplicar regras de **Instância** (1ª, 2ª, Superiores)

### 6.2 Matriz de Transição - Procedimento Comum (Fazenda Ré)

| Fase Atual | Evento Gatilho | Próxima Fase |
|------------|----------------|--------------|
| 1.1.1 Postulatória | Citação Realizada (123) | 1.1.2 Defesa - Aguardando Contestação |
| 1.1.2 Defesa | Juntada Contestação (12177) | 1.1.3 Réplica - Aguardando Réplica |
| 1.1.3 Réplica | Despacho Saneador (25) | 1.1.4 Saneamento - Pontos Controvertidos |
| 1.1.4 Saneamento | Designação Perícia/Audiência | 1.1.5 Instrução |
| 1.1.5 Instrução | Sentença Proferida (246) | 1.1.6 Decisória - Aguardando Prazo Recursal |
| 1.1.6 Decisória | Remessa ao Tribunal (970) | 1.2.1 Segunda Instância - Recurso Interposto |
| 1.1.6 Decisória | Trânsito em Julgado (848) | 2.1 Trânsito em Julgado |

### 6.3 Matriz de Transição - Execução Fiscal (Fazenda Autora)

| Fase Atual | Evento Gatilho | Próxima Fase |
|------------|----------------|--------------|
| 3.2.1 Citação | Citação Realizada (123) | 3.2.2 Aguardando Pagamento/Penhora |
| 3.2.2 Penhora | Penhora Realizada | 3.2.3 Aguardando Embargos |
| 3.2.3 Embargos | Juntada Embargos (Doc 56) | 3.2.3 Embargos - Em Instrução |
| 3.2.3 Embargos | Sentença Embargos (246) | 3.2.4 Expropriação (se improcedente) |
| 3.2.4 Expropriação | Satisfação Integral | 4.1.1 Arquivamento Definitivo |
| 3.2.2 Penhora | Não localizado devedor/bens | 4.1.2 Arquivamento Provisório (Art. 40 LEF) |

---

## 7. Aplicações Práticas do Sistema de Fases

### 7.1 Gestão de Prazos e Alertas

O sistema de fases permite configurar alertas específicos conforme a posição do processo na tramitação:

| Fase | Prazo de Alerta | Ação Esperada |
|------|----------------|---------------|
| Defesa (Fazenda Ré) | 25º dia útil após citação | Elaborar Contestação |
| Decisória - Pós-Sentença | 20º dia útil após intimação | Avaliar interposição de recurso |
| Contrarrazões (Fazenda) | 25º dia útil após intimação | Elaborar contrarrazões |
| Cumprimento de Sentença | 25º dia útil após intimação | Impugnar ou cumprir |
| Exec. Fiscal - Citação | 90 dias sem citação | Requerer citação por edital |

### 7.2 Dashboards Gerenciais

Indicadores sugeridos para painel de acompanhamento:

- **Volume por Fase**: Quantitativo de processos em cada fase macro
- **Tempo Médio por Fase**: Duração média em cada estágio processual
- **Taxa de Sucesso**: Percentual de êxito por tipo de fase decisória
- **Prazos Vencendo**: Processos com prazo crítico próximo
- **Distribuição por Instância**: Visão do acervo em 1ª, 2ª e instâncias superiores

### 7.3 Triagem e Distribuição Automática

Regras de encaminhamento baseadas na fase processual:

- **Fase Postulatória**: Encaminhar para equipe de análise de inicial
- **Fase Defesa**: Distribuir para procurador responsável pela matéria
- **Fase Recursal**: Encaminhar para equipe especializada em recursos
- **Fase Satisfativa**: Direcionar para equipe de cumprimento/precatórios

### 7.4 Alimentação de Modelos de IA

A fase processual fornece contexto essencial para geração automatizada de minutas:

- **Seleção de Templates**: Carregar modelo adequado à fase (contestação, recurso, etc.)
- **Contexto para RAG**: Filtrar jurisprudência relevante ao estágio processual
- **Prompts Especializados**: Ajustar instruções ao tipo de peça esperada
- **Validação de Saída**: Verificar se peça gerada é compatível com a fase

---

## 8. Considerações para Implementação

### 8.1 Integração MNI/DEJT

A Resolução CNJ 455/2022 estabelece o Domicílio Eletrônico Judicial como canal oficial de comunicação. O sistema deve:

- Consumir eventos do MNI em tempo real ou por polling periódico
- Processar os XMLs de movimentação conforme padrão DataJud
- Extrair códigos de Classes, Movimentos e Documentos
- Aplicar as regras de transição para classificar a fase
- Registrar histórico de transições para auditoria

### 8.2 Tratamento de Casos Especiais

- **Movimentos sem código CNJ**: Manter fase atual, alertar para revisão manual
- **Múltiplos movimentos simultâneos**: Priorizar movimento de maior impacto (ex: sentença > despacho)
- **Retorno de fase**: Permitir regressão quando houver anulação de ato
- **Sobrestamento**: Criar subfase paralela sem alterar fase principal

### 8.3 Manutenção das Tabelas

O CNJ atualiza periodicamente as Tabelas Processuais Unificadas. Recomenda-se:

- Monitorar boletins de atualização do CNJ (publicados no portal)
- Implementar mecanismo de importação das tabelas atualizadas
- Validar impacto de novos códigos nas regras de transição
- Versionar as regras para permitir auditoria retroativa

---

## 9. Próximos Passos

- [ ] **Validação com Procuradores**: Apresentar estrutura para validação das equipes de contencioso
- [ ] **Mapeamento Completo de Movimentos**: Expandir a tabela com todos os códigos relevantes à PGM
- [ ] **Prototipação**: Desenvolver MVP com amostra de processos reais
- [ ] **Integração com Sistema Atual**: Definir pontos de integração com PA Virtual
- [ ] **Testes e Ajustes**: Validar regras de transição com casos históricos
- [ ] **Capacitação**: Treinar equipes no uso do sistema de fases

---

## Document Control

| Atributo | Valor |
|----------|-------|
| **Versão** | 1.0 |
| **Data** | Janeiro de 2026 |
| **Autor** | Coordenação de Tecnologia da PGM-Rio |
| **Status** | Draft |
| **Última Atualização** | 2026-02-06 |

---

*Documento elaborado pela Coordenação de Tecnologia da PGM-Rio*  
*Janeiro de 2026*
