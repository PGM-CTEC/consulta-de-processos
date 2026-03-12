# Estrutura do JSON — API PAV Fusion
## Endpoint: `/services/custom-consulta-rapida-de-procesos/dados-da-consulta/{numero}`

**Data:** 2026-03-12
**Versão:** 1.0
**Fonte:** API PAV Fusion (Procuradoria-Geral da República — Rio de Janeiro)

---

## 📋 Visão Geral

A API PAV Fusion retorna um JSON **consolidado** contendo informações do processo judicial brasileiro, incluindo:
- Dados administrativos do tribunal (PAV)
- Dados processuais gerais
- Lista completa de partes (atores)
- Movimentos processuais com timestamps
- Assuntos e tópicos do processo
- Recursos processuais (Apelação, Recurso Extraordinário, etc.)
- Informações adicionais

**Nota:** O JSON combina dados do sistema PAV central COM informações obtidas dos Mini-Sistemas (MINIs) dos tribunais estaduais/federais.

---

## 🏗️ Estrutura Raiz

```json
{
  "dadosPAV": { ... },
  "dadosGerais": { ... },
  "partes": [ ... ],
  "movimentos": [ ... ],
  "assuntos": [ ... ],
  "recursos": [ ... ],
  "outrasInformacoes": { ... }
}
```

---

## 1️⃣ Seção: `dadosPAV`

Informações administrativas do PAV (sistema central de controle processos).

```json
{
  "dadosPAV": {
    "situacao": "string",                    // Ex: "Processando", "Arquivado", "Baixado"
    "localizacaoCorrente": "string",         // Ex: "Tribunal de Justiça do RJ"
    "procuradorResponsavel": "string",       // Ex: "João Silva - OAB/RJ 123456"
    "dataAtualizacao": "YYYY-MM-DDTHH:MM:SSZ",
    "sistemaOrigem": "string",               // Ex: "MINI-TJRJ", "MINI-TRF2"
    "dataInclusaoPAV": "YYYY-MM-DDTHH:MM:SSZ"
  }
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `situacao` | string | Sim | Status processual atual (ex: Processando, Baixado, Arquivado) |
| `localizacaoCorrente` | string | Sim | Órgão/tribunal onde processo está atualmente |
| `procuradorResponsavel` | string | Não | Procurador ou responsável pela acompanhamento |
| `dataAtualizacao` | ISO8601 | Sim | Data-hora da última atualização no PAV |
| `sistemaOrigem` | string | Sim | MINI/Sistema de origem (TJSP, TRF2, STJ, STF, etc.) |
| `dataInclusaoPAV` | ISO8601 | Não | Data de inclusão do processo no PAV central |

**Exemplo Real:**
```json
{
  "situacao": "Processando",
  "localizacaoCorrente": "Câmara Cível - TJRJ",
  "procuradorResponsavel": "Maria Santos - OAB/RJ 654321",
  "dataAtualizacao": "2025-08-15T14:32:10Z",
  "sistemaOrigem": "MINI-TJRJ",
  "dataInclusaoPAV": "2016-02-29T16:02:00Z"
}
```

---

## 2️⃣ Seção: `dadosGerais`

Informações processuais fundamentais (compatível com CNJ).

```json
{
  "dadosGerais": {
    "numeroJudicial": "string",              // Ex: "0064567-76.2016.8.19.0001" (formatado) ou "00645677620168190001" (puro)
    "numeroDossie": "string",                // Número interno do tribunal
    "classeProcessual": "string",            // Ex: "Apelação Cível", "Ação de Cobrança"
    "codigoClasse": "string",                // Código CNJ da classe (ex: "4001")
    "assuntoProcessual": "string",           // Assunto principal
    "dataAjuizamento": "DD/MM/YYYY HH:MM",   // Data da distribuição
    "orgaoJulgador": "string",               // Ex: "18ª CÂMARA CÍVEL" ou "Vara de Execuções"
    "grau": "string",                        // Ex: "G1" (1º grau), "G2" (2º grau), "G3" (STJ), "G4" (STF)
    "juiz": "string",                        // Nome do juiz/desembargador
    "tribunal": "string",                    // Sigla tribunal (TJRJ, TJSP, TRF2, etc.)
    "instancia": "string",                   // Ex: "Primeira Instância", "Segunda Instância"
    "dataDistribuicao": "DD/MM/YYYY HH:MM",
    "dataAtualizacao": "YYYY-MM-DDTHH:MM:SSZ",
    "statusProcesso": "string"               // Ex: "Ativo", "Baixado", "Suspenso"
  }
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `numeroJudicial` | string | **SIM** | Número CNJ do processo (PK de busca) |
| `numeroDossie` | string | Não | ID interno do tribunal |
| `classeProcessual` | string | **SIM** | Tipo de ação (ex: Apelação, Execução, etc.) |
| `codigoClasse` | string | Não | Código numérico CNJ |
| `assuntoProcessual` | string | Sim | Assunto principal |
| `dataAjuizamento` | string | Sim | Data da distribuição do processo |
| `orgaoJulgador` | string | **SIM** | Vara/Câmara (ex: "18ª CÂMARA CÍVEL") — **USAR PARA UI** |
| `grau` | string | Sim | Nível hierárquico (G1/G2/G3/G4) |
| `juiz` | string | Não | Nome do magistrado |
| `tribunal` | string | Sim | Sigla tribunal (TJRJ, TJSP, etc.) |
| `instancia` | string | Não | Descrição textual da instância |
| `dataDistribuicao` | string | Sim | Data da distribuição |
| `dataAtualizacao` | ISO8601 | Sim | Última atualização |
| `statusProcesso` | string | Sim | Status geral (Ativo/Baixado/Suspenso) |

**Exemplo Real:**
```json
{
  "numeroJudicial": "0064567-76.2016.8.19.0001",
  "numeroDossie": "2016.076549",
  "classeProcessual": "Apelação Cível",
  "codigoClasse": "4001",
  "assuntoProcessual": "Mandado de Segurança",
  "dataAjuizamento": "10/07/2025 18:03",
  "orgaoJulgador": "SEGUNDA CÂMARA DE DIREITO PÚBLICO (ANTIGA 10ª CÂMARA CÍVEL)",
  "grau": "G2",
  "juiz": "Des. João Pereira Silva",
  "tribunal": "TJRJ",
  "instancia": "Segunda Instância",
  "dataDistribuicao": "29/02/2016 16:02",
  "dataAtualizacao": "2025-08-15T14:32:10Z",
  "statusProcesso": "Ativo"
}
```

**⚠️ IMPORTANTE — Órgão Judicial:**
- **Campo recomendado para UI:** `dadosGerais.orgaoJulgador`
- **NÃO usar:** campos antigos de DataJud
- **Contém:** Nome completo da vara/câmara conforme tribunal

---

## 3️⃣ Seção: `partes`

Lista de atores no processo (autor, réu, terceiros, intervenientes).

```json
{
  "partes": [
    {
      "nome": "string",                      // Nome completo
      "tipoPolo": "string",                  // "Autor", "Réu", "Interveniente", "Terceiro"
      "tipoAtor": "string",                  // "Pessoa Física", "Pessoa Jurídica", "Órgão Público"
      "documento": "string",                 // CPF ou CNPJ
      "qualificacao": "string",              // Ex: "Advogado", "Preposto", "Procurador"
      "nomeProfissional": "string",          // Ex: "OAB/RJ 123456"
      "endereco": "string",                  // Endereço completo
      "email": "string",                     // Email do actor (se disponível)
      "telefone": "string"                   // Telefone de contato
    }
  ]
}
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `nome` | string | Nome completo da parte |
| `tipoPolo` | string | Posição no processo (Autor/Réu/Interveniente) |
| `tipoAtor` | string | Classificação (Pessoa Física/Jurídica/Órgão Público) |
| `documento` | string | CPF/CNPJ (sem formatação ou formatado) |
| `qualificacao` | string | Papel da parte (Advogado, Procurador, etc.) |
| `nomeProfissional` | string | Identificação profissional (OAB, registro público) |
| `endereco` | string | Endereço completo ou CEP |
| `email` | string | Email de contato |
| `telefone` | string | Telefone com DDD |

**Exemplo Real:**
```json
{
  "partes": [
    {
      "nome": "MUNICÍPIO DO RIO DE JANEIRO",
      "tipoPolo": "Autor",
      "tipoAtor": "Órgão Público",
      "documento": "00000000000191",
      "qualificacao": "Procurador",
      "nomeProfissional": "Procuradoria-Geral do Município",
      "endereco": "Av. Presidente Wilson, 165 - Rio de Janeiro/RJ",
      "email": "pgm@rio.rj.gov.br",
      "telefone": "(21) 2976-6000"
    },
    {
      "nome": "HUGO PEREIRA FIBEIRO GERALDO",
      "tipoPolo": "Réu",
      "tipoAtor": "Pessoa Física",
      "documento": "12345678900",
      "qualificacao": "Advogado",
      "nomeProfissional": "OAB/RJ 123456",
      "endereco": "Rua das Flores, 456 - Rio de Janeiro/RJ",
      "email": "hugo@email.com",
      "telefone": "(21) 9999-8888"
    }
  ]
}
```

---

## 4️⃣ Seção: `movimentos`

Histórico cronológico de movimentos/eventos processuais.

```json
{
  "movimentos": [
    {
      "dataDoMovimento": "DD/MM/YYYY HH:MM" ou "DD/MM/YYYY HH:MM:SS",
      "descricao": "string",                 // Descrição textual do movimento
      "tipoMovimentoCNJ": "string",          // Ex: "Recebimento", "Distribuição", "Sentença"
      "tipoMovimentoLocal": "string",        // Nomenclatura do tribunal
      "codigoMovimento": "string",           // Código único do movimento
      "documentos": [                        // Documentos anexados
        {
          "id": "string",
          "nome": "string",
          "tipo": "string",                  // "PDF", "Imagem", "Texto"
          "dataInclusao": "YYYY-MM-DDTHH:MM:SSZ",
          "url": "string"                    // URL para download
        }
      ],
      "complemento": "string",               // Informações adicionais
      "usuario": "string"                    // Usuário que registrou o movimento
    }
  ]
}
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `dataDoMovimento` | string | Data-hora do evento (formato PT ou com segundos) |
| `descricao` | string | Descrição completa do que ocorreu |
| `tipoMovimentoCNJ` | string | Classificação CNJ padronizada |
| `tipoMovimentoLocal` | string | Nomenclatura local do tribunal |
| `codigoMovimento` | string | ID único para rastreamento |
| `documentos` | array | Arquivos anexados (autos, despachos, sentença) |
| `complemento` | string | Detalhes adicionais |
| `usuario` | string | Quem registrou no sistema |

**Exemplo Real:**
```json
{
  "movimentos": [
    {
      "dataDoMovimento": "29/02/2016 16:02",
      "descricao": "Distribuição do processo",
      "tipoMovimentoCNJ": "Distribuição",
      "tipoMovimentoLocal": "Distribuição da Ação",
      "codigoMovimento": "MOV001",
      "documentos": [
        {
          "id": "DOC001",
          "nome": "Petição Inicial",
          "tipo": "PDF",
          "dataInclusao": "2016-02-29T16:02:00Z",
          "url": "https://pav.procuradoria.rio/docs/DOC001"
        }
      ],
      "complemento": "Distribuída à 18ª Câmara",
      "usuario": "sistema"
    },
    {
      "dataDoMovimento": "15/08/2025 14:32",
      "descricao": "Remessa dos autos a apelante",
      "tipoMovimentoCNJ": "Remessa",
      "tipoMovimentoLocal": "Remessa sem Sentença",
      "codigoMovimento": "MOV087",
      "documentos": [],
      "complemento": "Conforme despacho de 14/08/2025",
      "usuario": "sistema"
    }
  ]
}
```

---

## 5️⃣ Seção: `assuntos`

Tópicos e matérias do processo (para indexação e classificação).

```json
{
  "assuntos": [
    {
      "nome": "string",                      // Ex: "Mandado de Segurança", "Direito Administrativo"
      "codigo": "string",                    // Código CNJ
      "principal": boolean                   // true se é assunto principal
    }
  ]
}
```

**Exemplo Real:**
```json
{
  "assuntos": [
    {
      "nome": "Mandado de Segurança",
      "codigo": "2501",
      "principal": true
    },
    {
      "nome": "Direito Administrativo",
      "codigo": "1200",
      "principal": false
    }
  ]
}
```

---

## 6️⃣ Seção: `recursos`

Recursos processuais interpostos (Apelação, Embargo, Recurso Extraordinário).

```json
{
  "recursos": [
    {
      "tipoRecurso": "string",               // Ex: "Apelação", "Recurso Ordinário"
      "data": "DD/MM/YYYY",
      "status": "string",                    // "Admitido", "Negado", "Pendente"
      "tribunal": "string",                  // Tribunal para o qual foi encaminhado
      "numeroProcesso": "string"             // Número do processo de recurso
    }
  ]
}
```

**Exemplo Real:**
```json
{
  "recursos": [
    {
      "tipoRecurso": "Apelação",
      "data": "15/03/2016",
      "status": "Admitido",
      "tribunal": "Tribunal de Justiça do RJ",
      "numeroProcesso": "APL-0064567-76.2016.8.19.0001"
    }
  ]
}
```

---

## 7️⃣ Seção: `outrasInformacoes`

Dados complementares não categorizados.

```json
{
  "outrasInformacoes": {
    "descricaoCompleta": "string",           // Resumo do caso
    "valorCausa": "number",                  // Valor em reais (se houver)
    "dataProximoEvento": "DD/MM/YYYY",       // Próxima audiência/evento
    "localProximoEvento": "string",
    "advogados": [                           // Lista de advogados (alternativa)
      {
        "nome": "string",
        "oab": "string",
        "email": "string"
      }
    ],
    "tags": ["string"]                       // Tags/etiquetas para classificação
  }
}
```

---

## 🔍 Campos Críticos para a UI

| Uso | Campo Recomendado | Alternativa | Notas |
|-----|-------------------|-------------|-------|
| **Número processo** | `dadosGerais.numeroJudicial` | N/A | Sempre usar este campo |
| **Órgão/Vara** | `dadosGerais.orgaoJulgador` | `dadosPAV.localizacaoCorrente` | ⚠️ **NOVO — PAV, não DataJud** |
| **Fase processual** | Extrair de `movimentos` | DocumentPhaseClassifier | Usar últimos 5 movimentos |
| **Partes (Autor/Réu)** | `partes` (filtrar por tipoPolo) | N/A | Usar `nome` + `qualificacao` |
| **Última atualização** | `dadosGerais.dataAtualizacao` ou `dadosPAV.dataAtualizacao` | N/A | Usar timestamp mais recente |
| **Status** | `dadosPAV.situacao` ou `dadosGerais.statusProcesso` | N/A | Indicador de processamento |

---

## ⚙️ Notas Técnicas

### Encoding
- **Padrão:** UTF-8 com `ensure_ascii=False`
- **Caracteres:** Suporta acentos e caracteres especiais (ç, ã, é, etc.)

### Datas
- **Formato dadosGerais:** `DD/MM/YYYY HH:MM` ou `DD/MM/YYYY HH:MM:SS`
- **Formato ISO (PAV):** `YYYY-MM-DDTHH:MM:SSZ`
- **Parser:** Suporta ambos os formatos

### Nulabilidade
- Campos com `null` devem ser tratados como "N/A"
- Arrays vazios `[]` significam "sem dados disponíveis"
- Strings vazias `""` devem ser exibidas como "-" ou "N/A"

### Performance
- Endpoint é **sincrônico** — timeout recomendado: **15 segundos**
- JSON pode ter **100+ movimentos** — considerar paginação no frontend
- Documentos anexados podem ser **pesados** — lazy-load recomendado

---

## 📝 Exemplos de Resposta Completa (Resumida)

```json
{
  "dadosPAV": {
    "situacao": "Processando",
    "localizacaoCorrente": "Câmara Cível - TJRJ",
    "procuradorResponsavel": "Maria Santos - OAB/RJ 654321",
    "dataAtualizacao": "2025-08-15T14:32:10Z",
    "sistemaOrigem": "MINI-TJRJ"
  },
  "dadosGerais": {
    "numeroJudicial": "0064567-76.2016.8.19.0001",
    "classeProcessual": "Apelação Cível",
    "orgaoJulgador": "SEGUNDA CÂMARA DE DIREITO PÚBLICO",
    "grau": "G2",
    "tribunal": "TJRJ",
    "dataAjuizamento": "10/07/2025 18:03",
    "dataAtualizacao": "2025-08-15T14:32:10Z"
  },
  "partes": [
    {
      "nome": "MUNICÍPIO DO RIO DE JANEIRO",
      "tipoPolo": "Autor",
      "tipoAtor": "Órgão Público"
    },
    {
      "nome": "HUGO PEREIRA FIBEIRO GERALDO",
      "tipoPolo": "Réu",
      "tipoAtor": "Pessoa Física"
    }
  ],
  "movimentos": [
    {
      "dataDoMovimento": "29/02/2016 16:02",
      "descricao": "Distribuição do processo",
      "tipoMovimentoCNJ": "Distribuição"
    },
    {
      "dataDoMovimento": "15/08/2025 14:32",
      "descricao": "Remessa dos autos",
      "tipoMovimentoCNJ": "Remessa"
    }
  ],
  "assuntos": [
    {
      "nome": "Mandado de Segurança",
      "principal": true
    }
  ],
  "recursos": [],
  "outrasInformacoes": {}
}
```

---

## 🐛 Troubleshooting

| Problema | Causa | Solução |
|----------|-------|--------|
| Órgão vazio na UI | `orgaoJulgador` é null | Usar `localizacaoCorrente` como fallback |
| Movimentos vazios | Processo sem eventos registrados | Verificar `statusProcesso`, talvez não foi distribuído |
| Partes duplicadas | Mesma parte com nomes ligeiramente diferentes | Normalizar nomes (trim, uppercase) |
| Datas inválidas | Formato não esperado | Suportar `DD/MM/YYYY`, `DD/MM/YYYY HH:MM`, `DD/MM/YYYY HH:MM:SS` |
| Timeout 504 | Processo muito grande (muitos documentos) | Implementar timeout maior ou paginação |

---

**Última Atualização:** 2026-03-12
**Mantido por:** Arquitetura PAV-Only
**Status:** Referência Oficial
