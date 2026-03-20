# Fusion Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complementar a consulta DataJud com fallback ao Fusion/PAV quando o processo não é encontrado no DataJud, classificando a fase processual a partir dos batismos de documentos.

**Architecture:** Dual-source service (SQL Server direto → fallback API REST PAV). Ativado apenas quando DataJud retorna `not_found` sem erro. Nova engine de classificação por `tipoMovimentoLocal` dos movimentos do Fusion. Fase resultante usa as mesmas 15 categorias existentes.

**Tech Stack:** Python FastAPI, SQLAlchemy, httpx (já no projeto), pyodbc (SQL Server), pydantic_settings, React 19 (frontend), Tailwind CSS.

**Design doc:** `docs/plans/2026-03-07-fusion-integration-design.md`

---

## Contexto do Codebase

- Backend: `C:\Projetos\Consulta processo\backend\` (Python/FastAPI)
- Frontend: `C:\Projetos\Consulta processo\frontend\src\`
- Migrations SQL: `C:\Projetos\Consulta processo\backend\migrations\` (próxima: `005_`)
- Testes: `C:\Projetos\Consulta processo\backend\tests\`
- Worktree ativo: `C:\Projetos\Projetos Claude\Consulta processo\zen-bassi\`

**Padrões obrigatórios:**
- `pydantic_settings.BaseSettings` para config
- `unittest.mock` + `@patch` para testes
- `transaction_scope(db)` para transações
- `logger = logging.getLogger(__name__)` em cada módulo
- Relative imports (`from ..models import ...`)
- `Optional[type] = None` para campos nullable
- Classe de teste por feature, docstring `TC-N: descrição`

---

## Task 1: Migration — `phase_source` no banco

**Files:**
- Create: `backend/migrations/005_add_phase_source.sql`

**Step 1: Criar o arquivo de migration**

```sql
-- Migration 005: Add phase_source to processes and search_history
-- Story: Fusion Integration
-- Author: @dev
-- Description: Tracks whether phase was classified via DataJud or Fusion/PAV

-- Add phase_source to processes table
-- Values: 'datajud' | 'fusion_api' | 'fusion_sql' | null (legacy/unknown)
ALTER TABLE processes ADD COLUMN phase_source VARCHAR(20) DEFAULT 'datajud';

-- Add phase_source to search_history table
ALTER TABLE search_history ADD COLUMN phase_source VARCHAR(20);
```

**Step 2: Aplicar a migration ao banco local**

```bash
cd "C:\Projetos\Consulta processo"
python -c "
import sqlite3
conn = sqlite3.connect('consulta_processual.db')
conn.execute(\"ALTER TABLE processes ADD COLUMN phase_source VARCHAR(20) DEFAULT 'datajud'\")
conn.execute('ALTER TABLE search_history ADD COLUMN phase_source VARCHAR(20)')
conn.commit()
conn.close()
print('Migration 005 aplicada')
"
```

Expected: `Migration 005 aplicada`

**Step 3: Commit**

```bash
git add backend/migrations/005_add_phase_source.sql
git commit -m "feat: add phase_source migration [Fusion Integration]"
```

---

## Task 2: Models — `phase_source` em `Process` e `SearchHistory`

**Files:**
- Modify: `backend/models.py`

**Step 1: Escrever teste de modelo**

Abrir `backend/tests/test_models_extended.py` e adicionar ao final:

```python
class TestPhaseSourceField:
    """Tests for phase_source field on Process and SearchHistory."""

    def test_process_phase_source_defaults_to_datajud(self, db_session):
        """TC-1: Process.phase_source defaults to 'datajud'."""
        process = models.Process(
            number="0000001-01.2020.8.19.0001",
            phase_source="datajud"
        )
        db_session.add(process)
        db_session.commit()
        db_session.refresh(process)
        assert process.phase_source == "datajud"

    def test_process_phase_source_accepts_fusion_api(self, db_session):
        """TC-2: Process.phase_source accepts 'fusion_api'."""
        process = models.Process(
            number="0000001-01.2020.8.19.0002",
            phase_source="fusion_api"
        )
        db_session.add(process)
        db_session.commit()
        db_session.refresh(process)
        assert process.phase_source == "fusion_api"

    def test_search_history_phase_source_nullable(self, db_session):
        """TC-3: SearchHistory.phase_source is nullable."""
        history = models.SearchHistory(
            number="0000001-01.2020.8.19.0003",
            status="not_found"
        )
        db_session.add(history)
        db_session.commit()
        db_session.refresh(history)
        assert history.phase_source is None
```

**Step 2: Rodar o teste — verificar falha**

```bash
cd "C:\Projetos\Consulta processo"
python -m pytest backend/tests/test_models_extended.py::TestPhaseSourceField -v
```

Expected: `AttributeError: type object 'Process' has no attribute 'phase_source'`

**Step 3: Adicionar campos nos models**

Abrir `backend/models.py`. Localizar a classe `Process` e adicionar o campo após `phase_warning`:

```python
# Em class Process:
phase_source = Column(String(20), nullable=True, server_default="datajud")
```

Localizar a classe `SearchHistory` e adicionar após `error_message`:

```python
# Em class SearchHistory:
phase_source = Column(String(20), nullable=True)
```

**Step 4: Rodar os testes**

```bash
python -m pytest backend/tests/test_models_extended.py::TestPhaseSourceField -v
```

Expected: 3 testes PASS

**Step 5: Commit**

```bash
git add backend/models.py
git commit -m "feat: add phase_source field to Process and SearchHistory models"
```

---

## Task 3: Schemas — `phase_source` nas respostas

**Files:**
- Modify: `backend/schemas.py`

**Step 1: Adicionar `phase_source` nos schemas de resposta**

Abrir `backend/schemas.py`. Localizar `ProcessResponse` e adicionar após `phase_warning`:

```python
# Em ProcessResponse:
phase_source: Optional[str] = None
```

Localizar `SearchHistoryResponse` (ou equivalente) e adicionar:

```python
# Em SearchHistoryResponse (ou SearchHistory schema):
phase_source: Optional[str] = None
```

Localizar `ProcessBulkResult` (usado no bulk, schema leve) e adicionar:

```python
# Em ProcessBulkResult:
phase_source: Optional[str] = None
```

**Step 2: Verificar que os testes de schemas existentes continuam passando**

```bash
python -m pytest backend/tests/ -k "schema" -v
```

Expected: todos PASS (campos Optional não quebram schemas existentes)

**Step 3: Commit**

```bash
git add backend/schemas.py
git commit -m "feat: expose phase_source in process response schemas"
```

---

## Task 4: Config — settings Fusion

**Files:**
- Modify: `backend/config.py`

**Step 1: Adicionar settings Fusion**

Abrir `backend/config.py`. Localizar a classe `Settings` e adicionar um bloco novo ao final (antes de `model_config`):

```python
# --- Fusion / PAV Integration ---
FUSION_ENABLED: bool = True
FUSION_PAV_BASE_URL: str = "https://pav.procuradoria.rio"
FUSION_PAV_SESSION_COOKIE: str = ""  # Cookie JSESSIONID da sessão PAV
FUSION_PAV_TIMEOUT: int = 30

# SQL Server direto (opcional — se vazio, usa apenas API REST)
FUSION_SQL_HOST: str = ""
FUSION_SQL_PORT: int = 1433
FUSION_SQL_DATABASE: str = ""
FUSION_SQL_USER: str = ""
FUSION_SQL_PASSWORD: str = ""

@property
def fusion_sql_configured(self) -> bool:
    """True se todas as credenciais SQL Server estiverem configuradas."""
    return all([
        self.FUSION_SQL_HOST,
        self.FUSION_SQL_DATABASE,
        self.FUSION_SQL_USER,
        self.FUSION_SQL_PASSWORD,
    ])

@property
def fusion_api_configured(self) -> bool:
    """True se o cookie de sessão PAV estiver configurado."""
    return bool(self.FUSION_PAV_SESSION_COOKIE)
```

**Step 2: Verificar que os testes de config existentes passam**

```bash
python -m pytest backend/tests/test_config.py -v
```

Expected: todos PASS

**Step 3: Commit**

```bash
git add backend/config.py
git commit -m "feat: add Fusion/PAV configuration settings"
```

---

## Task 5: `DocumentPhaseClassifier` — engine de batismos

**Files:**
- Create: `backend/services/document_phase_classifier.py`
- Create: `backend/tests/test_document_phase_classifier.py`

**Step 1: Escrever os testes**

Criar `backend/tests/test_document_phase_classifier.py`:

```python
"""
Tests for DocumentPhaseClassifier — phase classification via document batismos.
"""
import pytest
from datetime import datetime
from backend.services.document_phase_classifier import DocumentPhaseClassifier, FusionMovimento


def _mov(tipo_local: str, data: str = "01/01/2024 10:00") -> FusionMovimento:
    """Helper: create FusionMovimento from tipo_local string."""
    return FusionMovimento(
        data=datetime.strptime(data, "%d/%m/%Y %H:%M"),
        tipo_local=tipo_local,
        tipo_cnj="",
    )


class TestClassifyArquivamento:
    """Tests for phase 15 — Arquivado Definitivamente."""

    def test_arquivamento_retorna_fase_15(self):
        """TC-1: Arquivamento ao final retorna fase 15."""
        movimentos = [
            _mov("Petição Inicial", "20/12/2023 14:35"),
            _mov("Sentença", "10/02/2024 15:00"),
            _mov("Trânsito em Julgado", "12/05/2024 10:00"),
            _mov("Arquivamento", "12/06/2024 16:33"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "15"

    def test_arquivamento_tem_prioridade_sobre_transito(self):
        """TC-2: Arquivamento posterior ao Trânsito tem prioridade."""
        movimentos = [
            _mov("Trânsito em Julgado", "01/01/2024 10:00"),
            _mov("Arquivamento", "02/02/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "15"


class TestClassifyTransitoJulgado:
    """Tests for phase 03 — Sentença com Trânsito em Julgado."""

    def test_certidao_transito_retorna_fase_03(self):
        """TC-3: Certidão de Trânsito em Julgado retorna fase 03."""
        movimentos = [
            _mov("Petição Inicial"),
            _mov("Sentença", "10/02/2024 10:00"),
            _mov("Certidão de Trânsito em Julgado", "12/05/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "03"

    def test_transito_em_julgado_explicito_retorna_fase_03(self):
        """TC-4: Documento 'Trânsito em Julgado' explícito retorna fase 03."""
        movimentos = [
            _mov("Sentença", "10/02/2024 10:00"),
            _mov("Trânsito em Julgado", "12/05/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "03"

    def test_sem_transito_nao_classifica_03(self):
        """TC-5: Sentença sem documento de trânsito não retorna fase 03."""
        movimentos = [
            _mov("Petição Inicial"),
            _mov("Sentença", "10/02/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "02"


class TestClassifySentenca:
    """Tests for phase 02 — Sentença sem Trânsito em Julgado."""

    def test_sentenca_pura_retorna_fase_02(self):
        """TC-6: 'Sentença' pura sem trânsito retorna fase 02."""
        movimentos = [
            _mov("Petição Inicial"),
            _mov("Conclusão ao Juiz"),
            _mov("Sentença", "10/02/2024 10:00"),
            _mov("Intimação Eletrônica - Atos do Juiz"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "02"

    def test_sentenca_homologatoria_retorna_fase_02(self):
        """TC-7: 'Sentença Homologatória' retorna fase 02."""
        movimentos = [_mov("Sentença Homologatória")]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "02"

    def test_sentenca_de_merito_retorna_fase_02(self):
        """TC-8: 'Sentença de Mérito' retorna fase 02."""
        movimentos = [_mov("Sentença de Mérito")]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "02"

    def test_despacho_sentenca_decisao_nao_classifica_sentenca(self):
        """TC-9: 'Despacho / Sentença / Decisão' NÃO retorna fase 02 (genérico)."""
        movimentos = [
            _mov("Petição Inicial"),
            _mov("Despacho / Sentença / Decisão"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "01"  # sem âncora de sentença → fase 01


class TestClassifyFase01:
    """Tests for phase 01 — Antes da Sentença (fallback conservador)."""

    def test_sem_ancoras_retorna_fase_01(self):
        """TC-10: Processo sem âncoras retorna fase 01."""
        movimentos = [
            _mov("Petição Inicial"),
            _mov("Conclusão ao Juiz"),
            _mov("Despacho / Sentença / Decisão"),
            _mov("Intimação Eletrônica - Atos do Juiz"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "01"

    def test_lista_vazia_retorna_fase_01(self):
        """TC-11: Lista vazia de movimentos retorna fase 01."""
        result = DocumentPhaseClassifier.classify([], "Ação Cível")
        assert result == "01"


class TestClassifyExecucao:
    """Tests for execution phases (10-12)."""

    def test_cumprimento_sentenca_retorna_fase_10(self):
        """TC-12: Classe 'Cumprimento de sentença' retorna fase 10."""
        movimentos = [
            _mov("Petição"),
            _mov("Ato Ordinatório Praticado"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Cumprimento de sentença")
        assert result == "10"

    def test_execucao_fiscal_retorna_fase_10(self):
        """TC-13: Classe 'Execução Fiscal' retorna fase 10."""
        movimentos = [_mov("Petição")]
        result = DocumentPhaseClassifier.classify(movimentos, "Execução Fiscal")
        assert result == "10"

    def test_execucao_arquivada_retorna_fase_15(self):
        """TC-14: Execução com Arquivamento retorna fase 15."""
        movimentos = [
            _mov("Petição"),
            _mov("Arquivamento"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Cumprimento de sentença")
        assert result == "15"


class TestNormalizacaoBatismos:
    """Tests for batismo normalization (accents, case)."""

    def test_arquivamento_sem_acento(self):
        """TC-15: 'Arquivamento' sem acento é reconhecido."""
        result = DocumentPhaseClassifier.classify([_mov("Arquivamento")], "Ação Cível")
        assert result == "15"

    def test_transito_com_acento(self):
        """TC-16: 'Trânsito em Julgado' com acento é reconhecido."""
        result = DocumentPhaseClassifier.classify(
            [_mov("Sentença"), _mov("Trânsito em Julgado")], "Ação Cível"
        )
        assert result == "03"

    def test_transito_sem_acento(self):
        """TC-17: 'Transito em Julgado' sem acento também é reconhecido."""
        result = DocumentPhaseClassifier.classify(
            [_mov("Sentença"), _mov("Transito em Julgado")], "Ação Cível"
        )
        assert result == "03"
```

**Step 2: Rodar testes — verificar falha**

```bash
cd "C:\Projetos\Consulta processo"
python -m pytest backend/tests/test_document_phase_classifier.py -v
```

Expected: `ModuleNotFoundError: No module named 'backend.services.document_phase_classifier'`

**Step 3: Implementar `DocumentPhaseClassifier`**

Criar `backend/services/document_phase_classifier.py`:

```python
"""
DocumentPhaseClassifier — classifica fase processual a partir dos batismos
de peças do Fusion/PAV (tipoMovimentoLocal).

Usa lógica de âncoras em ordem cronológica decrescente.
Trânsito em Julgado: somente com documento explícito (certidão ou peça nomeada).
Sentença: somente para peças nomeadas exclusivamente como sentença.
'Despacho / Sentença / Decisão' é ignorado (nome genérico do DCP).
"""
import unicodedata
import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FusionMovimento:
    data: datetime
    tipo_local: str   # "batismo" — principal âncora de classificação
    tipo_cnj: str     # código CNJ (referência)


# ---------------------------------------------------------------------------
# Anchor patterns (after normalization)
# ---------------------------------------------------------------------------

# Fase 15 — Arquivado Definitivamente
_ANCHOR_ARQUIVAMENTO = re.compile(r'\barquivamento\b')

# Fase 03 — Trânsito em Julgado (somente documento explícito)
_ANCHOR_TRANSITO = re.compile(
    r'(certidao\s+de\s+transito\s+em\s+julgado|transito\s+em\s+julgado)'
)

# Fase 02 / 03 — Sentença pura (NÃO "despacho / sentenca / decisao")
# Aceita: "Sentença", "Sentença de Mérito", "Sentença Homologatória", "Sentença Parcial"
# Rejeita: "Despacho / Sentença / Decisão"
_ANCHOR_SENTENCA = re.compile(r'^sentenca(\s+(de\s+merito|homologatoria|parcial|condenatoria|declaratoria|constitutiva))?$')

# Fase 04+ — Remessa / recurso para instância superior
_ANCHOR_REMESSA = re.compile(r'(remessa\b|declinio\s+de\s+competencia|redistribuicao)')

# Fase 13 — Suspenso/Sobrestado
_ANCHOR_SUSPENSO = re.compile(r'(suspensao|sobrestamento|processo\s+suspenso)')

# Classes processuais que indicam execução (fases 10-12, 14)
_CLASSES_EXECUCAO = {
    "cumprimento de sentenca",
    "cumprimento provisorio de sentenca",
    "execucao fiscal",
    "execucao de titulo extrajudicial",
    "execucao",
    "execucao por quantia certa",
    "execucao de alimentos",
}


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class DocumentPhaseClassifier:
    """
    Classifica fase processual a partir de movimentos do Fusion/PAV.
    Stateless — todos os métodos são classmethod.
    """

    @classmethod
    def classify(cls, movimentos: List[FusionMovimento], classe_processual: str) -> str:
        """
        Retorna código de fase (string "01"–"15").

        Args:
            movimentos: lista ordenada cronologicamente (ASC por data).
            classe_processual: classe do processo no tribunal.

        Returns:
            Fase processual como string de 2 dígitos.
        """
        classe_norm = cls._normalize(classe_processual)

        # Contexto de execução → branch específico
        if classe_norm in _CLASSES_EXECUCAO:
            return cls._classify_execucao(movimentos)

        return cls._classify_conhecimento(movimentos)

    # ------------------------------------------------------------------
    # Branch: conhecimento (fases 01–09, 13, 15)
    # ------------------------------------------------------------------

    @classmethod
    def _classify_conhecimento(cls, movimentos: List[FusionMovimento]) -> str:
        if not movimentos:
            return "01"

        # Percorre do mais recente para o mais antigo
        ordered = sorted(movimentos, key=lambda m: m.data, reverse=True)
        nomes = [cls._normalize(m.tipo_local) for m in ordered]

        # P1: Arquivamento
        for nome in nomes:
            if _ANCHOR_ARQUIVAMENTO.search(nome):
                return "15"

        # P2: Trânsito em Julgado (explícito)
        transito_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_TRANSITO.search(n)), None
        )

        # P3: Sentença pura
        sentenca_idx = next(
            (i for i, n in enumerate(nomes) if _ANCHOR_SENTENCA.match(n)), None
        )

        if transito_idx is not None:
            # Trânsito encontrado
            if sentenca_idx is not None:
                # Sentença também existe → fase 03
                return "03"
            # Trânsito sem sentença explícita → fase 03 (documento independente)
            return "03"

        if sentenca_idx is not None:
            # Sentença sem trânsito → fase 02
            return "02"

        # P5: Suspensão
        for nome in nomes:
            if _ANCHOR_SUSPENSO.search(nome):
                return "13"

        # Fallback conservador: antes da sentença
        return "01"

    # ------------------------------------------------------------------
    # Branch: execução (fases 10–12, 14, 15)
    # ------------------------------------------------------------------

    @classmethod
    def _classify_execucao(cls, movimentos: List[FusionMovimento]) -> str:
        if not movimentos:
            return "10"

        ordered = sorted(movimentos, key=lambda m: m.data, reverse=True)
        nomes = [cls._normalize(m.tipo_local) for m in ordered]

        # Arquivamento também termina execução
        for nome in nomes:
            if _ANCHOR_ARQUIVAMENTO.search(nome):
                return "15"

        # Suspensão de execução
        for nome in nomes:
            if _ANCHOR_SUSPENSO.search(nome):
                return "11"

        return "10"

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    @classmethod
    def _normalize(cls, texto: str) -> str:
        """Remove acentos, converte para minúsculas, normaliza espaços."""
        if not texto:
            return ""
        # Remove acentos via NFD decomposition
        nfkd = unicodedata.normalize("NFKD", texto)
        ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
        # Lowercase, strip, normalizar espaços múltiplos
        return re.sub(r'\s+', ' ', ascii_text.lower().strip())
```

**Step 4: Rodar todos os testes**

```bash
python -m pytest backend/tests/test_document_phase_classifier.py -v
```

Expected: 17 testes PASS

**Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier.py
git commit -m "feat: add DocumentPhaseClassifier with batismo-based phase detection"
```

---

## Task 6: `FusionAPIClient` — REST client PAV

**Files:**
- Create: `backend/services/fusion_api_client.py`
- Create: `backend/tests/test_fusion_api_client.py`

**Step 1: Escrever os testes**

Criar `backend/tests/test_fusion_api_client.py`:

```python
"""Tests for FusionAPIClient — PAV REST API client."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from backend.services.fusion_api_client import FusionAPIClient
from backend.services.document_phase_classifier import FusionMovimento


MOCK_RESPONSE = {
    "dadosPAV": {"wfProcessNeoId": 950453990, "neoId": 950453990},
    "dadosGerais": {
        "numeroJudicial": "00754816320208190001",
        "classeProcessual": "Cumprimento de sentença",
        "descricaoSistema": "TJRJ_DCP",
    },
    "movimentos": [
        {
            "dataDoMovimento": "08/04/2020 15:59",
            "tipoMovimentoCNJ": "Distribuição",
            "tipoMovimentoLocal": "DISTRIBUIÇÃO Sorteio",
            "documentos": ["123"],
        },
        {
            "dataDoMovimento": "10/02/2024 15:14",
            "tipoMovimentoCNJ": "Sentença",
            "tipoMovimentoLocal": "Sentença",
            "documentos": ["456"],
        },
    ],
    "encontradoTribunal": True,
    "uuid": "abc-123",
}


class TestFusionAPIClientParse:
    """Tests for response parsing."""

    def test_parse_retorna_fusion_result_correto(self):
        """TC-1: Parse retorna FusionResult com campos corretos."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=test",
            timeout=30,
        )
        result = client._parse(MOCK_RESPONSE, "00754816320208190001")

        assert result.neo_id == 950453990
        assert result.classe_processual == "Cumprimento de sentença"
        assert result.sistema == "TJRJ_DCP"
        assert result.fonte == "fusion_api"
        assert len(result.movimentos) == 2

    def test_parse_ordena_movimentos_por_data(self):
        """TC-2: Movimentos são ordenados cronologicamente (ASC)."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=test",
            timeout=30,
        )
        result = client._parse(MOCK_RESPONSE, "00754816320208190001")

        datas = [m.data for m in result.movimentos]
        assert datas == sorted(datas)

    def test_parse_converte_tipo_local_corretamente(self):
        """TC-3: tipoMovimentoLocal é mapeado para FusionMovimento.tipo_local."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=test",
            timeout=30,
        )
        result = client._parse(MOCK_RESPONSE, "00754816320208190001")
        assert result.movimentos[0].tipo_local == "DISTRIBUIÇÃO Sorteio"


class TestFusionAPIClientHTTP:
    """Tests for HTTP request behavior."""

    @pytest.mark.asyncio
    async def test_get_document_tree_chama_endpoint_correto(self):
        """TC-4: URL do endpoint contém número CNJ sem formatação."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=abc",
            timeout=30,
        )
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "get", new_callable=AsyncMock, return_value=mock_resp) as mock_get:
            await client.get_document_tree("0075481-63.2020.8.19.0001")
            called_url = mock_get.call_args[0][0]
            assert "00754816320208190001" in called_url
            assert "dados-da-consulta" in called_url

    @pytest.mark.asyncio
    async def test_get_document_tree_retorna_none_se_nao_encontrado(self):
        """TC-5: Retorna None se encontradoTribunal for False."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=abc",
            timeout=30,
        )
        mock_resp = MagicMock()
        mock_resp.json.return_value = {**MOCK_RESPONSE, "encontradoTribunal": False}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "get", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.get_document_tree("0075481-63.2020.8.19.0001")
            assert result is None
```

**Step 2: Rodar testes — verificar falha**

```bash
python -m pytest backend/tests/test_fusion_api_client.py -v
```

Expected: `ModuleNotFoundError: No module named 'backend.services.fusion_api_client'`

**Step 3: Implementar `FusionAPIClient`**

Criar `backend/services/fusion_api_client.py`:

```python
"""
FusionAPIClient — consome a API REST do PAV/Fusion para obter
árvore de documentos de um processo por número CNJ.

Endpoint descoberto:
GET https://pav.procuradoria.rio/services/custom-consulta-rapida-de-procesos/
    dados-da-consulta/{numero_cnj_sem_formatacao}
"""
import re
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

import httpx

from .document_phase_classifier import FusionMovimento

logger = logging.getLogger(__name__)

_DATE_FMT_SHORT = "%d/%m/%Y %H:%M"
_DATE_FMT_LONG  = "%d/%m/%Y %H:%M:%S"


def _parse_date(valor: str) -> datetime:
    """Tenta parsear data nos formatos curto e longo do PAV."""
    for fmt in (_DATE_FMT_LONG, _DATE_FMT_SHORT):
        try:
            return datetime.strptime(valor.strip(), fmt)
        except ValueError:
            continue
    # Fallback: data mínima para não quebrar a ordenação
    logger.warning(f"Não foi possível parsear data: {valor!r}")
    return datetime.min


@dataclass
class FusionResult:
    numero_cnj: str
    neo_id: Optional[int]
    classe_processual: str
    sistema: str
    movimentos: list          # List[FusionMovimento], ordenado ASC por data
    fonte: str                # "fusion_api" | "fusion_sql"
    data_consulta: datetime = None

    def __post_init__(self):
        if self.data_consulta is None:
            self.data_consulta = datetime.utcnow()


class FusionAPIClient:
    """
    Cliente HTTP para a API REST do PAV.
    Requer cookie de sessão JSESSIONID configurado.
    """

    _ENDPOINT = (
        "/services/custom-consulta-rapida-de-procesos"
        "/dados-da-consulta/{cnj}"
    )

    def __init__(self, base_url: str, session_cookie: str, timeout: int = 30):
        self._base_url = base_url.rstrip("/")
        self._session_cookie = session_cookie
        self._http = httpx.AsyncClient(
            timeout=timeout,
            headers={"Cookie": session_cookie} if session_cookie else {},
            follow_redirects=True,
        )

    async def get_document_tree(self, numero_cnj: str) -> Optional[FusionResult]:
        """
        Busca árvore de documentos pelo número CNJ.
        Retorna None se o processo não for encontrado no PAV.

        Args:
            numero_cnj: número CNJ (com ou sem formatação).

        Returns:
            FusionResult com movimentos ou None se não encontrado.
        """
        cnj_digits = re.sub(r"\D", "", numero_cnj)
        url = self._base_url + self._ENDPOINT.format(cnj=cnj_digits)

        try:
            response = await self._http.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.warning(f"PAV API HTTP error for {cnj_digits}: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"PAV API request error for {cnj_digits}: {e}")
            raise

        data = response.json()

        if not data.get("encontradoTribunal", False):
            logger.info(f"Processo {cnj_digits} não encontrado no tribunal via PAV")
            return None

        return self._parse(data, numero_cnj)

    def _parse(self, data: dict, numero_cnj: str) -> FusionResult:
        """Converte resposta JSON do PAV em FusionResult."""
        dados_pav = data.get("dadosPAV", {})
        dados_gerais = data.get("dadosGerais", {})

        movimentos = []
        for m in data.get("movimentos", []):
            try:
                movimentos.append(FusionMovimento(
                    data=_parse_date(m.get("dataDoMovimento", "")),
                    tipo_local=m.get("tipoMovimentoLocal", ""),
                    tipo_cnj=m.get("tipoMovimentoCNJ", ""),
                ))
            except Exception as e:
                logger.warning(f"Erro ao parsear movimento {m}: {e}")

        # Ordenar ASC por data
        movimentos.sort(key=lambda m: m.data)

        return FusionResult(
            numero_cnj=numero_cnj,
            neo_id=dados_pav.get("wfProcessNeoId") or dados_pav.get("neoId"),
            classe_processual=dados_gerais.get("classeProcessual", ""),
            sistema=dados_gerais.get("descricaoSistema", ""),
            movimentos=movimentos,
            fonte="fusion_api",
        )

    async def aclose(self):
        await self._http.aclose()
```

**Step 4: Rodar os testes**

```bash
python -m pytest backend/tests/test_fusion_api_client.py -v
```

Expected: 5 testes PASS

**Step 5: Commit**

```bash
git add backend/services/fusion_api_client.py backend/tests/test_fusion_api_client.py
git commit -m "feat: add FusionAPIClient for PAV REST endpoint"
```

---

## Task 7: `FusionSQLClient` — SQL Server (stub configurável)

**Files:**
- Create: `backend/services/fusion_sql_client.py`
- Create: `backend/tests/test_fusion_sql_client.py`

> **Nota:** A query SQL depende do schema real do Fusion. Esta task implementa a estrutura e um stub funcional com queries a serem confirmadas com o usuário quando o acesso ao SQL Server for estabelecido.

**Step 1: Escrever os testes**

Criar `backend/tests/test_fusion_sql_client.py`:

```python
"""Tests for FusionSQLClient — SQL Server direct access."""
import pytest
from unittest.mock import MagicMock, patch
from backend.services.fusion_sql_client import FusionSQLClient, FusionSQLException


class TestFusionSQLClientAvailability:
    """Tests for availability check."""

    def test_is_available_false_sem_host(self):
        """TC-1: is_available() retorna False sem host configurado."""
        client = FusionSQLClient(host="", port=1433, database="db", user="u", password="p")
        assert client.is_available() is False

    def test_is_available_false_sem_database(self):
        """TC-2: is_available() retorna False sem database configurado."""
        client = FusionSQLClient(host="server", port=1433, database="", user="u", password="p")
        assert client.is_available() is False

    def test_is_available_true_com_credenciais_completas(self):
        """TC-3: is_available() retorna True com todas as credenciais."""
        client = FusionSQLClient(host="server", port=1433, database="db", user="u", password="p")
        assert client.is_available() is True


class TestFusionSQLClientConnection:
    """Tests for connection string building."""

    def test_connection_string_correto(self):
        """TC-4: Connection string segue formato pyodbc SQL Server."""
        client = FusionSQLClient(host="10.0.0.1", port=1433, database="FusionDB", user="sa", password="pass")
        cs = client._build_connection_string()
        assert "10.0.0.1" in cs
        assert "FusionDB" in cs
        assert "1433" in cs
```

**Step 2: Rodar testes — verificar falha**

```bash
python -m pytest backend/tests/test_fusion_sql_client.py -v
```

Expected: `ModuleNotFoundError`

**Step 3: Implementar `FusionSQLClient`**

Criar `backend/services/fusion_sql_client.py`:

```python
"""
FusionSQLClient — acesso direto ao SQL Server do Fusion.

As queries SQL dependem do schema real do banco Fusion e devem ser
validadas com o DBA antes de ativar esta via. Por padrão a via API REST
é usada como fallback.

Requer: pyodbc instalado (`pip install pyodbc`)
"""
import logging
import re
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class FusionSQLException(Exception):
    pass


class FusionSQLClient:
    """
    Cliente SQL Server para acesso direto ao banco do Fusion.
    Stateless — cria conexão por request.
    """

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

    def is_available(self) -> bool:
        """True se todas as credenciais obrigatórias estiverem configuradas."""
        return bool(self._host and self._database and self._user and self._password)

    def _build_connection_string(self) -> str:
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self._host},{self._port};"
            f"DATABASE={self._database};"
            f"UID={self._user};"
            f"PWD={self._password};"
            f"TrustServerCertificate=yes;"
        )

    async def get_document_tree(self, numero_cnj: str):
        """
        Busca árvore de documentos via SQL Server.

        TODO: Queries a serem confirmadas com DBA após verificar schema.
        Estrutura esperada no Fusion:
          - Tabela de processos com campo numeroJudicial (CNJ sem formatação)
          - Tabela de movimentos com tipoMovimentoLocal e dataMovimento

        Raises:
            FusionSQLException: em caso de erro de conexão ou query.
        """
        if not self.is_available():
            raise FusionSQLException("SQL Server não configurado")

        try:
            import pyodbc  # noqa: F401 — importação lazy
        except ImportError:
            raise FusionSQLException(
                "pyodbc não instalado. Execute: pip install pyodbc"
            )

        cnj_digits = re.sub(r"\D", "", numero_cnj)

        # ---------------------------------------------------------------
        # PLACEHOLDER — substituir pelas queries reais após mapeamento
        # do schema do banco Fusion com o DBA
        # ---------------------------------------------------------------
        raise FusionSQLException(
            f"FusionSQLClient: queries SQL ainda não mapeadas para o schema Fusion. "
            f"CNJ: {cnj_digits}. Configure as queries após verificar o schema com o DBA."
        )
```

**Step 4: Rodar os testes**

```bash
python -m pytest backend/tests/test_fusion_sql_client.py -v
```

Expected: 4 testes PASS

**Step 5: Commit**

```bash
git add backend/services/fusion_sql_client.py backend/tests/test_fusion_sql_client.py
git commit -m "feat: add FusionSQLClient stub (queries pending schema mapping)"
```

---

## Task 8: `FusionService` — Orquestrador

**Files:**
- Create: `backend/services/fusion_service.py`
- Create: `backend/tests/test_fusion_service.py`

**Step 1: Escrever os testes**

Criar `backend/tests/test_fusion_service.py`:

```python
"""Tests for FusionService orchestrator."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.services.fusion_service import FusionService
from backend.services.fusion_sql_client import FusionSQLException


def _make_result(fonte="fusion_api"):
    from backend.services.fusion_api_client import FusionResult
    from datetime import datetime
    return FusionResult(
        numero_cnj="0000001-01.2020.8.19.0001",
        neo_id=123,
        classe_processual="Ação Cível",
        sistema="TJRJ_DCP",
        movimentos=[],
        fonte=fonte,
    )


class TestFusionServiceOrchestration:
    """Tests for SQL → API fallback logic."""

    @pytest.mark.asyncio
    async def test_usa_sql_quando_disponivel(self):
        """TC-1: Usa SQL direto quando disponível."""
        sql = MagicMock()
        sql.is_available.return_value = True
        sql.get_document_tree = AsyncMock(return_value=_make_result("fusion_sql"))

        api = MagicMock()
        api.get_document_tree = AsyncMock()

        service = FusionService(sql_client=sql, api_client=api)
        result = await service.get_document_tree("0000001-01.2020.8.19.0001")

        assert result.fonte == "fusion_sql"
        api.get_document_tree.assert_not_called()

    @pytest.mark.asyncio
    async def test_fallback_para_api_quando_sql_falha(self):
        """TC-2: Cai para API REST quando SQL lança exceção."""
        sql = MagicMock()
        sql.is_available.return_value = True
        sql.get_document_tree = AsyncMock(side_effect=FusionSQLException("erro"))

        api = MagicMock()
        api.get_document_tree = AsyncMock(return_value=_make_result("fusion_api"))

        service = FusionService(sql_client=sql, api_client=api)
        result = await service.get_document_tree("0000001-01.2020.8.19.0001")

        assert result.fonte == "fusion_api"

    @pytest.mark.asyncio
    async def test_usa_api_quando_sql_nao_disponivel(self):
        """TC-3: Vai direto para API quando SQL não configurado."""
        sql = MagicMock()
        sql.is_available.return_value = False

        api = MagicMock()
        api.get_document_tree = AsyncMock(return_value=_make_result("fusion_api"))

        service = FusionService(sql_client=sql, api_client=api)
        result = await service.get_document_tree("0000001-01.2020.8.19.0001")

        assert result.fonte == "fusion_api"
        sql.get_document_tree.assert_not_called()

    @pytest.mark.asyncio
    async def test_retorna_none_quando_nao_encontrado(self):
        """TC-4: Retorna None quando API também não encontra o processo."""
        sql = MagicMock()
        sql.is_available.return_value = False

        api = MagicMock()
        api.get_document_tree = AsyncMock(return_value=None)

        service = FusionService(sql_client=sql, api_client=api)
        result = await service.get_document_tree("0000001-01.2020.8.19.0001")

        assert result is None
```

**Step 2: Rodar testes — verificar falha**

```bash
python -m pytest backend/tests/test_fusion_service.py -v
```

Expected: `ModuleNotFoundError`

**Step 3: Implementar `FusionService`**

Criar `backend/services/fusion_service.py`:

```python
"""
FusionService — orquestra o acesso ao Fusion/PAV.

Tenta SQL Server direto primeiro (se configurado),
usa API REST PAV como fallback.
"""
import logging
from typing import Optional

from .fusion_sql_client import FusionSQLClient, FusionSQLException
from .fusion_api_client import FusionAPIClient, FusionResult

logger = logging.getLogger(__name__)


class FusionService:
    """
    Orquestrador dual-source para consulta ao Fusion/PAV.

    Priority:
      1. SQL Server direto (se is_available())
      2. API REST PAV (fallback)
    """

    def __init__(
        self,
        sql_client: Optional[FusionSQLClient],
        api_client: FusionAPIClient,
    ):
        self._sql = sql_client
        self._api = api_client

    async def get_document_tree(self, numero_cnj: str) -> Optional[FusionResult]:
        """
        Busca movimentos do processo no Fusion.

        Args:
            numero_cnj: número CNJ (com ou sem formatação).

        Returns:
            FusionResult ou None se não encontrado em nenhuma fonte.
        """
        # Via 1: SQL Server direto
        if self._sql and self._sql.is_available():
            try:
                result = await self._sql.get_document_tree(numero_cnj)
                if result is not None:
                    logger.info(f"Fusion SQL: processo {numero_cnj} encontrado")
                    return result
            except FusionSQLException as e:
                logger.warning(
                    f"Fusion SQL falhou para {numero_cnj}, usando API REST: {e}"
                )

        # Via 2: API REST PAV
        try:
            result = await self._api.get_document_tree(numero_cnj)
            if result is not None:
                logger.info(f"Fusion API: processo {numero_cnj} encontrado")
            else:
                logger.info(f"Fusion API: processo {numero_cnj} não encontrado")
            return result
        except Exception as e:
            logger.error(f"Fusion API erro para {numero_cnj}: {e}")
            return None
```

**Step 4: Rodar os testes**

```bash
python -m pytest backend/tests/test_fusion_service.py -v
```

Expected: 4 testes PASS

**Step 5: Commit**

```bash
git add backend/services/fusion_service.py backend/tests/test_fusion_service.py
git commit -m "feat: add FusionService orchestrator with SQL→API fallback"
```

---

## Task 9: Integração em `ProcessService`

**Files:**
- Modify: `backend/services/process_service.py`
- Create: `backend/services/dependency_container.py` (verificar se já existe — adicionar Fusion)

**Step 1: Ler o código atual de `process_service.py`**

```bash
grep -n "not_found\|api_data is None\|api_data ==" "C:\Projetos\Consulta processo\backend\services\process_service.py"
```

Identifique a linha onde `api_data is None` (ou equivalente) é verificado.

**Step 2: Escrever teste de integração**

Abrir `backend/tests/test_async_bulk.py` ou criar `backend/tests/test_process_service_fusion.py`:

```python
"""Tests for ProcessService Fusion fallback integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.process_service import ProcessService


class TestProcessServiceFusionFallback:
    """Tests for Fusion fallback when DataJud returns not_found."""

    @pytest.mark.asyncio
    async def test_ativa_fusion_quando_datajud_not_found(self, db_session):
        """TC-1: FusionService é chamado quando DataJud retorna None."""
        from backend.services.fusion_api_client import FusionResult
        from backend.services.document_phase_classifier import FusionMovimento
        from datetime import datetime

        fusion_result = FusionResult(
            numero_cnj="0000001-01.2020.8.19.0001",
            neo_id=999,
            classe_processual="Ação Cível",
            sistema="TJRJ_DCP",
            movimentos=[
                FusionMovimento(
                    data=datetime(2024, 1, 1),
                    tipo_local="Sentença",
                    tipo_cnj="Sentença",
                )
            ],
            fonte="fusion_api",
        )

        mock_datajud = MagicMock()
        mock_datajud.get_process = AsyncMock(return_value=None)

        mock_fusion = MagicMock()
        mock_fusion.get_document_tree = AsyncMock(return_value=fusion_result)

        service = ProcessService(
            db=db_session,
            client=mock_datajud,
            fusion_service=mock_fusion,
        )

        result = await service.get_or_update_process("0000001-01.2020.8.19.0001")

        mock_fusion.get_document_tree.assert_called_once()
        assert result is not None
        assert result.phase_source == "fusion_api"

    @pytest.mark.asyncio
    async def test_nao_ativa_fusion_quando_datajud_retorna_dados(self, db_session):
        """TC-2: FusionService NÃO é chamado quando DataJud encontra o processo."""
        mock_datajud = MagicMock()
        mock_datajud.get_process = AsyncMock(return_value={"hits": {"hits": [{"_source": {}}]}})

        mock_fusion = MagicMock()
        mock_fusion.get_document_tree = AsyncMock()

        service = ProcessService(
            db=db_session,
            client=mock_datajud,
            fusion_service=mock_fusion,
        )

        with patch.object(service, '_save_process_data', return_value=MagicMock(phase_source="datajud")):
            await service.get_or_update_process("0000001-01.2020.8.19.0001")

        mock_fusion.get_document_tree.assert_not_called()
```

**Step 3: Adicionar `fusion_service` ao `__init__` de `ProcessService`**

Abrir `backend/services/process_service.py`. Localizar `__init__` e adicionar o parâmetro:

```python
# Adicionar import no topo
from .fusion_service import FusionService
from .fusion_api_client import FusionResult
from .document_phase_classifier import DocumentPhaseClassifier

# Adicionar ao __init__:
def __init__(
    self,
    db: Session,
    client: Optional[DataJudClient] = None,
    phase_analyzer: Optional[PhaseAnalyzer] = None,
    fusion_service: Optional[FusionService] = None,   # NOVO
):
    self.db = db
    self.client = client or DataJudClient()
    self.phase_analyzer = phase_analyzer or PhaseAnalyzer
    self.fusion_service = fusion_service  # NOVO
```

**Step 4: Adicionar branch Fusion em `get_or_update_process`**

Localizar o trecho onde `api_data is None` (process not found no DataJud). Adicionar após:

```python
if api_data is None:
    # DataJud: not_found — tentar Fusion como segunda fonte
    if self.fusion_service:
        fusion_result = await self.fusion_service.get_document_tree(process_number)
        if fusion_result and fusion_result.movimentos:
            return await self._save_fusion_result(process_number, fusion_result)
    # não encontrado em nenhuma fonte
    await self._record_search_history(process_number, status="not_found")
    return None
```

**Step 5: Implementar `_save_fusion_result`**

Adicionar método privado em `ProcessService`:

```python
async def _save_fusion_result(
    self, process_number: str, fusion_result: FusionResult
) -> models.Process:
    """Salva resultado do Fusion no banco e retorna o processo."""
    phase = DocumentPhaseClassifier.classify(
        fusion_result.movimentos,
        fusion_result.classe_processual,
    )

    with transaction_scope(self.db):
        process = (
            self.db.query(models.Process)
            .filter(models.Process.number == process_number)
            .with_for_update()
            .first()
        )

        if not process:
            process = models.Process(
                number=process_number,
                class_nature=fusion_result.classe_processual,
                tribunal_name=fusion_result.sistema,
                phase=phase,
                phase_source=fusion_result.fonte,
            )
            self.db.add(process)
        else:
            process.phase = phase
            process.phase_source = fusion_result.fonte
            if fusion_result.classe_processual:
                process.class_nature = fusion_result.classe_processual

        self.db.flush()

    # Registrar no histórico
    self._save_search_history(
        process_number,
        status="found",
        phase_source=fusion_result.fonte,
    )

    logger.info(
        f"Processo {process_number} classificado via Fusion: "
        f"fase={phase}, fonte={fusion_result.fonte}"
    )
    return process
```

**Step 6: Rodar os testes**

```bash
python -m pytest backend/tests/test_process_service_fusion.py -v
python -m pytest backend/tests/ -v --tb=short 2>&1 | tail -30
```

Expected: novos testes PASS, sem regressão

**Step 7: Commit**

```bash
git add backend/services/process_service.py backend/tests/test_process_service_fusion.py
git commit -m "feat: integrate FusionService fallback into ProcessService"
```

---

## Task 10: Endpoint `/fusion/test` + Dependency Container

**Files:**
- Modify: `backend/services/dependency_container.py`
- Modify: `backend/main.py`

**Step 1: Registrar FusionService no container de dependências**

Abrir `backend/services/dependency_container.py`. Adicionar factory do Fusion:

```python
# Adicionar imports
from .fusion_api_client import FusionAPIClient
from .fusion_sql_client import FusionSQLClient
from .fusion_service import FusionService

def get_fusion_service() -> FusionService:
    """Factory para FusionService — lê config e constrói os clientes."""
    api_client = FusionAPIClient(
        base_url=settings.FUSION_PAV_BASE_URL,
        session_cookie=settings.FUSION_PAV_SESSION_COOKIE,
        timeout=settings.FUSION_PAV_TIMEOUT,
    )
    sql_client = None
    if settings.fusion_sql_configured:
        sql_client = FusionSQLClient(
            host=settings.FUSION_SQL_HOST,
            port=settings.FUSION_SQL_PORT,
            database=settings.FUSION_SQL_DATABASE,
            user=settings.FUSION_SQL_USER,
            password=settings.FUSION_SQL_PASSWORD,
        )
    return FusionService(sql_client=sql_client, api_client=api_client)
```

**Step 2: Adicionar endpoint de teste em `main.py`**

Abrir `backend/main.py`. Adicionar o endpoint após os endpoints de SQL existentes:

```python
@app.get("/fusion/test", tags=["fusion"])
async def test_fusion_connection(numero_cnj: str) -> dict:
    """
    Testa a integração Fusion consultando um processo pelo número CNJ.
    Útil para verificar cookie de sessão e conectividade.

    Args:
        numero_cnj: número CNJ para testar (com ou sem formatação).
    """
    fusion_service = get_fusion_service()
    result = await fusion_service.get_document_tree(numero_cnj)

    if result is None:
        return {
            "success": False,
            "message": "Processo não encontrado no Fusion/PAV",
            "numero_cnj": numero_cnj,
        }

    return {
        "success": True,
        "message": f"Processo encontrado via {result.fonte}",
        "numero_cnj": numero_cnj,
        "fonte": result.fonte,
        "classe_processual": result.classe_processual,
        "sistema": result.sistema,
        "total_movimentos": len(result.movimentos),
        "neo_id": result.neo_id,
    }
```

**Step 3: Verificar que o servidor inicia**

```bash
cd "C:\Projetos\Consulta processo"
python -m uvicorn backend.main:app --reload --port 8000
```

Expected: servidor inicia sem erro. Ctrl+C para parar.

**Step 4: Commit**

```bash
git add backend/services/dependency_container.py backend/main.py
git commit -m "feat: add /fusion/test endpoint and FusionService factory"
```

---

## Task 11: Frontend — Badge Fusion em `SearchProcess`

**Files:**
- Modify: `frontend/src/components/SearchProcess.jsx` (ou equivalente — verificar nome real)

**Step 1: Localizar onde a fase é exibida**

```bash
grep -rn "phase\|fase\|Phase" frontend/src/components/ | grep -i "display\|show\|render\|jsx" | head -20
```

**Step 2: Adicionar badge condicional**

Localizar o trecho que exibe a fase do processo. Adicionar após o texto da fase:

```jsx
{/* Badge de origem da fase */}
{process.phase_source && process.phase_source !== 'datajud' && (
  <span
    className="ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-amber-100 text-amber-800 border border-amber-300"
    title="Fase classificada via PAV/Fusion — processo não encontrado no DataJud"
  >
    Fusion
  </span>
)}
```

**Step 3: Verificar no browser**

```bash
cd "C:\Projetos\Consulta processo\frontend"
npm run dev
```

Buscar um processo que retorne `phase_source: "fusion_api"`. Verificar badge âmbar aparece.

**Step 4: Commit**

```bash
git add frontend/src/components/SearchProcess.jsx
git commit -m "feat: add Fusion badge indicator in SearchProcess results"
```

---

## Task 12: Frontend — Badge Fusion em `BulkSearch`

**Files:**
- Modify: `frontend/src/components/BulkSearch.jsx`

**Step 1: Localizar a coluna de fase no BulkSearch**

```bash
grep -n "phase\|Phase\|fase" frontend/src/components/BulkSearch.jsx | head -20
```

**Step 2: Adicionar badge na coluna de fase**

Localizar `ResultRow` ou equivalente. Após o texto da fase:

```jsx
{/* Badge Fusion para resultados em massa */}
{row.phase_source && row.phase_source !== 'datajud' && (
  <span
    className="ml-1 px-1.5 py-0.5 text-xs rounded bg-amber-100 text-amber-700 border border-amber-200"
    title={`Classificado via ${row.phase_source}`}
  >
    F
  </span>
)}
```

**Step 3: Verificar exportação CSV**

O campo `phase_source` já é incluído no schema `ProcessBulkResult` (Task 3). Verificar que o export CSV inclui a coluna.

**Step 4: Commit**

```bash
git add frontend/src/components/BulkSearch.jsx
git commit -m "feat: add Fusion indicator in BulkSearch result rows"
```

---

## Task 13: Frontend — Aba Fusion em Settings

**Files:**
- Modify: `frontend/src/components/Settings.jsx` (verificar nome real)
- Modify: `frontend/src/services/api.js`

**Step 1: Adicionar endpoint no `api.js`**

Abrir `frontend/src/services/api.js`. Adicionar:

```javascript
export const testFusionConnection = async (numeroCnj) => {
  const response = await axios.get(`${API_BASE}/fusion/test`, {
    params: { numero_cnj: numeroCnj }
  });
  return response.data;
};
```

**Step 2: Adicionar aba Fusion no Settings**

Localizar o componente Settings. Adicionar nova seção "Integração Fusion" com os campos de configuração:

```jsx
{/* Seção Fusion */}
<div className="mt-6 border-t pt-6">
  <h3 className="text-lg font-medium text-gray-900 mb-4">
    Integração Fusion/PAV
  </h3>
  <p className="text-sm text-gray-500 mb-4">
    Utilizado como fonte complementar quando o processo não é encontrado no DataJud.
  </p>

  <div className="space-y-4">
    <div>
      <label className="block text-sm font-medium text-gray-700">
        PAV Session Cookie
      </label>
      <input
        type="password"
        value={fusionCookie}
        onChange={e => setFusionCookie(e.target.value)}
        placeholder="JSESSIONID=..."
        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm text-sm"
      />
      <p className="mt-1 text-xs text-gray-400">
        Cookie de sessão do PAV (pav.procuradoria.rio)
      </p>
    </div>

    <button
      onClick={handleTestFusion}
      className="px-4 py-2 bg-amber-600 text-white rounded-md text-sm hover:bg-amber-700"
    >
      Testar Conexão Fusion
    </button>

    {fusionTestResult && (
      <div className={`text-sm p-3 rounded ${fusionTestResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
        {fusionTestResult.message}
      </div>
    )}
  </div>
</div>
```

**Step 3: Verificar no browser**

Abrir Settings → verificar seção Fusion aparece. Inserir cookie e testar com um número de processo.

**Step 4: Commit**

```bash
git add frontend/src/components/Settings.jsx frontend/src/services/api.js
git commit -m "feat: add Fusion integration settings panel with connection test"
```

---

## Task 14: Testes de Regressão e Linting

**Step 1: Rodar a suite completa de testes**

```bash
cd "C:\Projetos\Consulta processo"
python -m pytest backend/tests/ -v --tb=short 2>&1 | tail -50
```

Expected: todos os testes existentes PASS + novos testes PASS

**Step 2: Verificar lint**

```bash
npm run lint --prefix frontend
```

Expected: sem erros

**Step 3: Verificar typecheck (se configurado)**

```bash
npm run typecheck --prefix frontend 2>/dev/null || echo "typecheck não configurado"
```

**Step 4: Commit final de consolidação**

```bash
git add -A
git status  # verificar que não há arquivos sensíveis (.env) incluídos
git commit -m "feat: complete Fusion integration — dual-source fallback [Fusion Integration]"
```

---

## Resumo de Commits Esperados

1. `feat: add phase_source migration [Fusion Integration]`
2. `feat: add phase_source field to Process and SearchHistory models`
3. `feat: expose phase_source in process response schemas`
4. `feat: add Fusion/PAV configuration settings`
5. `feat: add DocumentPhaseClassifier with batismo-based phase detection`
6. `feat: add FusionAPIClient for PAV REST endpoint`
7. `feat: add FusionSQLClient stub (queries pending schema mapping)`
8. `feat: add FusionService orchestrator with SQL→API fallback`
9. `feat: integrate FusionService fallback into ProcessService`
10. `feat: add /fusion/test endpoint and FusionService factory`
11. `feat: add Fusion badge indicator in SearchProcess results`
12. `feat: add Fusion indicator in BulkSearch result rows`
13. `feat: add Fusion integration settings panel with connection test`
14. `feat: complete Fusion integration — dual-source fallback [Fusion Integration]`

---

## Checklist Final

- [ ] Migration `005_add_phase_source.sql` aplicada
- [ ] 17+ testes do `DocumentPhaseClassifier` passando
- [ ] `FusionAPIClient` testa endpoint real via `/fusion/test`
- [ ] `FusionService` falha graciosamente (SQL → API → None)
- [ ] `ProcessService` não ativa Fusion quando DataJud retorna dados
- [ ] Badge Fusion visível no frontend
- [ ] Settings com campo de cookie funcional
- [ ] Zero regressões na suite existente
- [ ] Lint frontend sem erros
- [ ] Todos os commits no branch `completar-pesquisa-externa`

---

*Plano criado em 2026-03-07. Branch: `completar-pesquisa-externa`.*
