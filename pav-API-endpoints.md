# API Endpoints — PAV (pav.procuradoria.rio)

> Base URL: `https://pav.procuradoria.rio/`
> Autenticação: Sessão via cookie (login no portal `/portal/action/Login/view/normal`)

---

## 1. Dados do Processo (consulta rápida)

### Dados gerais do processo (PAV)

```
GET /services/custom-consulta-rapida-de-procesos/dados-da-consulta/{neoId}
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `neoId` | path | ID interno do processo no PAV |

**Retorno:** Dados completos do processo — partes, advogados, assuntos, PAV, movimentações, etc.

**Erros:**
- `403` → sessão expirada, o sistema faz logout automático

---

## 2. Árvore de Documentos

### Montar árvore de documentos por sistema/tribunal ⭐ **(principal)**

```
GET /services/arquivos/arvore-processo-by-sistema/{numeroJudicial}
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `numeroJudicial` | path | Número CNJ do processo (ex: `0895829-30.2024.8.19.0001`) |

**Retorno:**

```json
{
  "precisaSincronizar": false,
  "processo": {
    "sucesso": true,
    "ultimaAtualizacao": "2025-11-30T11:01:14.141Z",
    "numeroJudicial": "08958293020248190001"
  },
  "tribunal": [
    {
      "codigo": "8",
      "destino": "TJRJ - PJE",
      "descricaoSistema": "TJRJ - PJE",
      "id": "uuid-do-tribunal",
      "classeProcessual": "",
      "numeroClasseProcessual": "",
      "documentos": [
        {
          "id": "136637434",
          "tipo": "30009",
          "nomeArquivo": "Despacho",
          "dataAutuacao": "12/08/2024 17:48:32",
          "numeroProcesso": "08958293020248190001",
          "numeroFolha": "0",
          "idDocumentoVinculado": "0"
        }
      ]
    }
  ]
}
```

**Destinos possíveis observados:**
- `TJRJ - DCP` — DCP (ordenação por folha)
- `TJRJ - PJE` — PJe TJRJ (ordenação por ID)
- `TJRJ - EPROC - 1TH` — eProc Primeira Instância
- `TJRJ - EPROC - 2TH` — eProc Segunda Instância
- `STJ - CPE` — STJ (ordenação por ID)
- `STF - PJE` — STF (ordenação por ID)
- `TRT - 1TH` / `TRT - 2TH` — TRT
- `TRF2 - EPROC - 1TH` / `TRF2 - EPROC - 2TH` — TRF2

**Observação:** Quando `precisaSincronizar === true`, o sistema chama automaticamente o endpoint de sincronização.

---

## 3. Sincronização de Autos

### Sincronizar autos com o tribunal

```
GET /services/arquivos/atualiza-processo-tribunal/{numeroJudicial}
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `numeroJudicial` | path | Número CNJ do processo |

**Retorno:**

```json
{
  "processo": {
    "sucesso": true,
    "ultimaAtualizacao": "...",
    "numeroJudicial": "..."
  },
  "documentos": [ /* novos documentos adicionados */ ]
}
```

**Em caso de erro:**
```json
{ "status": "error" }
```

---

### Baixar todos os documentos em background (async)

```
GET /services/arquivos/sincronizarAutos/{numeroJudicial}
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `numeroJudicial` | path | Número CNJ do processo |

> Chamado automaticamente após a sincronização. Não bloqueia a interface.

---

## 4. Documentos Individuais

### Buscar documento por ID (retorna base64)

```
GET /services/arquivos/get-documento-by-numero-judicial-and-id-documento/{idDocumento}/{numeroJudicial}
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `idDocumento` | path | ID do documento (campo `id` da árvore) |
| `numeroJudicial` | path | Número CNJ do processo |

**Retorno:**

```json
{
  "base64encode": "JVBERi0x...",
  "contentType": "application/pdf",
  "ext": ".pdf"
}
```

**Em caso de erro:**
```json
{ "error": { "errorMessage": "Mensagem de erro" } }
```

---

## 5. Configuração do Micro Serviço

### Obter URL do micro serviço de autos

```
GET /services/arquivos/get-url-micro-servico-autos
```

**Retorno:**

```json
{
  "urlMicroServicoAutos": "https://...",
  "idUsuario": 682586085,
  "urlMiddlewareConversor": "https://..."
}
```

**Erros:**
- `401` → usuário deslogado
- `500` → erro interno

> Usado para estabelecer a conexão SSE:
> `GET {urlMicroServicoAutos}/sse/busca-documento-tribunal`

---

## 6. Processos Incidentes

### Listar processos incidentes vinculados

```
GET /services/arquivos/loadingIncident?processo={neoId}
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `processo` | query | `neoId` do processo PAV |

**Retorno:** Array de processos incidentes.

```json
[
  {
    "classeProcessual": "Agravo de Instrumento",
    "numeroJudicial": "0012345-...",
    "numeroProcesso": "00123/2025",
    "neoId": "..."
  }
]
```

---

## 7. Download e Visualização

### Download de seleção de documentos (ZIP)

```
POST /services/arquivos/busca-arvore-documento-processo-download/{numeroJudicialId}/{uuid}
Content-Type: application/json

[/* array de IDs de documentos */]
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `numeroJudicialId` | path | Número CNJ do processo |
| `uuid` | path | UUID do tribunal (campo `id` do objeto tribunal na árvore) |
| body | array | Array com os documentos selecionados |

---

### Visualização de seleção de documentos

```
POST /services/arquivos/busca-arvore-documento-processo-visualizar/{numeroJudicialId}/{uuid}
Content-Type: application/json

[/* array de IDs de documentos */]
```

Mesma assinatura do endpoint de download, retorna conteúdo para visualização.

---

## 8. Upload e Conversão

### Upload de peça para o PAV

```
POST /services/arquivos/uploadFile/
Content-Type: application/json

{
  "base64file": "JVBERi0x...",
  "fileName": "nome-do-arquivo"
}
```

**Retorno:** ID do arquivo no PAV (neoId).

---

### Converter documento para PDF

```
POST /services/arquivos/conversor-from-any-base64-to-base64-pdf
Content-Type: application/json

{
  "base64": "...",
  "extension": ".docx"
}
```

**Retorno:**

```json
{
  "base64": "JVBERi0x...",
  "ext": ".pdf",
  "contentType": "application/pdf"
}
```

---

## 9. Prazos Judiciais

### Calcular data de prazo judicial

```
GET /services/prazos-judiciais-compromissos/get-judicial-deadline-date/
  ?initialDate={data}
  &daysOrHours={days|hours}
  &amount={quantidade}
  &courtCode={codigo|null}
  &isWorkingDaysOnly={true|false}
```

**Retorno:**

```json
{ "date": "25/03/2025 10:30" }
```

---

### Salvar liminar / prazo sensível

```
POST /services/prazos-judiciais-compromissos/save-liminar/
Content-Type: application/json

{
  "params": {
    "possuiLiminar": 1,
    "dataIntimacao": "20/03/2025 10:00",
    "quantidade": 15,
    "tipoDePrazo": 1,
    "dataDoPrazo": "04/04/2025 10:00",
    "observacao": "...",
    "itemNeoId": "..."
  }
}
```

---

## 10. Outros Endpoints Auxiliares

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `services/arquivos/atualiza-processo-tribunal/{numeroJudicial}` | Sincroniza autos com tribunal |
| `GET` | `services/leitura/iniciarNovoPAV?neoIdItem={id}&especializada={cod}&neoIdModelo={id}` | Inicia novo PAV a partir de intimação |
| `GET` | `services/intimacao/updateItem/null/{neoIdDoItem}` | Atualiza status de item de intimação |
| `GET` | `services/acaojudicial/modeloacao/getNewActionModels` | Carrega modelos de ação (PUMA, PSE, PDA, PPE) |
| `GET` | `servlet/DOItemAprovacaoServlet?novaFuncao=true&aprovar={bool}&entityId={id}` | Aprova/reprova item de intimação |

---

## Fluxo de inicialização da tela de Autos

```
1. GET /services/arquivos/get-url-micro-servico-autos
        ↓ retorna urlMicroServicoAutos
2. SSE  {urlMicroServicoAutos}/sse/busca-documento-tribunal
        ↓ abre stream de eventos (progresso de busca no tribunal)
3. GET  /services/arquivos/arvore-processo-by-sistema/{numeroJudicial}
        ↓ retorna árvore completa de documentos
        ↓ se precisaSincronizar === true → chama atualiza-processo-tribunal
4. Ao clicar em documento:
   GET  /services/arquivos/get-documento-by-numero-judicial-and-id-documento/{id}/{numeroJudicial}
        ↓ retorna base64 do arquivo para renderização no iframe
```

---

## Estrutura do documento na árvore

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | string | ID único do documento no tribunal |
| `tipo` | string | Código do tipo do documento |
| `nomeArquivo` | string | Nome legível do documento |
| `dataAutuacao` | string | Data/hora de autuação (`dd/MM/yyyy HH:mm:ss`) |
| `numeroProcesso` | string | Número do processo sem formatação |
| `numeroFolha` | string | Número da folha (DCP) ou `"0"` (PJe) |
| `idDocumentoVinculado` | string | ID do documento pai (se for anexo), ou `"0"` |
