# Design: Integração Fusion/PAV — Consulta por Árvore de Documentos

**Data:** 2026-03-07
**Branch:** `completar-pesquisa-externa`
**Status:** Aprovado

---

## Contexto

A aplicação "Consulta de Processos" classifica fases processuais via API pública do DataJud/CNJ. Quando o DataJud **não retorna dados** (sem erro — apenas `not_found`), o processo não pode ser classificado. Este design descreve a integração com o sistema Fusion/PAV da PGM-Rio como **segunda fonte de classificação**, ativada apenas nesses casos.

---

## Fluxo de Decisão Geral

```
SearchProcess(número CNJ)
│
├─ 1. DataJud API (lógica existente — sem alteração)
│   ├─ Retornou dados  → Classificação por movimentações CNJ (15 fases) ✓
│   ├─ Erro (rede, formato, API) → Retorna erro normalmente ✓
│   └─ not_found (sem erro) → NOVO: ativa FusionService ↓
│
├─ 2. FusionService.get_document_tree(número CNJ)
│   ├─ Via A: SQL Server direto (se configurado e acessível)
│   └─ Via B: API REST do PAV (fallback)
│       └─ GET /services/custom-consulta-rapida-de-procesos/dados-da-consulta/{cnj}
│
└─ 3. DocumentPhaseClassifier.classify(movimentos, classe_processual)
    ├─ Analisa tipoMovimentoLocal em ordem cronológica
    ├─ Aplica âncoras de fase por classe processual
    └─ Retorna fase (mesmas 15 fases do sistema atual) + source='fusion'
```

---

## Endpoint Fusion Descoberto (Inspeção de Browser)

### API REST do PAV

```
GET https://pav.procuradoria.rio/services/custom-consulta-rapida-de-procesos/
    dados-da-consulta/{numero_cnj_sem_formatacao}
```

- **Autenticação:** Cookie de sessão do PAV (JSESSIONID)
- **Número CNJ:** sem formatação, apenas dígitos (ex: `00754816320208190001`)
- **Resposta JSON:**

```json
{
  "dadosPAV": {
    "neoId": 950453990,
    "wfProcessNeoId": 950453990,
    "situacao": "Ativo",
    ...
  },
  "dadosGerais": {
    "numeroJudicial": "00754816320208190001",
    "classeProcessual": "Cumprimento de sentença",
    "orgaoJulgador": "Cartório da 3ª Vara da Fazenda Pública",
    "descricaoSistema": "TJRJ_DCP",
    ...
  },
  "movimentos": [
    {
      "dataDoMovimento": "08/04/2020 15:59",
      "tipoMovimentoCNJ": "Distribuição",
      "tipoMovimentoLocal": "DISTRIBUIÇÃO Sorteio",
      "documentos": ["783447489", ...]
    },
    ...
  ],
  "urlConsultaAutos": "http://10.32.96.217:3004/TJRJ",
  "encontradoTribunal": true,
  "uuid": "46110a89-..."
}
```

**Campos chave para classificação:**
- `dadosGerais.classeProcessual` → contexto macro da fase
- `movimentos[].tipoMovimentoLocal` → "batismo" da peça (âncora de classificação)
- `movimentos[].dataDoMovimento` → ordenação cronológica
- `dadosPAV.wfProcessNeoId` → ID interno Fusion (para SQL direto)

### Middleware de Sincronização (referência futura)

```
http://10.32.96.217:3004/TJRJ/sse/busca-documento-tribunal
```
SSE para sincronização com tribunal. Atualmente retorna 503 (instável). Não usado nesta implementação.

---

## Módulos Novos

### `FusionService` — Orquestrador

```python
class FusionService:
    """
    Orquestra acesso ao Fusion: tenta SQL direto primeiro,
    usa API REST como fallback.
    """
    async def get_document_tree(self, numero_cnj: str) -> FusionResult | None:
        if self.sql_client and self.sql_client.is_available():
            try:
                return await self.sql_client.get_document_tree(numero_cnj)
            except FusionSQLException as e:
                logger.warning(f"Fusion SQL falhou ({e}), usando API REST")
        return await self.api_client.get_document_tree(numero_cnj)
```

### `FusionAPIClient` — Via REST

```python
class FusionAPIClient:
    """
    Consome o endpoint JSON do PAV.
    Requer cookie de sessão configurado.
    """
    BASE_URL = "https://pav.procuradoria.rio"
    ENDPOINT = "/services/custom-consulta-rapida-de-procesos/dados-da-consulta/{cnj}"

    async def get_document_tree(self, numero_cnj: str) -> FusionResult:
        # numero_cnj: apenas dígitos, sem formatação
        cnj_digits = re.sub(r'\D', '', numero_cnj)
        url = self.BASE_URL + self.ENDPOINT.format(cnj=cnj_digits)
        response = await self.http.get(url, headers={"Cookie": self.session_cookie})
        data = response.json()
        return self._parse(data, numero_cnj)

    def _parse(self, data: dict, numero_cnj: str) -> FusionResult:
        movimentos = [
            FusionMovimento(
                data=parse_date(m["dataDoMovimento"]),
                tipo_local=m["tipoMovimentoLocal"],
                tipo_cnj=m["tipoMovimentoCNJ"],
            )
            for m in data.get("movimentos", [])
        ]
        return FusionResult(
            numero_cnj=numero_cnj,
            neo_id=data["dadosPAV"].get("wfProcessNeoId"),
            classe_processual=data["dadosGerais"].get("classeProcessual", ""),
            sistema=data["dadosGerais"].get("descricaoSistema", ""),
            movimentos=sorted(movimentos, key=lambda m: m.data),
            fonte="fusion_api",
        )
```

### `FusionSQLClient` — Via SQL Server

```python
class FusionSQLClient:
    """
    Acesso direto ao SQL Server do Fusion.
    Queries a serem mapeadas com o usuário após verificar schema.
    """
    async def get_document_tree(self, numero_cnj: str) -> FusionResult:
        cnj_digits = re.sub(r'\D', '', numero_cnj)
        # Passo 1: CNJ → neoId + classeProcessual
        processo = await self._query_processo(cnj_digits)
        # Passo 2: neoId → movimentos ordenados
        movimentos = await self._query_movimentos(processo.neo_id)
        return FusionResult(
            numero_cnj=numero_cnj,
            neo_id=processo.neo_id,
            classe_processual=processo.classe_processual,
            movimentos=movimentos,
            fonte="fusion_sql",
        )
```

### `DocumentPhaseClassifier` — Engine de Batismos

#### Princípio

Percorre `movimentos[].tipoMovimentoLocal` em ordem **decrescente de data** (mais recente primeiro) e identifica o último evento significativo usando âncoras predefinidas.

#### Normalização

Todos os batismos são normalizados antes da comparação:
```python
def normalizar(texto: str) -> str:
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    return texto.lower().strip()
```

#### Âncoras de Fase (em ordem de prioridade)

| Prioridade | Padrão (regex, após normalização) | Fase | Notas |
|-----------|----------------------------------|------|-------|
| 1 | `arquivamento` | **15** | Arquivado Definitivamente |
| 2 | `certidao de transito em julgado` \| `transito em julgado` | **03** | Somente documento explícito com este nome |
| 3 | `^sentenca` \| `sentenca de merito` \| `sentenca homologatoria` \| `sentenca parcial` | **02** | Sentença pura — **NÃO** "Despacho / Sentença / Decisão" |
| 4 | `sentenca` (âncora 3) + âncora 2 encontrada cronologicamente após | **03** | Sentença com Trânsito |
| 5 | `remessa` \| `declinio de competencia` → redistribuição 2g | **04** | Recurso pendente 2ª inst. |
| 6 | `acordao` sem trânsito posterior | **05** | Acórdão sem Trânsito |
| 7 | `acordao` com trânsito posterior | **06** | Acórdão com Trânsito |
| 8 | `suspensao` \| `sobrestamento` | **13** | Suspenso/Sobrestado |
| — | `despacho / sentenca / decisao` | **IGNORADO** | Genérico — cobre despachos, decisões interlocutórias e sentenças indistintamente |

#### Contexto por Classe Processual

Antes de aplicar âncoras, a classe processual define o contexto macro:

```python
CLASSES_EXECUCAO = {
    "cumprimento de sentenca",
    "execucao fiscal",
    "execucao de titulo extrajudicial",
    "execucao",
    # ...
}

def classify(movimentos, classe_processual):
    classe_norm = normalizar(classe_processual)

    if classe_norm in CLASSES_EXECUCAO:
        return classify_execucao(movimentos)  # Fases 10-12, 14

    return classify_conhecimento(movimentos)  # Fases 01-09, 13, 15
```

#### Comportamento Conservador

Se nenhuma âncora for encontrada → **Fase 01** (processo em andamento, antes da sentença). Nunca inferir trânsito por ausência de atividade.

---

## Schema de Dados

```python
@dataclass
class FusionMovimento:
    data: datetime
    tipo_local: str     # "batismo" — usado na classificação
    tipo_cnj: str       # referência CNJ

@dataclass
class FusionResult:
    numero_cnj: str
    neo_id: int | None
    classe_processual: str
    sistema: str              # "TJRJ_DCP", "TJRJ_PJE", etc.
    movimentos: list[FusionMovimento]  # ordenados por data ASC
    fonte: str                # "fusion_api" | "fusion_sql"
    data_consulta: datetime = field(default_factory=datetime.utcnow)
```

---

## Integração com `ProcessService` (existente)

```python
# backend/services/process_service.py
async def get_or_update_process(number: str) -> Process:
    # --- lógica DataJud existente (inalterada) ---
    try:
        api_data = await datajud_client.get_process(number)
    except DataJudAPIException as e:
        # tenta retornar do cache local
        ...

    if api_data is None:
        # DataJud: not_found sem erro → ativa Fusion
        fusion_result = await fusion_service.get_document_tree(number)
        if fusion_result and fusion_result.movimentos:
            phase = document_classifier.classify(
                fusion_result.movimentos,
                fusion_result.classe_processual
            )
            return await _save_fusion_result(number, fusion_result, phase)
        # Fusion também não encontrou → not_found normal
        await _record_search_history(number, status="not_found")
        return None

    # --- lógica de classificação DataJud existente (inalterada) ---
    ...
```

---

## Mudanças no Banco de Dados

### Migration Alembic

```sql
-- processes
ALTER TABLE processes ADD COLUMN phase_source VARCHAR(20) DEFAULT 'datajud';
-- Valores: 'datajud' | 'fusion_api' | 'fusion_sql' | 'not_found'

-- search_history
ALTER TABLE search_history ADD COLUMN phase_source VARCHAR(20);
```

---

## Mudanças no Frontend

### Indicador de Fonte (mínimo e não-invasivo)

- Badge `[Fusion]` ao lado da fase em `SearchProcess` e `BulkSearch`
- Tooltip: *"Fase classificada via PAV/Fusion — processo não encontrado no DataJud"*
- Cor diferenciada do badge (ex: âmbar vs verde para DataJud)
- Sem nova tela ou componente — adição dentro dos componentes existentes

### Settings — Nova Aba "Integração Fusion"

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| PAV Base URL | text | Sim (API) |
| PAV Session Cookie | password | Sim (API) |
| SQL Server Host | text | Não (SQL) |
| SQL Server Port | number | Não (SQL) |
| SQL Server Database | text | Não (SQL) |
| SQL Server User | text | Não (SQL) |
| SQL Server Password | password | Não (SQL) |
| Botão "Testar Conexão" | action | — |

**Nota:** Cookie de sessão expira. Roadmap: automatizar login com usuário/senha PAV.

---

## Arquivos Afetados

| Arquivo | Tipo de Mudança |
|---------|----------------|
| `backend/services/fusion_service.py` | **Novo** |
| `backend/services/fusion_api_client.py` | **Novo** |
| `backend/services/fusion_sql_client.py` | **Novo** |
| `backend/services/document_phase_classifier.py` | **Novo** |
| `backend/services/process_service.py` | Adição — branch Fusion |
| `backend/models.py` | +campo `phase_source` |
| `backend/schemas.py` | +`phase_source` nos schemas |
| `backend/config.py` | +config Fusion |
| `backend/main.py` | +endpoint `GET /fusion/test` |
| `frontend/src/components/SearchProcess.jsx` | +badge Fusion |
| `frontend/src/components/BulkSearch.jsx` | +coluna/badge Fusion |
| `frontend/src/components/Settings.jsx` | +aba Fusion |
| `alembic/versions/xxxx_add_phase_source.py` | **Novo** — migration |

---

## Decisões de Design Registradas

| Decisão | Justificativa |
|---------|--------------|
| Fusion apenas quando DataJud retorna `not_found` sem erro | Não substituir a fonte primária; Fusion é complemento |
| API REST como via principal, SQL como preferencial quando disponível | Maior robustez; SQL evita dependência de cookie |
| `tipoMovimentoLocal` como âncora de classificação | Equivalente ao `nomeArquivo` da árvore de peças — mesma informação |
| `"Despacho / Sentença / Decisão"` ignorado como âncora | Nome genérico do DCP — cobre atos judiciais distintos |
| Trânsito em Julgado apenas com documento explícito | Conservadorismo jurídico — nunca inferir por ausência |
| Fallback conservador: Fase 01 se nenhuma âncora encontrada | Mais seguro juridicamente do que supor fase avançada |
| Mesmas 15 fases do sistema DataJud | Consistência de interface; sem nova dimensão de dado |

---

*Design aprovado em 2026-03-07. Próximo passo: plano de implementação.*
