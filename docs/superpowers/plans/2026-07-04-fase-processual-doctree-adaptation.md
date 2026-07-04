# Adaptação das Regras do `fase-processual-doctree` ao `DocumentPhaseClassifier` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Portar as regras determinísticas RE-01 a RE-12 do doctree (exceto leitura de teor) para dentro de `DocumentPhaseClassifier`, introduzindo o código de abstenção `"16"` com threshold de confiança calibrado, sem regressão na suíte de testes existente.

**Architecture:** Todas as regras novas entram como âncoras/regex adicionais e checagens de precedência dentro dos dois branches existentes (`_classify_conhecimento_traced` / `_classify_execucao_traced`) da classe única `DocumentPhaseClassifier` — nenhuma classe nova é criada (Decisão 2.3 do spec). A abstenção (`"16"`) é implementada como uma etapa de pós-processamento (`_aplicar_abstencao`) que envolve o resultado de qualquer um dos branches, usando uma lista explícita de nomes de regra elegíveis à abstenção em vez de recalibrar globalmente `_compute_confidence()` — isso evita reclassificar retroativamente regras já existentes e testadas (ver decisão §5.1 abaixo).

**Tech Stack:** Python puro (regex/`re`, `dataclasses`), pytest, SQLAlchemy (sem migração de schema), JavaScript/React (frontend, `phases.js`/`phaseColors.js`), Vitest.

---

## Decisões técnicas resolvidas nesta fase de planejamento

Estas decisões foram deixadas em aberto pelo spec (`docs/superpowers/specs/2026-07-04-fase-processual-doctree-adaptation-design.md`) e são resolvidas aqui, de forma concreta e vinculante para todas as tasks abaixo.

**1. Escala de confiança (spec §5.1) — resolvida como variante da "alternativa B" (score paralelo), implementada via allowlist de regras, não como uma função de score totalmente separada.** Verificação empírica (grep na suíte inteira): apenas 2 asserts hardcoded de `confidence` existem em toda a suíte (`test_document_phase_classifier_execucao.py:37,152`, ambos `== 0.70` para `P0_execucao_posterior_transito`, valor literal, não calculado por `_compute_confidence`). Recalibrar `_compute_confidence()` para todas as regras existentes arriscaria abstenções indevidas em massa (ex.: `P1_arquivamento` isolado, sem trânsito/sentença corroborantes, já retorna `0.70` hoje — se esse valor disparasse abstenção univesalmente, processos hoje corretamente classificados como "15" virariam "16" sem nenhuma regra RE-xx justificando a mudança, o que o spec §8.1 proíbe). A solução adotada: um dicionário `_MOTIVO_ABSTENCAO_BY_RULE` (nome de regra → motivo de abstenção) funciona como a "lista de regras elegíveis à abstenção". Só regras cujo nome está nesse dicionário — e cuja `confidence` (calculada normalmente, sem mudar a escala de nenhuma regra pré-existente) fica abaixo de `0.75` — são convertidas em `"16"`. Regras novas introduzidas nesta fase (fallbacks, trânsito inferido, conflito de classe) entram nesse dicionário com confiança deliberadamente baixa; regras pré-existentes (P1-P5, E1-E2) NÃO entram no dicionário e portanto nunca abstêm, preservando 100% o comportamento anterior.

**2. Home hierárquico do "16" (spec §6.2) — novo `Stage.CONTROLE = 6`, `substage = None`.** Análogo ao tratamento hoje dado às fases 13 (`Stage.SUSPENSAO`) e 15 (`Stage.ARQUIVAMENTO`), que também têm `substage=None`. `PHASE_TO_STAGE_SUBSTAGE["16"] = (Stage.CONTROLE, None)` e `_LEGACY_MAP` ganha entradas `(6, None, "sim"|"nao"|"na") → "16"`.

**3. Correção da consolidação tri-fonte (spec §5.2) — tratamento uniforme de `"16"`/`"Indefinido"` nas 3 fontes**, mais uma 5ª regra: se todas as fontes com dado válido abstiveram (`"16"`), o consolidado também é `"16"` (modo `"todas_abstencao"`).

**4. Extensão do `reclassify_hierarchical.py` (spec §8.3) — reconstruir `FusionMovimento` a partir dos digests já persistidos em `raw_data.__meta__` (`fusion_movements`, `pav_tree_documents`) e re-executar `classify_with_trace()`**, atrás de uma nova flag `--full-reclassify` (opt-in, para não alterar o comportamento padrão do script). Limitação documentada: o digest de `pav_tree_documents` só grava `{"name", "date"}` (não `tipo_cnj`/`descricao`), então a reconstrução da Árvore PAV é lossy — aceitável para o diff de impacto pré-rollout, não para reclassificação definitiva.

**Nota sobre escopo do RE-01 (relevante para a Task 12 — importação de `testes-minimos.json`):** a Tabela regra-a-regra do spec (§3) descreve a mudança de RE-01 apenas como uma separação de responsabilidades dentro de `_is_classe_execucao` (bifurcação por classe vs. trava RE-11) — não como um detector de título executivo a partir do CONTEÚDO da petição inicial quando `classe_processual` está ausente/vazia. Esta adaptação **não** implementa esse detector de conteúdo. Isso significa que, dos 14 casos reais em `testes-minimos.json` (ver Task 12), alguns casos sintéticos que dependem de inferir domínio (execução vs. conhecimento) apenas do texto da árvore, sem qualquer `classe_processual`, permanecem fora do alcance desta fase e são marcados `xfail` com justificativa — não é lacuna silenciosa, é escolha documentada.

**Nota sobre `VALID_PHASE_CODES` (`backend/constants.py:2`) — deliberadamente NÃO alterado.** Esse conjunto (`"01"`-`"15"`) valida o endpoint `POST /processes/{number}/phase-correction`, usado por um humano para CORRIGIR a fase que o sistema errou. Um humano corrigindo manualmente sempre aponta para uma fase definitiva (01-15); nunca faria sentido submeter `"16"` como a fase corrigida, já que `"16"` significa exatamente "ainda não sei, precisa de revisão humana" — o próprio humano fazendo a correção É a revisão. Portanto este arquivo fica fora do escopo das tasks abaixo.

---

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `backend/services/document_phase_classifier.py` | Modificado extensivamente: novo campo `autor` em `FusionMovimento`; novos campos `fase_provavel`/`motivo_abstencao` em `ClassificationResult`; novas âncoras regex (RE-04, RE-05, RE-06, RE-03.2, RE-11, RE-12); novo filtro de ruído RE-12; nova etapa de abstenção RE-07; novo parâmetro `abstention_resolver` reservado (§7). |
| `backend/services/hierarchical_classification.py` | Modificado: novo `Stage.CONTROLE = 6`; nova entrada `PHASE_TO_STAGE_SUBSTAGE["16"]`; novas entradas em `_LEGACY_MAP` para `(6, None, *) → "16"`. |
| `backend/services/process_service.py` | Modificado: `_consolidar_tres_fontes()` ganha tratamento uniforme de `"16"`/`"Indefinido"` e nova regra de abstenção consolidada; `_extrair_hierarquia_da_fonte()` ganha suporte ao modo `"todas_abstencao"`. |
| `backend/scripts/reclassify_hierarchical.py` | Modificado: nova flag `--full-reclassify` que reconstrói movimentos e re-executa `classify_with_trace()`. |
| `frontend/src/constants/phases.js` | Modificado: nova entrada `INDETERMINADO_REVISAO_HUMANA` (código `"16"`) em `VALID_PHASES`; novo `Stage 6` em `STAGES`; nova entrada em `LEGACY_PHASE_TO_HIERARCHY`; `hierarchyToLegacyPhase` trata `stage === 6`. |
| `frontend/src/utils/phaseColors.js` | Modificado: nova cor (`cyan`) no `colorMap` de `getPhaseColorClasses`/`getPhaseProgressBarClasses`/`getStageColorClasses`/`getStageProgressBarClasses`. |
| `backend/tests/test_document_phase_classifier_data_model.py` | Criado (Task 1): testa os novos campos de dados. |
| `backend/tests/test_document_phase_classifier_autoria.py` | Criado (Task 2): testa `_infer_autor`, `_autor_confidence_delta` e a integração na regra de sentença (RE-04). |
| `backend/tests/test_document_phase_classifier_despacho_ruido.py` | Criado (Task 3): testa o filtro de ruído RE-12. |
| `backend/tests/test_document_phase_classifier_conversao_renda.py` | Criado (Task 4): testa a âncora de conversão em renda (RE-06/RE-03.1) em ambos os branches. |
| `backend/tests/test_document_phase_classifier_suspensao_parcial.py` | Criado (Task 5): testa a âncora de suspensão parcial (RE-03.2). |
| `backend/tests/test_document_phase_classifier_transito_inferido.py` | Criado (Task 6): testa o trânsito inferido com teto de confiança (RE-05). |
| `backend/tests/test_document_phase_classifier_conflito_classe.py` | Criado (Task 7): testa o conflito classe executiva × peças cognitivas (RE-11). |
| `backend/tests/test_document_phase_classifier_abstencao.py` | Criado (Task 8): testa o threshold de abstenção (RE-07) e a propagação de `fase_provavel`/`motivo_abstencao`. |
| `backend/tests/test_consolidar_tres_fontes.py` | Criado (Task 9): primeira cobertura de teste dedicada a `_consolidar_tres_fontes` (não existia nenhuma). |
| `backend/tests/test_hierarchical_classification.py` | Modificado (Tasks 9, 10): novo caso em `TestExtrairHierarquiaDaFonte`; `test_all_legacy_map_entries_covered` atualizado com justificativa; nova classe `TestStageControle`. |
| `backend/tests/test_document_phase_classifier_doctree_cases.py` | Criado (Task 12): importa e roda os 14 casos de `fase-processual-doctree/tests/testes-minimos.json`. |
| `frontend/src/tests/phases16.test.js` | Criado (Task 15): testa a nova entrada de fase "16" no frontend. |

---

## Task 1: Modelo de dados — `autor`, `fase_provavel`, `motivo_abstencao`

**Files:**
- Modify: `backend/services/document_phase_classifier.py:29-85`
- Test: `backend/tests/test_document_phase_classifier_data_model.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para os novos campos de dados introduzidos pela adaptação doctree:
FusionMovimento.autor, ClassificationResult.fase_provavel/motivo_abstencao.
"""
from datetime import datetime

from backend.services.document_phase_classifier import (
    FusionMovimento, ClassificationResult,
)


class TestFusionMovimentoAutor:
    def test_autor_e_opcional_com_default_none(self):
        mov = FusionMovimento(
            data=datetime(2024, 1, 1), tipo_local="Sentença", tipo_cnj="", descricao="",
        )
        assert mov.autor is None

    def test_autor_pode_ser_informado_explicitamente(self):
        mov = FusionMovimento(
            data=datetime(2024, 1, 1), tipo_local="Sentença", tipo_cnj="",
            descricao="", autor="juizo_1grau",
        )
        assert mov.autor == "juizo_1grau"


class TestClassificationResultAbstencao:
    def test_fase_provavel_e_motivo_abstencao_sao_opcionais(self):
        resultado = ClassificationResult(
            phase="01", branch="conhecimento", classe_normalizada="acao civel",
            total_movimentos=0, rule_applied="empty_list_fallback",
        )
        assert resultado.fase_provavel is None
        assert resultado.motivo_abstencao is None

    def test_to_dict_inclui_fase_provavel_e_motivo_abstencao(self):
        resultado = ClassificationResult(
            phase="16", branch="conhecimento", classe_normalizada="acao civel",
            total_movimentos=3, rule_applied="P6_fallback_antes_sentenca",
            fase_provavel="01", motivo_abstencao="opacidade",
        )
        d = resultado.to_dict()
        assert d["fase_provavel"] == "01"
        assert d["motivo_abstencao"] == "opacidade"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_data_model.py -v`
Expected: FAIL com `TypeError: FusionMovimento.__init__() got an unexpected keyword argument 'autor'` (e a mesma classe de erro para `fase_provavel`/`motivo_abstencao` em `ClassificationResult`).

- [ ] **Step 3: Write minimal implementation**

Edit `backend/services/document_phase_classifier.py`. Old:

```python
@dataclass
class FusionMovimento:
    data: datetime
    tipo_local: str      # "batismo" — tipoMovimentoLocal
    tipo_cnj: str        # tipoMovimentoCNJ
    descricao: str = ""  # campo "descricao" da API — texto descritivo mais rico
```

New:

```python
@dataclass
class FusionMovimento:
    data: datetime
    tipo_local: str      # "batismo" — tipoMovimentoLocal
    tipo_cnj: str        # tipoMovimentoCNJ
    descricao: str = ""  # campo "descricao" da API — texto descritivo mais rico
    autor: Optional[str] = None  # RE-04 — "parte" | "serventia" | "juizo_1grau" |
                                  # "tribunal_2grau" | "tribunal_superior" | "terceiro" | None
```

Old:

```python
    # Classificação hierárquica (3 campos)
    stage: int = 1
    substage: Optional[str] = None
    transit_julgado: str = "nao"

    def to_dict(self) -> dict:
        """Retorna dict serializável para JSON."""
        return {
            "phase": self.phase,
            "branch": self.branch,
            "classe_normalizada": self.classe_normalizada,
            "total_movimentos": self.total_movimentos,
            "rule_applied": self.rule_applied,
            "decisive_movement": self.decisive_movement,
            "decisive_movement_date": self.decisive_movement_date,
            "anchor_matches": self.anchor_matches,
            "confidence": self.confidence,
            "context_summary": self.context_summary,
            "stage": self.stage,
            "substage": self.substage,
            "transit_julgado": self.transit_julgado,
        }
```

New:

```python
    # Classificação hierárquica (3 campos)
    stage: int = 1
    substage: Optional[str] = None
    transit_julgado: str = "nao"

    # RE-07 — só preenchidos quando phase == "16"
    fase_provavel: Optional[str] = None
    motivo_abstencao: Optional[str] = None
    # motivo_abstencao (enum): opacidade | transito_nao_certificado |
    # contradicao_documental | polaridade_indeterminada | pendencia_financeira |
    # confianca_insuficiente

    def to_dict(self) -> dict:
        """Retorna dict serializável para JSON."""
        return {
            "phase": self.phase,
            "branch": self.branch,
            "classe_normalizada": self.classe_normalizada,
            "total_movimentos": self.total_movimentos,
            "rule_applied": self.rule_applied,
            "decisive_movement": self.decisive_movement,
            "decisive_movement_date": self.decisive_movement_date,
            "anchor_matches": self.anchor_matches,
            "confidence": self.confidence,
            "context_summary": self.context_summary,
            "stage": self.stage,
            "substage": self.substage,
            "transit_julgado": self.transit_julgado,
            "fase_provavel": self.fase_provavel,
            "motivo_abstencao": self.motivo_abstencao,
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_data_model.py -v`
Expected: PASS (4 testes)

- [ ] **Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier_data_model.py
git commit -m "feat: add autor field to FusionMovimento and abstention fields to ClassificationResult"
```

---

## Task 2: RE-04 — Autoria como sinal

Escopo desta task: implementar `_infer_autor()` (inferência a partir do texto quando `autor` não foi informado) e `_autor_confidence_delta()` (ajuste de confiança), e integrar esse ajuste em UM ponto de decisão concreto (`P3_sentenca_sem_transito`, no branch de conhecimento), como demonstração funcional do sinal. Per spec: "autoria usada como desempate e reforço de confiança, não como âncora isolada nova" — não é adicionada como gatilho de fase em nenhum outro ponto nesta fase.

**Files:**
- Modify: `backend/services/document_phase_classifier.py`
- Test: `backend/tests/test_document_phase_classifier_autoria.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para RE-04 — Autoria como sinal (inferência + reforço de confiança).
"""
from datetime import datetime

from backend.services.document_phase_classifier import (
    DocumentPhaseClassifier, FusionMovimento,
)


def _mov(tipo_local: str, data_str: str = "2024-01-01", autor=None, descricao: str = "") -> FusionMovimento:
    return FusionMovimento(
        data=datetime.strptime(data_str, "%Y-%m-%d"),
        tipo_local=tipo_local, tipo_cnj="", descricao=descricao, autor=autor,
    )


class TestInferAutor:
    def test_autor_explicito_tem_prioridade(self):
        mov = _mov("Petição", autor="tribunal_2grau")
        assert DocumentPhaseClassifier._infer_autor(mov) == "tribunal_2grau"

    def test_infere_serventia_de_certidao(self):
        mov = _mov("Certidão de Trânsito em Julgado")
        assert DocumentPhaseClassifier._infer_autor(mov) == "serventia"

    def test_infere_juizo_1grau_de_sentenca(self):
        mov = _mov("Sentença")
        assert DocumentPhaseClassifier._infer_autor(mov) == "juizo_1grau"

    def test_infere_tribunal_2grau_de_acordao(self):
        mov = _mov("Acórdão")
        assert DocumentPhaseClassifier._infer_autor(mov) == "tribunal_2grau"

    def test_infere_parte_de_peticao_de_razoes(self):
        mov = _mov("Razões de Apelação")
        assert DocumentPhaseClassifier._infer_autor(mov) == "parte"

    def test_sem_sinal_retorna_none(self):
        mov = _mov("Andamento Processual")
        assert DocumentPhaseClassifier._infer_autor(mov) is None


class TestAutorConfidenceDelta:
    def test_autor_confirma_regra_aumenta_confianca(self):
        assert DocumentPhaseClassifier._autor_confidence_delta("juizo_1grau", "juizo_1grau") == 0.05

    def test_autor_contradiz_regra_reduz_confianca(self):
        assert DocumentPhaseClassifier._autor_confidence_delta("juizo_1grau", "parte") == -0.05

    def test_autor_ausente_nao_altera_confianca(self):
        assert DocumentPhaseClassifier._autor_confidence_delta("juizo_1grau", None) == 0.0


class TestAutoriaWiredNaSentenca:
    def test_autor_explicito_contraditorio_reduz_confianca_da_sentenca(self):
        """Sentença com autor=parte (contraditório) tem confiança reduzida vs. baseline."""
        movs_base = [_mov("Petição Inicial", "2024-01-01"), _mov("Sentença", "2024-06-01")]
        resultado_base = DocumentPhaseClassifier.classify_with_trace(movs_base, "Ação Cível")

        movs_contraditorio = [
            _mov("Petição Inicial", "2024-01-01"),
            _mov("Sentença", "2024-06-01", autor="parte"),
        ]
        resultado_contraditorio = DocumentPhaseClassifier.classify_with_trace(movs_contraditorio, "Ação Cível")

        assert resultado_base.phase == "02"
        assert resultado_contraditorio.phase == "02"
        assert resultado_contraditorio.confidence < resultado_base.confidence
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_autoria.py -v`
Expected: FAIL com `AttributeError: type object 'DocumentPhaseClassifier' has no attribute '_infer_autor'`

- [ ] **Step 3: Write minimal implementation**

Add near the top of `backend/services/document_phase_classifier.py`, right after the `_CLASSES_EXECUCAO`/`_is_classe_execucao` block (before `class DocumentPhaseClassifier:`):

```python
# ---------------------------------------------------------------------------
# RE-04 — Autoria como sinal
# ---------------------------------------------------------------------------

_AUTOR_SIGNAIS = [
    (re.compile(r'(certidao|termo|juntada|mandado|\bar\b|edital)'), "serventia"),
    (re.compile(r'(sentenca|decisao)'), "juizo_1grau"),
    (re.compile(r'(acordao|voto|ementa|relator|camara|turma)'), "tribunal_2grau"),
    (re.compile(r'(stj|stf|ministro|recurso\s+especial|extraordinario)'), "tribunal_superior"),
    (re.compile(r'(peticao|razoes|contrarrazoes|manifestacao|embargos)'), "parte"),
    (re.compile(r'(laudo|parecer\s+tecnico|oficio)'), "terceiro"),
]
```

Add these two classmethods inside `class DocumentPhaseClassifier:`, right before `_build_context_summary`:

```python
    @classmethod
    def _infer_autor(cls, movimento: "FusionMovimento") -> Optional[str]:
        """
        RE-04: infere o autor da peça a partir do texto disponível quando o
        campo `autor` não foi explicitamente informado.

        Prioridade: campo explícito > inferência por texto
        (tipo_local > tipo_cnj > descricao) > None.
        """
        if movimento.autor is not None:
            return movimento.autor
        for texto in (movimento.tipo_local, movimento.tipo_cnj, movimento.descricao):
            texto_norm = cls._normalize(texto)
            if not texto_norm:
                continue
            for pattern, autor in _AUTOR_SIGNAIS:
                if pattern.search(texto_norm):
                    return autor
        return None

    @classmethod
    def _autor_confidence_delta(cls, esperado: str, atual: Optional[str]) -> float:
        """
        RE-04: pequeno ajuste de confiança quando o autor da peça decisiva
        confirma (+0.05) ou contradiz (-0.05) o autor esperado para a regra.
        Retorna 0.0 quando não há autor disponível (nem explícito, nem inferível).
        """
        if atual is None:
            return 0.0
        if atual == esperado:
            return 0.05
        return -0.05
```

Now wire it into `P3_sentenca_sem_transito`. Old (inside `_classify_conhecimento_traced`):

```python
            # Sentença sem remessa posterior nem trânsito → fase 02
            rule = "P3_sentenca_sem_transito"
            nome, data = _decisive(sentenca_idx)
            return ClassificationResult(
                "02", "conhecimento", classe_norm, total,
                rule, nome, data, anchors,
                cls._compute_confidence(anchors, context, rule), context,
            )
```

New:

```python
            # Sentença sem remessa posterior nem trânsito → fase 02
            rule = "P3_sentenca_sem_transito"
            nome, data = _decisive(sentenca_idx)
            confidence = cls._compute_confidence(anchors, context, rule)
            autor_sentenca = cls._infer_autor(ordered[sentenca_idx])
            confidence = max(0.0, min(1.0, confidence + cls._autor_confidence_delta("juizo_1grau", autor_sentenca)))
            return ClassificationResult(
                "02", "conhecimento", classe_norm, total,
                rule, nome, data, anchors,
                confidence, context,
            )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_autoria.py -v`
Expected: PASS (9 testes)

- [ ] **Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier_autoria.py
git commit -m "feat: infer autor from text and use it to reinforce sentenca confidence (RE-04)"
```

---

## Task 3: RE-12 — Despacho genérico como ruído (filtro + refatoração dos scans de âncora)

**Files:**
- Modify: `backend/services/document_phase_classifier.py`
- Test: `backend/tests/test_document_phase_classifier_despacho_ruido.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para RE-12 (primeira metade) — Despacho genérico é ruído por metadado,
não pode ser o movimento decisivo de nenhuma âncora.
"""
from datetime import datetime

from backend.services.document_phase_classifier import (
    DocumentPhaseClassifier, FusionMovimento,
)


def _mov(tipo_local: str, data_str: str, descricao: str = "") -> FusionMovimento:
    return FusionMovimento(
        data=datetime.strptime(data_str, "%Y-%m-%d"),
        tipo_local=tipo_local, tipo_cnj="", descricao=descricao,
    )


class TestDespachoGenericoEhIgnorado:
    def test_despacho_generico_mais_recente_nao_e_decisivo(self):
        """Sentença seguida de Despacho genérico → continua fase 02, Despacho não é decisivo."""
        movs = [
            _mov("Petição Inicial", "2024-01-10"),
            _mov("Sentença", "2024-04-20"),
            _mov("Despacho", "2024-06-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Cível")
        assert resultado.phase == "02"
        assert resultado.decisive_movement != "Despacho"

    def test_despacho_com_numero_tambem_e_ruido(self):
        """'Despacho_123' (variante numérica) também é tratado como ruído."""
        movs = [
            _mov("Petição Inicial", "2024-01-10"),
            _mov("Sentença", "2024-04-20"),
            _mov("Despacho_123", "2024-06-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Cível")
        assert resultado.phase == "02"

    def test_despacho_com_texto_especifico_nao_e_ruido(self):
        """Despacho com nome_arquivo/descrição específica (não genérica) NÃO é ruído."""
        movs = [
            _mov("Petição Inicial", "2018-02-01"),
            _mov("Despacho", "2020-03-05", descricao="suspensao art 40 lef arquivo provisorio sem baixa"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Execução Fiscal")
        # A descrição específica ("suspensao...") deve poder ser a âncora decisiva
        # mesmo que tipo_local seja "despacho" — só é ruído se TODOS os campos
        # disponíveis normalizarem para "despacho" puro.
        assert resultado.phase == "11"


class TestIsRuidoDespachoGenerico:
    def test_despacho_puro_em_todos_os_campos_e_ruido(self):
        assert DocumentPhaseClassifier._is_ruido_despacho_generico("Despacho", "", "despacho") is True

    def test_despacho_numerico_e_ruido(self):
        assert DocumentPhaseClassifier._is_ruido_despacho_generico("despacho_123", "", "") is True

    def test_despacho_com_descricao_especifica_nao_e_ruido(self):
        assert DocumentPhaseClassifier._is_ruido_despacho_generico("Despacho", "", "suspensao art 40 lef") is False

    def test_texto_nao_despacho_nao_e_ruido(self):
        assert DocumentPhaseClassifier._is_ruido_despacho_generico("Sentença", "", "") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_despacho_ruido.py -v`
Expected: FAIL com `AttributeError: type object 'DocumentPhaseClassifier' has no attribute '_is_ruido_despacho_generico'`

- [ ] **Step 3: Write minimal implementation**

Add near the other anchor regex definitions in `backend/services/document_phase_classifier.py` (right after `_CLASSES_EXECUCAO`/`_is_classe_execucao`, before the `_AUTOR_SIGNAIS` block added in Task 2):

```python
# RE-12 — Despacho genérico (ruído por metadado, nunca decisivo)
_ANCHOR_DESPACHO_GENERICO = re.compile(r'^despacho(_\d+)?$')
```

Add this classmethod right before `_build_context_summary` (before the `_infer_autor` block added in Task 2, i.e. this becomes the first of the new helper classmethods):

```python
    @classmethod
    def _is_ruido_despacho_generico(cls, local: str, cnj: str, desc: str) -> bool:
        """
        RE-12: um documento é ruído por metadado quando TODOS os campos de
        texto disponíveis (tipo_local, tipo_cnj, descricao — já esperados
        NORMALIZADOS aqui) reduzem-se exatamente a "despacho" ou variante
        numérica ("despacho_123"). Se qualquer campo disponível trouxer texto
        mais específico, o documento NÃO é ruído (o sinal deve vir desse texto).
        """
        candidatos = [t for t in (local, cnj, desc) if t]
        if not candidatos:
            return False
        return all(_ANCHOR_DESPACHO_GENERICO.match(t) for t in candidatos)
```

Now refactor the anchor-scanning section of `_classify_conhecimento_traced`. Old:

```python
        def _any_match(pattern, local: str, cnj: str, desc: str, use_match: bool = False) -> bool:
            """Verifica se o padrão bate em tipo_local, tipo_cnj OU descricao."""
            fn = pattern.match if use_match else pattern.search
            return bool(fn(local)) or bool(cnj and fn(cnj)) or bool(desc and fn(desc))

        # Escaneia todas as âncoras considerando os três campos
        arq_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_ARQUIVAMENTO, l, c, d)), None
        )
        transito_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_TRANSITO, l, c, d)), None
        )
        sentenca_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_SENTENCA, l, c, d, use_match=True)), None
        )
        # Desfecho de julgamento via descrição (Procedência, Improcedência, etc.)
        sentenca_resultado_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_SENTENCA_RESULTADO, l, c, d)), None
        )
        # Sentença efetiva: o mais recente entre sentença literal e resultado de julgamento
        if sentenca_idx is not None and sentenca_resultado_idx is not None:
            sentenca_idx = min(sentenca_idx, sentenca_resultado_idx)  # menor idx = mais recente em DESC
        elif sentenca_resultado_idx is not None:
            sentenca_idx = sentenca_resultado_idx
        # Remessa: sistema de 3 níveis
        remessa_superior_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_REMESSA_SUPERIOR, l, c, d)), None
        )
        remessa_lateral_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_REMESSA_LATERAL, l, c, d)), None
        )
        remessa_generica_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple)
             if _any_match(_ANCHOR_REMESSA_GENERICA, l, c, d)
             and not (remessa_superior_idx is not None and remessa_superior_idx == i)
             and not (remessa_lateral_idx is not None and remessa_lateral_idx == i)), None
        )

        acordao_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_ACORDAO, l, c, d)), None
        )
```

New:

```python
        def _any_match(pattern, local: str, cnj: str, desc: str, use_match: bool = False) -> bool:
            """Verifica se o padrão bate em tipo_local, tipo_cnj OU descricao."""
            fn = pattern.match if use_match else pattern.search
            return bool(fn(local)) or bool(cnj and fn(cnj)) or bool(desc and fn(desc))

        # RE-12: máscara de ruído (despacho genérico nunca é decisivo)
        ruido_mask = [cls._is_ruido_despacho_generico(l, c, d) for l, c, d in nomes_triple]

        def _scan(pattern, use_match: bool = False):
            """Busca a primeira ocorrência (mais recente) do padrão, ignorando ruído RE-12."""
            return next(
                (i for i, (l, c, d) in enumerate(nomes_triple)
                 if not ruido_mask[i] and _any_match(pattern, l, c, d, use_match)),
                None
            )

        # Escaneia todas as âncoras considerando os três campos
        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        transito_idx = _scan(_ANCHOR_TRANSITO)
        sentenca_idx = _scan(_ANCHOR_SENTENCA, use_match=True)
        # Desfecho de julgamento via descrição (Procedência, Improcedência, etc.)
        sentenca_resultado_idx = _scan(_ANCHOR_SENTENCA_RESULTADO)
        # Sentença efetiva: o mais recente entre sentença literal e resultado de julgamento
        if sentenca_idx is not None and sentenca_resultado_idx is not None:
            sentenca_idx = min(sentenca_idx, sentenca_resultado_idx)  # menor idx = mais recente em DESC
        elif sentenca_resultado_idx is not None:
            sentenca_idx = sentenca_resultado_idx
        # Remessa: sistema de 3 níveis
        remessa_superior_idx = _scan(_ANCHOR_REMESSA_SUPERIOR)
        remessa_lateral_idx = _scan(_ANCHOR_REMESSA_LATERAL)
        remessa_generica_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple)
             if not ruido_mask[i]
             and _any_match(_ANCHOR_REMESSA_GENERICA, l, c, d)
             and not (remessa_superior_idx is not None and remessa_superior_idx == i)
             and not (remessa_lateral_idx is not None and remessa_lateral_idx == i)), None
        )

        acordao_idx = _scan(_ANCHOR_ACORDAO)
```

Further down in the same method, old:

```python
        suspenso_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_SUSPENSO, l, c, d)), None
        )
        execucao_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_EXECUCAO, l, c, d)), None
        )
```

New:

```python
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)
        execucao_idx = _scan(_ANCHOR_EXECUCAO)
```

Now do the same refactor in `_classify_execucao_traced`. Old:

```python
        def _any_match(pattern, local: str, cnj: str, desc: str, use_match: bool = False) -> bool:
            """Verifica se o padrão bate em tipo_local, tipo_cnj OU descricao."""
            fn = pattern.match if use_match else pattern.search
            return bool(fn(local)) or bool(cnj and fn(cnj)) or bool(desc and fn(desc))

        arq_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_ARQUIVAMENTO, l, c, d)), None
        )
        suspenso_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_SUSPENSO, l, c, d)), None
        )
```

New:

```python
        def _any_match(pattern, local: str, cnj: str, desc: str, use_match: bool = False) -> bool:
            """Verifica se o padrão bate em tipo_local, tipo_cnj OU descricao."""
            fn = pattern.match if use_match else pattern.search
            return bool(fn(local)) or bool(cnj and fn(cnj)) or bool(desc and fn(desc))

        # RE-12: máscara de ruído (despacho genérico nunca é decisivo)
        ruido_mask = [cls._is_ruido_despacho_generico(l, c, d) for l, c, d in nomes_triple]

        def _scan(pattern, use_match: bool = False):
            """Busca a primeira ocorrência (mais recente) do padrão, ignorando ruído RE-12."""
            return next(
                (i for i, (l, c, d) in enumerate(nomes_triple)
                 if not ruido_mask[i] and _any_match(pattern, l, c, d, use_match)),
                None
            )

        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_despacho_ruido.py -v`
Expected: PASS (7 testes)

- [ ] **Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier_despacho_ruido.py
git commit -m "feat: treat bare 'Despacho' documents as noise, never decisive (RE-12)"
```

---

## Task 4: RE-06 / RE-03.1 — Conversão em renda (ambos os branches)

Escopo: nova âncora de conversão em renda com verificação de polaridade positiva, verificada ANTES do arquivamento em ambos os branches (RE-03.1: "14 > 15"). No branch de conhecimento, isso é implementado como um novo override de domínio análogo ao já existente `P0_execucao_posterior_transito` (que já promove um resultado do branch de conhecimento para `branch="execucao"`, `phase="10"`, mesmo sem `classe_processual` indicar execução) — não é um novo gate de domínio genérico (RE-01), é a extensão do MESMO padrão já existente para um segundo caso de transição de domínio.

**Files:**
- Modify: `backend/services/document_phase_classifier.py`
- Test: `backend/tests/test_document_phase_classifier_conversao_renda.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para RE-06 / RE-03.1 — Conversão em renda (fase 14), precedência sobre
arquivamento posterior, em ambos os branches (conhecimento e execução).
"""
from datetime import datetime

from backend.services.document_phase_classifier import (
    DocumentPhaseClassifier, FusionMovimento,
)


def _mov(tipo_local: str, data_str: str, descricao: str = "") -> FusionMovimento:
    return FusionMovimento(
        data=datetime.strptime(data_str, "%Y-%m-%d"),
        tipo_local=tipo_local, tipo_cnj="", descricao=descricao,
    )


class TestConversaoRendaBranchConhecimento:
    """Classe processual não informada (''): roteia para o branch de conhecimento,
    onde a âncora de conversão atua como override de domínio (P0c), análogo ao
    P0 já existente para execução posterior a trânsito."""

    def test_conversao_real_t01_retorna_fase_14(self):
        """Caso real anonimizado (T-01 de testes-minimos.json)."""
        movs = [
            _mov("Capa", "2025-01-16"),
            _mov("Petição Inicial", "2025-01-16"),
            _mov("Mandado de Pagamento", "2025-12-15"),
            _mov("Comprovante de Resgate MRJ", "2025-12-15", descricao="comprovanteResgatePdf"),
            _mov("Aprovação", "2025-12-17", descricao="Dam conversão 11-002219-2025"),
            _mov("Comprovante de Resgate MRJ", "2025-12-18", descricao="CONTA BB 2"),
            _mov("Despacho", "2026-01-06"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "")
        assert resultado.phase == "14"
        assert resultado.confidence >= 0.75

    def test_mandado_pagamento_sozinho_nao_basta(self):
        """Mandado de pagamento sem termo de polaridade positiva NÃO ativa a fase 14."""
        movs = [
            _mov("Petição Inicial", "2024-02-01"),
            _mov("Mandado de Pagamento", "2025-06-10", descricao="mandado pagamento 12345"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "")
        assert resultado.phase != "14"

    def test_precatorio_pago_pelo_municipio_nunca_e_14(self):
        """Polaridade negativa (satisfação CONTRA o ente) jamais é fase 14 (F-09)."""
        movs = [
            _mov("Petição", "2019-05-02", descricao="cumprimento de sentenca contra o municipio"),
            _mov("Ofício", "2021-03-10", descricao="oficio requisitorio precatorio"),
            _mov("Comprovante", "2024-07-01", descricao="deposito pagamento precatorio"),
            _mov("Sentença", "2024-09-12", descricao="extincao art 924 II"),
            _mov("Certidão", "2024-10-01", descricao="baixa definitiva"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "")
        assert resultado.phase == "15"
        assert resultado.phase != "14"


class TestConversaoRendaBranchExecucao:
    def test_conversao_prevalece_sobre_arquivamento_posterior(self):
        """Conversão em renda seguida de arquivamento posterior → mantém fase 14 (RE-03.1)."""
        movs = [
            _mov("Petição", "2024-01-01", descricao="cumprimento de sentenca"),
            _mov("Termo de Conversão", "2024-06-01", descricao="conversao em renda em favor do municipio"),
            _mov("Certidão", "2024-08-01", descricao="arquivamento"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Cumprimento de Sentença")
        assert resultado.phase == "14"
        assert resultado.rule_applied == "E0_conversao_renda"

    def test_arrecadacao_parcial_mantem_fase_10_com_marcador(self):
        """Arrecadação parcial (termo neutro) com execução em curso → fase 10 + marcador."""
        movs = [
            _mov("Petição", "2024-01-01", descricao="cumprimento de sentenca"),
            _mov("Penhora", "2024-04-01"),
            _mov("Mandado de Pagamento", "2024-06-01", descricao="levantamento parcial"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Cumprimento de Sentença")
        assert resultado.phase == "10"
        assert resultado.anchor_matches.get("arrecadacao_parcial") is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_conversao_renda.py -v`
Expected: FAIL — `test_conversao_real_t01_retorna_fase_14` obtém `phase == "01"` (fallback conservador) em vez de `"14"`; `test_conversao_prevalece_sobre_arquivamento_posterior` obtém `phase == "15"` (E1_arquivamento, pois arquivamento já é decisivo hoje) em vez de `"14"`.

- [ ] **Step 3: Write minimal implementation**

Add two new anchor regexes right after `_ANCHOR_EXECUCAO` in `backend/services/document_phase_classifier.py`:

```python
# RE-06 — Conversão em renda: polaridade positiva (fase 14)
_ANCHOR_CONVERSAO_POSITIVA = re.compile(
    r'(dam\s+de?\s+conversao|conversao\s+em\s+renda|resgate\s+mrj|'
    r'em\s+favor\s+d[oa]\s+(municipio|mrj|fazenda)|'
    r'satisfacao\s+do\s+credito\s+fiscal)'
)

# RE-06 — Movimentação financeira neutra (não conta para 14 sozinha)
_ANCHOR_CONVERSAO_NEUTRA = re.compile(
    r'(mandado\s+de\s+pagamento|alvara|levantamento|transferencia|resgate)'
)
```

Add `conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)` right after `acordao_idx = _scan(_ANCHOR_ACORDAO)` inside `_classify_conhecimento_traced` (added by Task 3). Old:

```python
        acordao_idx = _scan(_ANCHOR_ACORDAO)
```

New:

```python
        acordao_idx = _scan(_ANCHOR_ACORDAO)
        conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)
```

Add `"conversao_renda": conversao_idx` to the `anchors` dict. Old:

```python
        anchors = {
            "arquivamento": arq_idx,
            "transito": transito_idx,
            "sentenca": sentenca_idx,
            "remessa": remessa_idx,
            "acordao": acordao_idx,
            "suspenso": suspenso_idx,
            "execucao": execucao_idx,
        }
```

New:

```python
        anchors = {
            "arquivamento": arq_idx,
            "transito": transito_idx,
            "sentenca": sentenca_idx,
            "remessa": remessa_idx,
            "acordao": acordao_idx,
            "suspenso": suspenso_idx,
            "execucao": execucao_idx,
            "conversao_renda": conversao_idx,
        }
```

Insert the new override check as the FIRST rule checked (before `P1: Arquivamento`), so conversion prevails over any subsequent arquivamento anchor. Old:

```python
        total = len(movimentos)
        context = cls._build_context_summary(ordered, nomes)

        # P1: Arquivamento — somente se NÃO há atividade substancial posterior
        if arq_idx is not None:
```

New:

```python
        total = len(movimentos)
        context = cls._build_context_summary(ordered, nomes)

        # P0c: Conversão em renda — prevalece sobre arquivamento posterior (RE-03.1/RE-06).
        # Análogo ao override de domínio já existente em P0 (execução posterior a
        # trânsito): promove o resultado a branch="execucao" mesmo vindo do
        # branch de conhecimento, quando a árvore contém sinal de polaridade positiva.
        if conversao_idx is not None:
            rule = "P0c_conversao_renda"
            nome, data = _decisive(conversao_idx)
            confidence = cls._compute_confidence(anchors, context, rule)
            return ClassificationResult(
                "14", "execucao", classe_norm, total,
                rule, nome, data, anchors,
                confidence, context,
            )

        # P1: Arquivamento — somente se NÃO há atividade substancial posterior
        if arq_idx is not None:
```

Now do the equivalent in `_classify_execucao_traced`. Add the two new scans after `suspenso_idx = _scan(_ANCHOR_SUSPENSO)` (added by Task 3). Old:

```python
        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)

        anchors = {
            "arquivamento": arq_idx,
            "suspenso": suspenso_idx,
        }
```

New:

```python
        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)
        conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)
        conversao_neutra_idx = _scan(_ANCHOR_CONVERSAO_NEUTRA)

        anchors = {
            "arquivamento": arq_idx,
            "suspenso": suspenso_idx,
            "conversao_renda": conversao_idx,
            "arrecadacao_parcial": (
                conversao_idx is None and conversao_neutra_idx is not None
                and context_execucao_ok  # placeholder removido abaixo
            ),
        }
```

Replace that last `anchors` block (it references `context_execucao_ok` which does not exist yet — this is corrected in the same edit before the file is saved) with the following, which computes `context` first. Old (replace the whole block above, including the erroneous placeholder, with this final version — the intermediate step above is shown only to make the diff from Task 3's state explicit; only this final version is applied to the file):

```python
        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)
        conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)
        conversao_neutra_idx = _scan(_ANCHOR_CONVERSAO_NEUTRA)

        def _decisive(idx):
            if idx is None:
                return None, None
            m = ordered[idx]
            return (m.tipo_local or m.tipo_cnj or m.descricao), m.data.isoformat()

        total = len(movimentos)
        context = cls._build_context_summary(ordered, nomes)

        arrecadacao_parcial = (
            conversao_idx is None
            and conversao_neutra_idx is not None
            and context["anchor_counts"].get("execucao", 0) > 0
        )

        anchors = {
            "arquivamento": arq_idx,
            "suspenso": suspenso_idx,
            "conversao_renda": conversao_idx,
            "arrecadacao_parcial": arrecadacao_parcial,
        }

        # E0: Conversão em renda — prevalece sobre arquivamento posterior (RE-03.1/RE-06)
        if conversao_idx is not None:
            rule = "E0_conversao_renda"
            nome, data = _decisive(conversao_idx)
            return ClassificationResult(
                "14", "execucao", classe_norm, total,
                rule, nome, data, anchors,
                cls._compute_confidence(anchors, context, rule), context,
            )
```

This replaces the following old block in full (which previously defined `_decisive`, `total`, `context` further down, after the `anchors` dict):

```python
        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)

        anchors = {
            "arquivamento": arq_idx,
            "suspenso": suspenso_idx,
        }

        def _decisive(idx):
            if idx is None:
                return None, None
            m = ordered[idx]
            return (m.tipo_local or m.tipo_cnj or m.descricao), m.data.isoformat()

        total = len(movimentos)
        context = cls._build_context_summary(ordered, nomes)

        # E1: Arquivamento — somente se NÃO há atividade substancial posterior
        if arq_idx is not None:
```

The new block above ends right before `# E1: Arquivamento`, so the method continues unchanged from `# E1: Arquivamento` onward (the `if arq_idx is not None:` line and everything after it, unchanged).

Finally, add a new branch to `_compute_confidence` for the `"conversao"` rule name. Old:

```python
        # Fallback deve ser avaliado ANTES de checks por substring
        # pois o nome da regra pode conter "sentenca" (ex: P6_fallback_antes_sentenca)
        if "fallback" in rule_lower:
            if total > 15:
                return 0.40  # muitos movimentos sem âncora = baixa confiança
            return 0.60

        if "arquivamento" in rule_lower:
```

New:

```python
        # Fallback deve ser avaliado ANTES de checks por substring
        # pois o nome da regra pode conter "sentenca" (ex: P6_fallback_antes_sentenca)
        if "fallback" in rule_lower:
            if total > 15:
                return 0.40  # muitos movimentos sem âncora = baixa confiança
            return 0.60

        if "conversao" in rule_lower:
            # RE-06: a âncora já exige polaridade positiva explícita; corroboração
            # por atividade de execução em curso reforça ainda mais a confiança.
            if counts.get("execucao", 0) > 0:
                return 0.90
            return 0.80

        if "arquivamento" in rule_lower:
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_conversao_renda.py -v`
Expected: PASS (5 testes)

- [ ] **Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier_conversao_renda.py
git commit -m "feat: add conversao em renda anchor with polarity check, precedes arquivamento (RE-06/RE-03.1)"
```

---

## Task 5: RE-03.2 — Suspensão parcial (branch execução)

**Files:**
- Modify: `backend/services/document_phase_classifier.py`
- Test: `backend/tests/test_document_phase_classifier_suspensao_parcial.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para RE-03.2 — Suspensão parcial da execução (fase 12), distinta da
suspensão total (fase 11).
"""
from datetime import datetime

from backend.services.document_phase_classifier import (
    DocumentPhaseClassifier, FusionMovimento,
)


def _mov(tipo_local: str, data_str: str, descricao: str = "") -> FusionMovimento:
    return FusionMovimento(
        data=datetime.strptime(data_str, "%Y-%m-%d"),
        tipo_local=tipo_local, tipo_cnj="", descricao=descricao,
    )


class TestSuspensaoParcial:
    def test_suspensao_parcial_retorna_fase_12(self):
        movs = [
            _mov("Petição", "2023-01-01", descricao="cumprimento de sentenca"),
            _mov("Decisão", "2024-05-01", descricao="suspensao parcial da execucao"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Cumprimento de Sentença")
        assert resultado.phase == "12"
        assert resultado.rule_applied == "E1b_suspensao_parcial"

    def test_suspensao_total_continua_fase_11(self):
        """Regressão: suspensão SEM qualificador 'parcial' continua fase 11."""
        movs = [
            _mov("Petição", "2023-01-01", descricao="cumprimento de sentenca"),
            _mov("Decisão", "2024-05-01", descricao="suspensao da execucao art 921"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Cumprimento de Sentença")
        assert resultado.phase == "11"
        assert resultado.rule_applied == "E2_suspensao"

    def test_suspensao_parcial_nunca_e_15(self):
        """RE-03.2: suspensão (total ou parcial) nunca é arquivamento definitivo."""
        movs = [
            _mov("Petição Inicial", "2018-02-01", descricao="execucao fiscal CDA"),
            _mov("Certidão", "2019-07-10", descricao="mandado negativo citacao"),
            _mov("Decisão", "2020-03-05", descricao="suspensao parcial art 40 lef"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Execução Fiscal")
        assert resultado.phase == "12"
        assert resultado.phase != "15"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_suspensao_parcial.py -v`
Expected: FAIL — os três casos obtêm `phase == "11"` (a âncora `_ANCHOR_SUSPENSO` genérica já captura "suspensao", sem distinguir "parcial").

- [ ] **Step 3: Write minimal implementation**

Add the new anchor regex right after `_ANCHOR_CONVERSAO_NEUTRA` (added in Task 4):

```python
# RE-03.2 — Suspensão parcial da execução (fase 12, distinta da suspensão total)
_ANCHOR_SUSPENSAO_PARCIAL = re.compile(
    r'(suspensao\s+parcial|efeito\s+suspensivo\s+parcial|garantia\s+parcial|'
    r'impugnacao\s+parcial|embargos\s+parcial)'
)
```

Modify `_classify_execucao_traced`. Old (state after Task 4):

```python
        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)
        conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)
        conversao_neutra_idx = _scan(_ANCHOR_CONVERSAO_NEUTRA)
```

New:

```python
        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)
        suspenso_parcial_idx = _scan(_ANCHOR_SUSPENSAO_PARCIAL)
        conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)
        conversao_neutra_idx = _scan(_ANCHOR_CONVERSAO_NEUTRA)
```

Old:

```python
        anchors = {
            "arquivamento": arq_idx,
            "suspenso": suspenso_idx,
            "conversao_renda": conversao_idx,
            "arrecadacao_parcial": arrecadacao_parcial,
        }
```

New:

```python
        anchors = {
            "arquivamento": arq_idx,
            "suspenso": suspenso_idx,
            "suspenso_parcial": suspenso_parcial_idx,
            "conversao_renda": conversao_idx,
            "arrecadacao_parcial": arrecadacao_parcial,
        }
```

Insert the new `E1b` check right after the existing `E1: Arquivamento` block and before `E2: Suspensão total`. Old:

```python
        # E1: Arquivamento — somente se NÃO há atividade substancial posterior
        if arq_idx is not None:
            if not cls._has_substantive_posterior_activity(nomes, arq_idx):
                rule = "E1_arquivamento"
                nome, data = _decisive(arq_idx)
                return ClassificationResult(
                    "15", "execucao", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            anchors["arquivamento_overridden"] = True
            logger.info(
                "Arquivamento (execução) ignorado: atividade substancial posterior "
                f"(total_movimentos={total})"
            )

        # E2: Suspensão de execução — somente se NÃO há atividade substancial posterior
        if suspenso_idx is not None:
```

New:

```python
        # E1: Arquivamento — somente se NÃO há atividade substancial posterior
        if arq_idx is not None:
            if not cls._has_substantive_posterior_activity(nomes, arq_idx):
                rule = "E1_arquivamento"
                nome, data = _decisive(arq_idx)
                return ClassificationResult(
                    "15", "execucao", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            anchors["arquivamento_overridden"] = True
            logger.info(
                "Arquivamento (execução) ignorado: atividade substancial posterior "
                f"(total_movimentos={total})"
            )

        # E1b: Suspensão PARCIAL — RE-03.2, mais específica que a suspensão total,
        # por isso é checada antes de E2.
        if suspenso_parcial_idx is not None:
            if not cls._has_substantive_posterior_activity(nomes, suspenso_parcial_idx):
                rule = "E1b_suspensao_parcial"
                nome, data = _decisive(suspenso_parcial_idx)
                return ClassificationResult(
                    "12", "execucao", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            anchors["suspenso_parcial_overridden"] = True

        # E2: Suspensão de execução — somente se NÃO há atividade substancial posterior
        if suspenso_idx is not None:
```

Add a `_compute_confidence` branch for `"suspensao_parcial"`. Old:

```python
        if "conversao" in rule_lower:
```

New:

```python
        if "suspensao_parcial" in rule_lower:
            return 0.80

        if "conversao" in rule_lower:
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_suspensao_parcial.py -v`
Expected: PASS (3 testes)

- [ ] **Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier_suspensao_parcial.py
git commit -m "feat: distinguish partial suspension (12) from total suspension (11) (RE-03.2)"
```

---

## Task 6: RE-05 — Trânsito inferido com teto de confiança (branch conhecimento)

**Files:**
- Modify: `backend/services/document_phase_classifier.py`
- Test: `backend/tests/test_document_phase_classifier_transito_inferido.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para RE-05 — Trânsito em julgado inferido (sem certidão explícita) tem
teto de confiança de 0.70.
"""
from datetime import datetime

from backend.services.document_phase_classifier import (
    DocumentPhaseClassifier, FusionMovimento,
)


def _mov(tipo_local: str, data_str: str, descricao: str = "") -> FusionMovimento:
    return FusionMovimento(
        data=datetime.strptime(data_str, "%Y-%m-%d"),
        tipo_local=tipo_local, tipo_cnj="", descricao=descricao,
    )


class TestTransitoInferido:
    def test_decurso_de_prazo_infere_transito_com_confianca_capada(self):
        movs = [
            _mov("Petição Inicial", "2024-01-01"),
            _mov("Sentença", "2024-03-01"),
            _mov("Certidão", "2024-08-01", descricao="decurso de prazo recursal"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Cível")
        assert resultado.rule_applied == "P2b_transito_inferido"
        assert resultado.confidence == 0.70
        assert resultado.anchor_matches.get("transito_inferido") is True

    def test_certidao_explicita_tem_prioridade_sobre_inferencia(self):
        """Regressão: quando há certidão EXPLÍCITA de trânsito, ela decide (P2), não a inferência."""
        movs = [
            _mov("Sentença", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2024-03-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Cível")
        assert resultado.rule_applied == "P2_transito_em_julgado"

    def test_sem_sinal_de_transito_nao_infere(self):
        """Regressão: sem nenhum sinal de trânsito (explícito ou inferido) → não infere nada."""
        movs = [
            _mov("Petição Inicial", "2024-01-01"),
            _mov("Sentença", "2024-03-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Cível")
        assert resultado.rule_applied == "P3_sentenca_sem_transito"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_transito_inferido.py -v`
Expected: FAIL — o primeiro caso obtém `rule_applied == "P3_sentenca_sem_transito"` (sem inferência de trânsito ainda implementada).

- [ ] **Step 3: Write minimal implementation**

Add the new anchor regex right after `_ANCHOR_SUSPENSAO_PARCIAL` (added in Task 5):

```python
# RE-05 — Trânsito inferido (sem certidão explícita); teto de confiança 0.70
_ANCHOR_TRANSITO_INFERIDO = re.compile(
    r'(decurso\s+de\s+prazo|desistencia\s+de\s+recurso|homologacao\s+de\s+desistencia)'
)
```

Modify `_classify_conhecimento_traced`. Old (state after Task 4):

```python
        acordao_idx = _scan(_ANCHOR_ACORDAO)
        conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)
```

New:

```python
        acordao_idx = _scan(_ANCHOR_ACORDAO)
        conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)
        transito_inferido_idx = _scan(_ANCHOR_TRANSITO_INFERIDO) if transito_idx is None else None
```

Add `"transito_inferido"` marker to `anchors`. Old:

```python
        anchors = {
            "arquivamento": arq_idx,
            "transito": transito_idx,
            "sentenca": sentenca_idx,
            "remessa": remessa_idx,
            "acordao": acordao_idx,
            "suspenso": suspenso_idx,
            "execucao": execucao_idx,
            "conversao_renda": conversao_idx,
        }
```

New:

```python
        anchors = {
            "arquivamento": arq_idx,
            "transito": transito_idx,
            "sentenca": sentenca_idx,
            "remessa": remessa_idx,
            "acordao": acordao_idx,
            "suspenso": suspenso_idx,
            "execucao": execucao_idx,
            "conversao_renda": conversao_idx,
            "transito_inferido": transito_inferido_idx is not None,
        }
```

Insert the `P2b` check right after the existing `P2: Trânsito em Julgado (explícito)` block. Old:

```python
        # P2: Trânsito em Julgado (explícito)
        if transito_idx is not None:
            rule = "P2_transito_em_julgado"
            nome, data = _decisive(transito_idx)
            return ClassificationResult(
                "03", "conhecimento", classe_norm, total,
                rule, nome, data, anchors,
                cls._compute_confidence(anchors, context, rule), context,
            )

        # P3: Sentença
        if sentenca_idx is not None:
```

New:

```python
        # P2: Trânsito em Julgado (explícito)
        if transito_idx is not None:
            rule = "P2_transito_em_julgado"
            nome, data = _decisive(transito_idx)
            return ClassificationResult(
                "03", "conhecimento", classe_norm, total,
                rule, nome, data, anchors,
                cls._compute_confidence(anchors, context, rule), context,
            )

        # P2b: Trânsito INFERIDO (RE-05) — teto de confiança 0.70, nunca mais que isso.
        if transito_inferido_idx is not None:
            rule = "P2b_transito_inferido"
            nome, data = _decisive(transito_inferido_idx)
            return ClassificationResult(
                "03", "conhecimento", classe_norm, total,
                rule, nome, data, anchors,
                0.70, context,
            )

        # P3: Sentença
        if sentenca_idx is not None:
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_transito_inferido.py -v`
Expected: PASS (3 testes)

- [ ] **Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier_transito_inferido.py
git commit -m "feat: infer transito em julgado from decurso de prazo, capped at 0.70 confidence (RE-05)"
```

---

## Task 7: RE-11 — Conflito classe executiva × peças cognitivas (branch execução)

**Files:**
- Modify: `backend/services/document_phase_classifier.py`
- Test: `backend/tests/test_document_phase_classifier_conflito_classe.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para RE-11 (item 3) — Conflito entre classe executiva e peças
puramente cognitivas: não força fase executiva sem sinal de apoio.
"""
from datetime import datetime

from backend.services.document_phase_classifier import (
    DocumentPhaseClassifier, FusionMovimento,
)


def _mov(tipo_local: str, data_str: str, descricao: str = "") -> FusionMovimento:
    return FusionMovimento(
        data=datetime.strptime(data_str, "%Y-%m-%d"),
        tipo_local=tipo_local, tipo_cnj="", descricao=descricao,
    )


class TestConflitoClasseExecutivaComPecasCognitivas:
    def test_classe_executiva_com_apenas_pecas_cognitivas_nao_confia_em_10(self):
        movs = [
            _mov("Petição Inicial", "2020-01-01"),
            _mov("Contestação", "2020-06-01"),
            _mov("Réplica", "2020-09-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Execução Fiscal")
        assert resultado.rule_applied == "E2b_conflito_classe_pecas"
        assert resultado.confidence == 0.50

    def test_classe_executiva_com_sinal_de_execucao_nao_aciona_conflito(self):
        """Regressão: havendo QUALQUER sinal de execução, o conflito não se aplica."""
        movs = [
            _mov("Petição Inicial", "2020-01-01"),
            _mov("Penhora", "2020-06-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Execução Fiscal")
        assert resultado.rule_applied == "E3_fallback"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_conflito_classe.py -v`
Expected: FAIL — o primeiro caso obtém `rule_applied == "E3_fallback"` (sem distinguir peças puramente cognitivas).

- [ ] **Step 3: Write minimal implementation**

Add the new anchor regex right after `_ANCHOR_TRANSITO_INFERIDO` (added in Task 6):

```python
# RE-11 (item 3) — Peças puramente cognitivas dentro de árvore de classe executiva
_ANCHOR_COGNITIVO_PURO = re.compile(
    r'(contestacao|replica|audiencia\s+de\s+instrucao)'
)
```

Modify `_classify_execucao_traced`. Add the scan right after `suspenso_parcial_idx = _scan(_ANCHOR_SUSPENSAO_PARCIAL)` (added in Task 5). Old:

```python
        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)
        suspenso_parcial_idx = _scan(_ANCHOR_SUSPENSAO_PARCIAL)
        conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)
        conversao_neutra_idx = _scan(_ANCHOR_CONVERSAO_NEUTRA)
```

New:

```python
        arq_idx = _scan(_ANCHOR_ARQUIVAMENTO)
        suspenso_idx = _scan(_ANCHOR_SUSPENSO)
        suspenso_parcial_idx = _scan(_ANCHOR_SUSPENSAO_PARCIAL)
        conversao_idx = _scan(_ANCHOR_CONVERSAO_POSITIVA)
        conversao_neutra_idx = _scan(_ANCHOR_CONVERSAO_NEUTRA)
        cognitivo_idx = _scan(_ANCHOR_COGNITIVO_PURO)
```

Insert the `E2b` check right after the existing `E2: Suspensão de execução` block and before `# Fallback: execução em andamento`. Old:

```python
        # E2: Suspensão de execução — somente se NÃO há atividade substancial posterior
        if suspenso_idx is not None:
            if not cls._has_substantive_posterior_activity(nomes, suspenso_idx):
                rule = "E2_suspensao"
                nome, data = _decisive(suspenso_idx)
                return ClassificationResult(
                    "11", "execucao", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            anchors["suspenso_overridden"] = True

        # Fallback: execução em andamento
        rule = "E3_fallback"
```

New:

```python
        # E2: Suspensão de execução — somente se NÃO há atividade substancial posterior
        if suspenso_idx is not None:
            if not cls._has_substantive_posterior_activity(nomes, suspenso_idx):
                rule = "E2_suspensao"
                nome, data = _decisive(suspenso_idx)
                return ClassificationResult(
                    "11", "execucao", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            anchors["suspenso_overridden"] = True

        # E2b: Conflito classe executiva × peças puramente cognitivas (RE-11, item 3).
        # Só se aplica quando NÃO há nenhum sinal de execução na árvore inteira —
        # qualquer sinal de execução (mesmo fraco) já basta para seguir o fallback normal.
        if cognitivo_idx is not None and context["anchor_counts"].get("execucao", 0) == 0:
            rule = "E2b_conflito_classe_pecas"
            nome, data = _decisive(cognitivo_idx)
            return ClassificationResult(
                "10", "execucao", classe_norm, total,
                rule, nome, data, anchors,
                0.50, context,
            )

        # Fallback: execução em andamento
        rule = "E3_fallback"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_conflito_classe.py -v`
Expected: PASS (2 testes)

- [ ] **Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier_conflito_classe.py
git commit -m "feat: flag execucao branch conflict when only cognitive-typical documents exist (RE-11)"
```

---

## Task 8: RE-07 — Threshold de abstenção (código "16")

**Files:**
- Modify: `backend/services/document_phase_classifier.py`
- Test: `backend/tests/test_document_phase_classifier_abstencao.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para RE-07 — Abstenção calibrada (fase "16"): threshold 0.75 aplicado
apenas às regras explicitamente elegíveis, preservando o comportamento de
todas as regras pré-existentes (arquivamento, trânsito explícito, sentença,
remessa, suspensão total, suspensão parcial, conversão em renda).
"""
from datetime import datetime

from backend.services.document_phase_classifier import (
    DocumentPhaseClassifier, FusionMovimento,
)


def _mov(tipo_local: str, data_str: str, descricao: str = "") -> FusionMovimento:
    return FusionMovimento(
        data=datetime.strptime(data_str, "%Y-%m-%d"),
        tipo_local=tipo_local, tipo_cnj="", descricao=descricao,
    )


class TestAbstencaoFallbackConhecimento:
    def test_arvore_opaca_sem_ancoras_abstem(self):
        """Caso real anonimizado (T-02 de testes-minimos.json): árvore de trabalho
        sem peças decisórias nominadas → abstenção."""
        movs = [
            _mov("Petição Inicial", "2015-04-10"),
            _mov("Aviso de Recebimento", "2016-02-02"),
            _mov("Andamento Processual", "2019-09-03"),
            _mov("Andamento Processual", "2021-06-14"),
            _mov("Publicação", "2026-01-20"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "")
        assert resultado.phase == "16"
        assert resultado.fase_provavel == "01"
        assert resultado.motivo_abstencao == "opacidade"


class TestAbstencaoFallbackExecucao:
    def test_fallback_execucao_com_muitos_movimentos_sem_ancora_abstem(self):
        movs = [_mov(f"Andamento {i}", f"2020-{(i % 12) + 1:02d}-01") for i in range(20)]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Execução Fiscal")
        assert resultado.phase == "16"
        assert resultado.fase_provavel == "10"
        assert resultado.motivo_abstencao == "opacidade"


class TestAbstencaoP0ExecucaoPosteriorTransito:
    def test_execucao_posterior_a_transito_abstem_por_transito_nao_certificado(self):
        """P0_execucao_posterior_transito tem confiança fixa 0.70 (< 0.75) → abstém."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
            _mov("Execução / Cumprimento de Sentença", "2026-03-10"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")
        assert resultado.phase == "16"
        assert resultado.fase_provavel == "10"
        assert resultado.motivo_abstencao == "transito_nao_certificado"


class TestAbstencaoNaoAfetaRegrasExistentes:
    """Guarda de regressão: regras com confiança < 0.75 mas NÃO elegíveis à
    abstenção (por não estarem no dicionário de motivos) continuam retornando
    a fase substantiva normalmente."""

    def test_arquivamento_isolado_sem_corroboracao_nao_abstem(self):
        """P1_arquivamento sem trânsito/sentença corroborantes tem confiança 0.70,
        mas P1_arquivamento não é uma regra elegível à abstenção."""
        movs = [
            _mov("Trânsito em Julgado", "2024-01-01"),
            _mov("Arquivamento", "2024-02-02"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Cível")
        assert resultado.phase == "15"
        assert resultado.confidence == 0.85

    def test_conflito_classe_pecas_abstem_por_contradicao_documental(self):
        movs = [
            _mov("Petição Inicial", "2020-01-01"),
            _mov("Contestação", "2020-06-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Execução Fiscal")
        assert resultado.phase == "16"
        assert resultado.fase_provavel == "10"
        assert resultado.motivo_abstencao == "contradicao_documental"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_abstencao.py -v`
Expected: FAIL — todos os casos que esperam `phase == "16"` obtêm a fase substantiva original (`"01"`, `"10"`), pois a etapa de abstenção ainda não existe.

- [ ] **Step 3: Write minimal implementation**

Add module-level constants right after `_is_classe_execucao` (before the RE-04 `_AUTOR_SIGNAIS` block):

```python
# ---------------------------------------------------------------------------
# RE-07 — Abstenção calibrada (fase "16")
# ---------------------------------------------------------------------------

_ABSTENTION_THRESHOLD = 0.75

# Regras elegíveis à abstenção e o motivo correspondente. Regras que NÃO
# aparecem aqui nunca abstêm, mesmo que sua confiança fique abaixo do
# threshold — isso preserva o comportamento de todas as regras pré-existentes
# (P1-P5, E1-E2), evitando recalibrar retroativamente a suíte de regressão
# (spec §5.1, decisão de planejamento #1).
_MOTIVO_ABSTENCAO_BY_RULE = {
    "P6_fallback_antes_sentenca": "opacidade",
    "P6_fallback_antes_sentenca_ALERT": "opacidade",
    "E3_fallback": "opacidade",
    "P0_execucao_posterior_transito": "transito_nao_certificado",
    "P2b_transito_inferido": "transito_nao_certificado",
    "E2b_conflito_classe_pecas": "contradicao_documental",
}
```

Add the new classmethod `_aplicar_abstencao` right before `_computar_hierarquia`:

```python
    @classmethod
    def _aplicar_abstencao(cls, result: ClassificationResult) -> None:
        """
        RE-07: converte um resultado preliminar de baixa confiança em fase
        "16", preenchendo fase_provavel/motivo_abstencao. Só atua sobre
        regras explicitamente listadas em _MOTIVO_ABSTENCAO_BY_RULE.
        """
        motivo = _MOTIVO_ABSTENCAO_BY_RULE.get(result.rule_applied)
        if motivo is None:
            return
        if result.confidence is None or result.confidence >= _ABSTENTION_THRESHOLD:
            return
        result.fase_provavel = result.phase
        result.motivo_abstencao = motivo
        result.phase = "16"
```

Wire it into `classify_with_trace`. Old:

```python
        classe_norm = cls._normalize(classe_processual)

        if _is_classe_execucao(classe_norm):
            result = cls._classify_execucao_traced(movimentos, classe_norm)
        else:
            result = cls._classify_conhecimento_traced(movimentos, classe_norm)

        cls._computar_hierarquia(result, classe_norm)
        return result
```

New:

```python
        classe_norm = cls._normalize(classe_processual)

        if _is_classe_execucao(classe_norm):
            result = cls._classify_execucao_traced(movimentos, classe_norm)
        else:
            result = cls._classify_conhecimento_traced(movimentos, classe_norm)

        cls._aplicar_abstencao(result)
        cls._computar_hierarquia(result, classe_norm)
        return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_abstencao.py -v`
Expected: PASS (5 testes)

- [ ] **Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier_abstencao.py
git commit -m "feat: abstain to phase 16 for explicitly eligible low-confidence rules (RE-07)"
```

---

## Task 9: Consolidação tri-fonte — tratamento uniforme de "16"/"Indefinido"

**Files:**
- Modify: `backend/services/process_service.py:35-146`
- Test: `backend/tests/test_consolidar_tres_fontes.py` (novo — não existia cobertura dedicada)
- Test: `backend/tests/test_hierarchical_classification.py` (novo caso em `TestExtrairHierarquiaDaFonte`)

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para _consolidar_tres_fontes — não existia arquivo de teste dedicado
antes desta adaptação (verificado por busca na suíte inteira).
"""
from backend.services.process_service import _consolidar_tres_fontes


class TestConsolidacaoComAbstencao:
    def test_pav_tree_abstem_nao_sobrescreve_fusion_valido(self):
        """'16' na Árvore PAV deve ser tratado como 'pular', igual a 'Indefinido'."""
        fase, modo = _consolidar_tres_fontes("Indefinido", "02", "16")
        assert fase == "02"
        assert modo == "fusion_preferred"

    def test_fusion_abstem_nao_sobrescreve_datajud_valido(self):
        fase, modo = _consolidar_tres_fontes("05 Recurso", "16", "Indefinido")
        assert fase == "05 Recurso"
        assert modo == "datajud_fallback"

    def test_todas_fontes_validas_abstem_consolidado_e_16(self):
        fase, modo = _consolidar_tres_fontes("Indefinido", "16", "16")
        assert fase == "16"
        assert modo == "todas_abstencao"

    def test_execucao_valida_ainda_sobrescreve_conhecimento_mesmo_com_abstencao_presente(self):
        """Regra 1 (execução > conhecimento) continua funcionando com uma 3ª fonte abstendo."""
        fase, modo = _consolidar_tres_fontes("02 Conhecimento", "16", "10")
        assert fase == "10"
        assert modo == "pav_tree_execucao_override"


class TestConsolidacaoRegressao:
    """Guarda de regressão: comportamento pré-existente sem nenhuma fonte "16"."""

    def test_pav_tree_fusion_concordam(self):
        fase, modo = _consolidar_tres_fontes("Indefinido", "05", "05")
        assert fase == "05"
        assert modo == "pav_tree_fusion_concordam"

    def test_todas_indefinidas(self):
        fase, modo = _consolidar_tres_fontes("Indefinido", "Indefinido", "Indefinido")
        assert fase == "Indefinido"
        assert modo == "todas_indefinidas"

    def test_pav_tree_preferred(self):
        fase, modo = _consolidar_tres_fontes("Indefinido", "Indefinido", "07")
        assert fase == "07"
        assert modo == "pav_tree_preferred"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_consolidar_tres_fontes.py -v`
Expected: FAIL — `test_pav_tree_abstem_nao_sobrescreve_fusion_valido` obtém `modo == "pav_tree_preferred"` (hoje `"16"` não é reconhecido como "pular"); `test_todas_fontes_validas_abstem_consolidado_e_16` obtém `fase == "Indefinido"` em vez de `"16"`.

- [ ] **Step 3: Write minimal implementation**

Replace `_consolidar_tres_fontes` in `backend/services/process_service.py`. Old:

```python
def _consolidar_tres_fontes(
    fase_datajud: str, fase_fusion: str, fase_pav_tree: str
) -> tuple[str, str]:
    """
    Consolida fases de DataJud, Fusion e Árvore PAV usando as seguintes regras:

    1. Execução sobrescreve Conhecimento (qualquer fonte com 10-14 anula 01-09)
    2. PAV Tree + Fusion concordam → usa PAV Tree (alta confiança)
    3. PAV Tree com valor válido (não "Indefinido") → PAV Tree tem precedência
    4. Fallback Fusion → fallback DataJud

    IMPORTANTE: "Indefinido" não é um código válido e não deve ser usado como prioridade.
    """
    cod_dj  = _extrair_codigo_fase(fase_datajud)
    cod_fu  = _extrair_codigo_fase(fase_fusion)
    cod_pav = _extrair_codigo_fase(fase_pav_tree) if fase_pav_tree != "Indefinido" else ""

    logger.debug(
        f"_consolidar_tres_fontes: DataJud={fase_datajud} (cod={cod_dj}), "
        f"Fusion={fase_fusion} (cod={cod_fu}), PAVTree={fase_pav_tree} (cod={cod_pav})"
    )

    all_valid = [c for c in [cod_dj, cod_fu, cod_pav] if c]
    has_exec = any(c in _FASES_EXECUCAO for c in all_valid)
    has_conh = any(c in _FASES_CONHECIMENTO for c in all_valid)

    # Regra 1: Execução > Conhecimento
    if has_exec and has_conh:
        if cod_pav in _FASES_EXECUCAO:
            logger.debug(f"-> PAV Tree execução override: {fase_pav_tree}")
            return fase_pav_tree, "pav_tree_execucao_override"
        if cod_fu in _FASES_EXECUCAO:
            logger.debug(f"-> Fusion execução override: {fase_fusion}")
            return fase_fusion, "fusion_execucao_override"
        if cod_dj in _FASES_EXECUCAO:
            logger.debug(f"-> DataJud execução override: {fase_datajud}")
            return fase_datajud, "datajud_execucao_override"

    # Regra 2: PAV Tree + Fusion concordam (ambos com códigos válidos)
    if cod_pav and cod_fu and cod_pav == cod_fu:
        logger.debug(f"-> PAV Tree + Fusion concordam: {fase_pav_tree}")
        return fase_pav_tree, "pav_tree_fusion_concordam"

    # Regra 3: PAV Tree com valor válido (não "Indefinido")
    if cod_pav and fase_pav_tree != "Indefinido":
        logger.debug(f"-> PAV Tree preferred: {fase_pav_tree}")
        return fase_pav_tree, "pav_tree_preferred"

    # Regra 4: Fallbacks
    if cod_fu:
        logger.debug(f"-> Fusion preferred: {fase_fusion}")
        return fase_fusion, "fusion_preferred"
    if cod_dj:
        logger.debug(f"-> DataJud fallback: {fase_datajud}")
        return fase_datajud, "datajud_fallback"

    logger.debug("-> Todas indefinidas")
    return "Indefinido", "todas_indefinidas"
```

New:

```python
def _codigo_valido_para_cascata(fase_str: str) -> str:
    """
    Extrai o código de fase para fins de PRIORIDADE na cascata de
    consolidação, tratando "Indefinido" (ausência de dado) e "16" (abstenção
    — RE-07) uniformemente como "pular" nas Regras 1-3, para as 3 fontes
    (DataJud, Fusion, Árvore PAV). Antes desta correção, apenas a Árvore PAV
    tinha essa proteção, e só para "Indefinido" (spec §5.2).
    """
    cod = _extrair_codigo_fase(fase_str)
    if fase_str == "Indefinido" or cod == "16":
        return ""
    return cod


def _consolidar_tres_fontes(
    fase_datajud: str, fase_fusion: str, fase_pav_tree: str
) -> tuple[str, str]:
    """
    Consolida fases de DataJud, Fusion e Árvore PAV usando as seguintes regras:

    1. Execução sobrescreve Conhecimento (qualquer fonte com 10-14 anula 01-09)
    2. PAV Tree + Fusion concordam → usa PAV Tree (alta confiança)
    3. PAV Tree com valor válido (não "Indefinido", não "16") → PAV Tree tem precedência
    4. Fallback Fusion → fallback DataJud
    5. Se todas as fontes com dado válido abstiveram ("16") → consolidado é "16"

    IMPORTANTE: "Indefinido" (ausência de dado) e "16" (abstenção — indeterminação
    jurídica, RE-07) são conceitos distintos (spec §5.3) e nenhum dos dois deve
    ser usado como prioridade na cascata das Regras 1-4.
    """
    cod_dj  = _codigo_valido_para_cascata(fase_datajud)
    cod_fu  = _codigo_valido_para_cascata(fase_fusion)
    cod_pav = _codigo_valido_para_cascata(fase_pav_tree)

    # Rastreamento de abstenção (Regra 5): fontes que retornaram dado legível
    # ("Indefinido" é ausência de dado, não conta aqui) e o subconjunto delas
    # que abstiveram ("16").
    fontes_com_dado = [f for f in (fase_datajud, fase_fusion, fase_pav_tree) if f and f != "Indefinido"]
    fontes_abstencao = [f for f in fontes_com_dado if _extrair_codigo_fase(f) == "16"]

    logger.debug(
        f"_consolidar_tres_fontes: DataJud={fase_datajud} (cod={cod_dj}), "
        f"Fusion={fase_fusion} (cod={cod_fu}), PAVTree={fase_pav_tree} (cod={cod_pav})"
    )

    all_valid = [c for c in [cod_dj, cod_fu, cod_pav] if c]
    has_exec = any(c in _FASES_EXECUCAO for c in all_valid)
    has_conh = any(c in _FASES_CONHECIMENTO for c in all_valid)

    # Regra 1: Execução > Conhecimento
    if has_exec and has_conh:
        if cod_pav in _FASES_EXECUCAO:
            logger.debug(f"-> PAV Tree execução override: {fase_pav_tree}")
            return fase_pav_tree, "pav_tree_execucao_override"
        if cod_fu in _FASES_EXECUCAO:
            logger.debug(f"-> Fusion execução override: {fase_fusion}")
            return fase_fusion, "fusion_execucao_override"
        if cod_dj in _FASES_EXECUCAO:
            logger.debug(f"-> DataJud execução override: {fase_datajud}")
            return fase_datajud, "datajud_execucao_override"

    # Regra 2: PAV Tree + Fusion concordam (ambos com códigos válidos)
    if cod_pav and cod_fu and cod_pav == cod_fu:
        logger.debug(f"-> PAV Tree + Fusion concordam: {fase_pav_tree}")
        return fase_pav_tree, "pav_tree_fusion_concordam"

    # Regra 3: PAV Tree com valor válido (não "Indefinido", não "16")
    if cod_pav:
        logger.debug(f"-> PAV Tree preferred: {fase_pav_tree}")
        return fase_pav_tree, "pav_tree_preferred"

    # Regra 4: Fallbacks
    if cod_fu:
        logger.debug(f"-> Fusion preferred: {fase_fusion}")
        return fase_fusion, "fusion_preferred"
    if cod_dj:
        logger.debug(f"-> DataJud fallback: {fase_datajud}")
        return fase_datajud, "datajud_fallback"

    # Regra 5 (RE-07/spec §5.2): todas as fontes com dado válido abstiveram
    if fontes_abstencao and len(fontes_abstencao) == len(fontes_com_dado):
        logger.debug("-> Todas as fontes válidas abstiveram (16)")
        return "16", "todas_abstencao"

    logger.debug("-> Todas indefinidas")
    return "Indefinido", "todas_indefinidas"
```

Now update `_extrair_hierarquia_da_fonte` to handle the new `"todas_abstencao"` mode. Old:

```python
def _extrair_hierarquia_da_fonte(modo: str, meta: dict) -> tuple:
    """
    Extrai (stage, substage, transit_julgado) da fonte vencedora da consolidação.

    O parâmetro 'modo' é o segundo valor retornado por _consolidar_tres_fontes(),
    e indica qual fonte "venceu" (pav_tree_*, fusion_*, datajud_*).
    """
    if modo.startswith("pav_tree"):
        prefix = "pav_tree"
    elif modo.startswith("fusion"):
        prefix = "fusion"
    elif modo.startswith("datajud"):
        prefix = "datajud"
    else:
        return (None, None, None)

    return (
        meta.get(f"{prefix}_stage"),
        meta.get(f"{prefix}_substage"),
        meta.get(f"{prefix}_transit"),
    )
```

New:

```python
def _extrair_hierarquia_da_fonte(modo: str, meta: dict) -> tuple:
    """
    Extrai (stage, substage, transit_julgado) da fonte vencedora da consolidação.

    O parâmetro 'modo' é o segundo valor retornado por _consolidar_tres_fontes(),
    e indica qual fonte "venceu" (pav_tree_*, fusion_*, datajud_*), ou o modo
    especial "todas_abstencao" (RE-07) quando todas as fontes válidas abstiveram.
    """
    if modo == "todas_abstencao":
        # Qualquer fonte que absteve já computou stage=Stage.CONTROLE (6) para
        # "16" (ver Task 10); usa a de maior prioridade que estiver disponível.
        prefix = "pav_tree" if meta.get("pav_tree_stage") is not None else "fusion"
    elif modo.startswith("pav_tree"):
        prefix = "pav_tree"
    elif modo.startswith("fusion"):
        prefix = "fusion"
    elif modo.startswith("datajud"):
        prefix = "datajud"
    else:
        return (None, None, None)

    return (
        meta.get(f"{prefix}_stage"),
        meta.get(f"{prefix}_substage"),
        meta.get(f"{prefix}_transit"),
    )
```

Add a new parametrized case to `TestExtrairHierarquiaDaFonte` in `backend/tests/test_hierarchical_classification.py`. Old:

```python
    @pytest.mark.parametrize("modo,expected", [
        ("pav_tree_preferred", (1, "1.4", "nao")),
        ("pav_tree_execucao_override", (1, "1.4", "nao")),
        ("pav_tree_fusion_concordam", (1, "1.4", "nao")),
        ("fusion_preferred", (2, "2.1", "sim")),
        ("fusion_execucao_override", (2, "2.1", "sim")),
        ("datajud_fallback", (1, "1.1", "nao")),
        ("datajud_execucao_override", (1, "1.1", "nao")),
        ("todas_indefinidas", (None, None, None)),
        ("ambos_indefinidos", (None, None, None)),
        ("manual_override", (None, None, None)),
    ])
    def test_fonte_selection(self, modo, expected):
        assert _extrair_hierarquia_da_fonte(modo, self._META) == expected
```

New:

```python
    @pytest.mark.parametrize("modo,expected", [
        ("pav_tree_preferred", (1, "1.4", "nao")),
        ("pav_tree_execucao_override", (1, "1.4", "nao")),
        ("pav_tree_fusion_concordam", (1, "1.4", "nao")),
        ("fusion_preferred", (2, "2.1", "sim")),
        ("fusion_execucao_override", (2, "2.1", "sim")),
        ("datajud_fallback", (1, "1.1", "nao")),
        ("datajud_execucao_override", (1, "1.1", "nao")),
        ("todas_indefinidas", (None, None, None)),
        ("ambos_indefinidos", (None, None, None)),
        ("manual_override", (None, None, None)),
        ("todas_abstencao", (1, "1.4", "nao")),  # usa pav_tree por estar presente em _META
    ])
    def test_fonte_selection(self, modo, expected):
        assert _extrair_hierarquia_da_fonte(modo, self._META) == expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_consolidar_tres_fontes.py tests/test_hierarchical_classification.py -v`
Expected: PASS (7 novos testes em `test_consolidar_tres_fontes.py` + a suíte inteira de `test_hierarchical_classification.py`, incluindo o novo caso parametrizado)

- [ ] **Step 5: Commit**

```bash
git add backend/services/process_service.py backend/tests/test_consolidar_tres_fontes.py backend/tests/test_hierarchical_classification.py
git commit -m "fix: treat 16 (abstention) uniformly across the 3 sources in phase consolidation"
```

---

## Task 10: Mapeamento hierárquico — Stage.CONTROLE para "16"

**Files:**
- Modify: `backend/services/hierarchical_classification.py`
- Modify: `backend/tests/test_hierarchical_classification.py`

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/test_hierarchical_classification.py`, right after `TestPhaseToStageSubstage`:

```python
# ============================================================
# Stage.CONTROLE — home hierárquico do código "16" (abstenção)
# ============================================================

class TestStageControle:
    """Testa o novo Stage.CONTROLE (6), home hierárquico da fase '16' (RE-07)."""

    def test_stage_controle_e_6(self):
        assert Stage.CONTROLE == 6

    def test_stage_controle_tem_label(self):
        assert Stage.LABELS[6] == "Controle / Revisão Humana"

    def test_phase_to_stage_substage_16(self):
        stage, substage = PHASE_TO_STAGE_SUBSTAGE["16"]
        assert stage == Stage.CONTROLE
        assert substage is None

    @pytest.mark.parametrize("transit", ["sim", "nao", "na"])
    def test_derive_legacy_phase_stage_controle(self, transit):
        assert derive_legacy_phase(Stage.CONTROLE, None, transit) == "16"
```

Also update `test_all_legacy_map_entries_covered` in the same file. Old:

```python
    def test_all_legacy_map_entries_covered(self):
        """Todos os 15 códigos são alcançáveis pelo _LEGACY_MAP."""
        all_codes = set(_LEGACY_MAP.values())
        expected_codes = {f"{i:02d}" for i in range(1, 16)}
        assert expected_codes == all_codes
```

New:

```python
    def test_all_legacy_map_entries_covered(self):
        """
        Todos os 16 códigos (15 oficiais + '16' de controle/abstenção) são
        alcançáveis pelo _LEGACY_MAP.

        Justificativa da mudança (adaptação doctree, RE-07): a partir desta
        adaptação, o classificador pode devolver o código '16' (Indeterminado
        — Revisão Humana) quando a confiança cai abaixo do threshold de
        abstenção. '16' ganhou home hierárquico próprio (Stage.CONTROLE=6,
        substage=None), análogo ao tratamento já dado a 13/15. Este teste
        passa a exigir 16 códigos, não mais 15 — mudança intencional, não
        uma regressão.
        """
        all_codes = set(_LEGACY_MAP.values())
        expected_codes = {f"{i:02d}" for i in range(1, 16)} | {"16"}
        assert expected_codes == all_codes
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_hierarchical_classification.py -v -k "TestStageControle or test_all_legacy_map_entries_covered"`
Expected: FAIL — `TestStageControle` obtém `AttributeError: type object 'Stage' has no attribute 'CONTROLE'`; `test_all_legacy_map_entries_covered` obtém `AssertionError` (o conjunto atual não contém `"16"`, o esperado agora exige).

- [ ] **Step 3: Write minimal implementation**

Edit `backend/services/hierarchical_classification.py`. Old:

```python
class Stage:
    CONHECIMENTO = 1
    EXECUCAO = 2
    SUSPENSAO = 3
    ARQUIVAMENTO = 4
    CONVERSAO = 5

    LABELS = {
        1: "Conhecimento",
        2: "Execução",
        3: "Suspensão / Sobrestamento",
        4: "Arquivamento",
        5: "Conversão em Renda",
    }
```

New:

```python
class Stage:
    CONHECIMENTO = 1
    EXECUCAO = 2
    SUSPENSAO = 3
    ARQUIVAMENTO = 4
    CONVERSAO = 5
    CONTROLE = 6  # RE-07 — abstenção / revisão humana (fase "16")

    LABELS = {
        1: "Conhecimento",
        2: "Execução",
        3: "Suspensão / Sobrestamento",
        4: "Arquivamento",
        5: "Conversão em Renda",
        6: "Controle / Revisão Humana",
    }
```

Old:

```python
    # Conversão
    (5, None, "sim"):  "14",
    (5, None, "nao"):  "14",
    (5, None, "na"):   "14",
}
```

New:

```python
    # Conversão
    (5, None, "sim"):  "14",
    (5, None, "nao"):  "14",
    (5, None, "na"):   "14",
    # Controle (abstenção — RE-07)
    (6, None, "sim"):  "16",
    (6, None, "nao"):  "16",
    (6, None, "na"):   "16",
}
```

Old:

```python
PHASE_TO_STAGE_SUBSTAGE = {
    "01": (Stage.CONHECIMENTO, Substage.ANTES_SENTENCA),
    "02": (Stage.CONHECIMENTO, Substage.SENTENCA_PROFERIDA),
    "03": (Stage.CONHECIMENTO, Substage.SENTENCA_PROFERIDA),       # transit=sim
    "04": (Stage.CONHECIMENTO, Substage.PENDENTE_TRIBUNAL_LOCAL),
    "05": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_LOCAL),
    "06": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_LOCAL), # transit=sim
    "07": (Stage.CONHECIMENTO, Substage.PENDENTE_TRIBUNAL_SUPERIOR),
    "08": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_SUPERIOR),
    "09": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_SUPERIOR), # transit=sim
    "10": (Stage.EXECUCAO, Substage.EXECUCAO_NORMAL),
    "11": (Stage.EXECUCAO, Substage.EXECUCAO_SUSPENSA_TOTAL),
    "12": (Stage.EXECUCAO, Substage.EXECUCAO_SUSPENSA_PARCIAL),
    "13": (Stage.SUSPENSAO, None),
    "14": (Stage.CONVERSAO, None),
    "15": (Stage.ARQUIVAMENTO, None),
}
```

New:

```python
PHASE_TO_STAGE_SUBSTAGE = {
    "01": (Stage.CONHECIMENTO, Substage.ANTES_SENTENCA),
    "02": (Stage.CONHECIMENTO, Substage.SENTENCA_PROFERIDA),
    "03": (Stage.CONHECIMENTO, Substage.SENTENCA_PROFERIDA),       # transit=sim
    "04": (Stage.CONHECIMENTO, Substage.PENDENTE_TRIBUNAL_LOCAL),
    "05": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_LOCAL),
    "06": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_LOCAL), # transit=sim
    "07": (Stage.CONHECIMENTO, Substage.PENDENTE_TRIBUNAL_SUPERIOR),
    "08": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_SUPERIOR),
    "09": (Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_SUPERIOR), # transit=sim
    "10": (Stage.EXECUCAO, Substage.EXECUCAO_NORMAL),
    "11": (Stage.EXECUCAO, Substage.EXECUCAO_SUSPENSA_TOTAL),
    "12": (Stage.EXECUCAO, Substage.EXECUCAO_SUSPENSA_PARCIAL),
    "13": (Stage.SUSPENSAO, None),
    "14": (Stage.CONVERSAO, None),
    "15": (Stage.ARQUIVAMENTO, None),
    "16": (Stage.CONTROLE, None),  # RE-07 — abstenção / revisão humana
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_hierarchical_classification.py -v`
Expected: PASS (suíte inteira, incluindo `TestStageControle` e `test_all_legacy_map_entries_covered` atualizado)

- [ ] **Step 5: Commit**

```bash
git add backend/services/hierarchical_classification.py backend/tests/test_hierarchical_classification.py
git commit -m "feat: add Stage.CONTROLE(6) as the hierarchical home for phase 16"
```

---

## Task 11: Gancho reservado para LLM futuro (§7)

**Files:**
- Modify: `backend/services/document_phase_classifier.py`
- Test: `backend/tests/test_document_phase_classifier_abstencao.py`

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_document_phase_classifier_abstencao.py`:

```python
class TestAbstentionResolverHook:
    """§7 — gancho reservado para segunda opinião via LLM, não implementado
    (no-op por padrão), apenas com a interface reservada."""

    def test_sem_resolver_comportamento_e_identico(self):
        movs = [
            _mov("Petição Inicial", "2015-04-10"),
            _mov("Andamento Processual", "2019-09-03"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "")
        assert resultado.phase == "16"

    def test_resolver_e_chamado_apenas_quando_resultado_e_16(self):
        chamadas = []

        def resolver(movimentos, resultado_preliminar):
            chamadas.append(resultado_preliminar.phase)
            return resultado_preliminar

        movs_sem_ancora = [
            _mov("Petição Inicial", "2015-04-10"),
            _mov("Andamento Processual", "2019-09-03"),
        ]
        DocumentPhaseClassifier.classify_with_trace(movs_sem_ancora, "", abstention_resolver=resolver)
        assert chamadas == ["16"]

        chamadas.clear()
        movs_com_sentenca = [_mov("Sentença", "2024-01-01")]
        DocumentPhaseClassifier.classify_with_trace(movs_com_sentenca, "", abstention_resolver=resolver)
        assert chamadas == []

    def test_resolver_pode_substituir_o_resultado(self):
        def resolver(movimentos, resultado_preliminar):
            resultado_preliminar.phase = "10"
            resultado_preliminar.motivo_abstencao = None
            return resultado_preliminar

        movs = [
            _mov("Petição Inicial", "2015-04-10"),
            _mov("Andamento Processual", "2019-09-03"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "", abstention_resolver=resolver)
        assert resultado.phase == "10"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_abstencao.py -v -k TestAbstentionResolverHook`
Expected: FAIL com `TypeError: classify_with_trace() got an unexpected keyword argument 'abstention_resolver'`

- [ ] **Step 3: Write minimal implementation**

Edit `backend/services/document_phase_classifier.py`. Old (state after Task 8):

```python
    @classmethod
    def classify_with_trace(
        cls, movimentos: List[FusionMovimento], classe_processual: str
    ) -> ClassificationResult:
        """
        Classifica fase processual e retorna trace completo da decisão.

        Args:
            movimentos: lista ordenada cronologicamente (ASC por data).
            classe_processual: classe do processo no tribunal.

        Returns:
            ClassificationResult com fase, regra aplicada, movimento decisivo, etc.
        """
        classe_norm = cls._normalize(classe_processual)

        if _is_classe_execucao(classe_norm):
            result = cls._classify_execucao_traced(movimentos, classe_norm)
        else:
            result = cls._classify_conhecimento_traced(movimentos, classe_norm)

        cls._aplicar_abstencao(result)
        cls._computar_hierarquia(result, classe_norm)
        return result
```

New:

```python
    @classmethod
    def classify_with_trace(
        cls,
        movimentos: List[FusionMovimento],
        classe_processual: str,
        abstention_resolver: Optional[
            "Callable[[List[FusionMovimento], ClassificationResult], ClassificationResult]"
        ] = None,
    ) -> ClassificationResult:
        """
        Classifica fase processual e retorna trace completo da decisão.

        Args:
            movimentos: lista ordenada cronologicamente (ASC por data).
            classe_processual: classe do processo no tribunal.
            abstention_resolver: gancho reservado (spec §7) para uma segunda
                opinião via LLM quando o resultado preliminar for "16". Não
                implementado nesta fase — default None preserva integralmente
                o comportamento atual (sem LLM). Quando fornecido, é chamado
                com (movimentos, resultado_preliminar) e deve retornar um
                ClassificationResult (podendo ser o mesmo, inalterado).

        Returns:
            ClassificationResult com fase, regra aplicada, movimento decisivo, etc.
        """
        classe_norm = cls._normalize(classe_processual)

        if _is_classe_execucao(classe_norm):
            result = cls._classify_execucao_traced(movimentos, classe_norm)
        else:
            result = cls._classify_conhecimento_traced(movimentos, classe_norm)

        cls._aplicar_abstencao(result)

        if result.phase == "16" and abstention_resolver is not None:
            result = abstention_resolver(movimentos, result)

        cls._computar_hierarquia(result, classe_norm)
        return result
```

Add `Callable` to the typing import at the top of the file. Old:

```python
from typing import List, Optional
```

New:

```python
from typing import Callable, List, Optional
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_abstencao.py -v`
Expected: PASS (suíte inteira do arquivo, incluindo `TestAbstentionResolverHook`)

- [ ] **Step 5: Commit**

```bash
git add backend/services/document_phase_classifier.py backend/tests/test_document_phase_classifier_abstencao.py
git commit -m "feat: reserve abstention_resolver extension point for future LLM second opinion (spec §7)"
```

---

## Task 12: Importação de `testes-minimos.json`

**Files:**
- Create: `backend/tests/test_document_phase_classifier_doctree_cases.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Importa e roda os casos de fase-processual-doctree/tests/testes-minimos.json
contra DocumentPhaseClassifier (spec §8.2).

Mapeamento de adaptação (árvore do doctree → FusionMovimento):
- tipo_local  <- tipo_peca (rótulo normalizável do tipo de peça)
- descricao   <- nome_arquivo sem a extensão .pdf (texto mais específico)
- tipo_cnj    <- "" (o JSON do doctree não tem equivalente ao código CNJ)
- classe_processual <- caso.get("classe_processual", "") quando informado

O arquivo se autodescreve como tendo "11 casos" (ver campo "descricao" no
JSON); a contagem real lida diretamente do arquivo (versão 1.1) é 14
(T-01 a T-14) — corrigimos essa contagem aqui como achado de leitura
primária, e travamos com test_doctree_json_has_14_cases.

Casos marcados xfail exigem capacidades explicitamente fora do escopo desta
adaptação (ver docs/superpowers/plans/2026-07-04-fase-processual-doctree-adaptation.md,
seção "Decisões técnicas resolvidas nesta fase de planejamento" e Task 12).
"""
import json
import re
from datetime import datetime
from pathlib import Path

import pytest

from backend.services.document_phase_classifier import DocumentPhaseClassifier, FusionMovimento

DOCTREE_CASES_PATH = (
    Path(__file__).resolve().parents[2] / "fase-processual-doctree" / "tests" / "testes-minimos.json"
)

with open(DOCTREE_CASES_PATH, "r", encoding="utf-8") as f:
    _DOCTREE_DATA = json.load(f)

_CASOS_POR_ID = {caso["id"]: caso for caso in _DOCTREE_DATA["casos"]}

_XFAIL_REASONS = {
    "T-04-art40-lef-nunca-15": (
        "Requer gate de dominio (execucao vs. conhecimento) inferido do "
        "CONTEUDO da peticao inicial (CDA) quando classe_processual nao e "
        "informada. Nesta adaptacao, RE-01 permanece um refactor da "
        "bifurcacao ja existente por STRING de classe (_is_classe_execucao), "
        "nao um detector de titulo executivo por texto -- decisao explicita "
        "documentada no plano para nao expandir o escopo de RE-01 alem do "
        "que a Tabela regra-a-regra do spec (secao 3) autoriza."
    ),
    "T-08-mandado-pagamento-sem-polaridade": (
        "Requer a trava financeira do arquivamento (F-13: arquivamento com "
        "destinacao financeira incerta deve abster) -- fronteira F-13 nao "
        "portada nesta fase (spec secao 1: fronteiras F-01 a F-13 nao sao "
        "portadas como regras proprias)."
    ),
    "T-09-sobrestamento-sem-retomada": (
        "RE-03.3 (spec secao 3) declara explicitamente 'sem mudanca "
        "estrutural': o pipeline P1-P6 do branch de conhecimento prioriza "
        "por TIPO de ancora (sentenca/remessa antes de suspensao), nao pela "
        "ancora mais recente entre TODOS os tipos. Corrigir isso alteraria a "
        "arquitetura de precedencia do classificador, que o spec "
        "explicitamente nao autoriza mexer para esta regra."
    ),
    "T-14-fallback-teor-ultimos-cinco": (
        "Requer leitura de teor de pecas (RE-12, segunda metade) -- fora de "
        "escopo por decisao explicita do spec secao 9 (Fase 2 separada, "
        "pendente de confirmacao do formato do MCP-PAV)."
    ),
}


def _mov_from_arvore_item(item: dict) -> FusionMovimento:
    nome_arquivo = item.get("nome_arquivo", "")
    descricao = re.sub(r"\.pdf$", "", nome_arquivo, flags=re.IGNORECASE)
    return FusionMovimento(
        data=datetime.strptime(item["data"], "%Y-%m-%d"),
        tipo_local=item.get("tipo_peca", ""),
        tipo_cnj="",
        descricao=descricao,
    )


def _classify_caso(caso: dict):
    movimentos = [_mov_from_arvore_item(item) for item in caso["arvore"]]
    classe_processual = caso.get("classe_processual", "")
    return DocumentPhaseClassifier.classify_with_trace(movimentos, classe_processual)


@pytest.mark.parametrize("caso_id", sorted(_CASOS_POR_ID.keys()))
def test_doctree_caso(caso_id):
    caso = _CASOS_POR_ID[caso_id]
    reason = _XFAIL_REASONS.get(caso_id)
    if reason:
        pytest.xfail(reason)

    resultado = _classify_caso(caso)
    esperado = caso["esperado"]

    fase_esperada = esperado.get("fase_codigo")
    if fase_esperada is not None:
        assert resultado.phase == fase_esperada, (
            f"{caso_id}: esperado fase {fase_esperada}, obtido {resultado.phase} "
            f"(regra={resultado.rule_applied})"
        )

    fase_proibida = esperado.get("fase_proibida")
    if fase_proibida is not None:
        assert resultado.phase != fase_proibida, (
            f"{caso_id}: fase {fase_proibida} e proibida, mas foi retornada"
        )

    fases_proibidas = esperado.get("fases_proibidas")
    if fases_proibidas:
        assert resultado.phase not in fases_proibidas, (
            f"{caso_id}: fase {resultado.phase} esta na lista de fases proibidas {fases_proibidas}"
        )

    fases_aceitas = esperado.get("fases_aceitas")
    if fases_aceitas:
        assert resultado.phase in fases_aceitas, (
            f"{caso_id}: fase {resultado.phase} nao esta entre as aceitas {fases_aceitas}"
        )

    confianca_min = esperado.get("confianca_min")
    if confianca_min is not None and resultado.phase != "16":
        assert resultado.confidence is not None and resultado.confidence >= confianca_min, (
            f"{caso_id}: confianca {resultado.confidence} abaixo do minimo {confianca_min}"
        )


def test_doctree_json_has_14_cases():
    assert len(_DOCTREE_DATA["casos"]) == 14
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_doctree_cases.py -v`
Expected: no primeiro run (antes de qualquer outra task), FAIL total por `ModuleNotFoundError`/`AttributeError` (nem `autor`, nem as âncoras novas existem ainda). **Nota de sequenciamento:** esta task pressupõe que as Tasks 1-11 já foram aplicadas (é a última task de regra desta adaptação); rodada nesse ponto, o comando acima deve reportar 10 PASS + 4 XFAIL (nenhum FAIL). Se estiver rodando esta task isoladamente antes das demais, espera-se FAIL nos 10 casos não-xfail.

- [ ] **Step 3: Write minimal implementation**

O arquivo de teste em si já é a implementação (Step 1) — não há mudança de código de produção nesta task. Nenhuma ação adicional além de salvar o arquivo criado no Step 1.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_doctree_cases.py -v`
Expected: PASS — 10 casos com assert real (`T-01`, `T-02`, `T-03`, `T-05`, `T-06`, `T-07`, `T-10`, `T-11`, `T-12`, `T-13`) + `test_doctree_json_has_14_cases`; 4 casos `XFAIL` (`T-04`, `T-08`, `T-09`, `T-14`). Total: 11 PASS, 4 XFAIL, 0 FAIL.

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_document_phase_classifier_doctree_cases.py
git commit -m "test: import fase-processual-doctree/tests/testes-minimos.json as pytest cases"
```

---

## Task 13: Suíte de regressão completa (verificação)

Esta task não escreve código novo — é a verificação de guarda de regressão exigida pelo spec §8.1: qualquer teste pré-existente que mudar de resultado precisa de justificativa explícita.

**Files:**
- (nenhum arquivo criado ou modificado — task de verificação)

- [ ] **Step 1: Rodar a suíte completa do backend**

Run: `cd backend && python -m pytest tests/ -v --tb=short`

Expected: 100% dos testes PASS ou XFAIL esperado (os 4 xfail da Task 12), 0 FAIL, 0 ERROR.

- [ ] **Step 2: Conferir a contagem total de testes contra a baseline pré-adaptação**

Run: `cd backend && python -m pytest tests/ --collect-only -q | tail -5`

Critério de aceite explícito: o número total de testes coletados deve ser igual à baseline (contagem antes desta adaptação: 66 + 7 + 11 + 40 parametrizados nos 4 arquivos citados no spec §8.1, mais os testes já existentes nos demais arquivos da pasta `backend/tests/`) **mais** os testes novos introduzidos pelas Tasks 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12 e 15 deste plano. Nenhum teste pré-existente deve ter sido removido ou pulado silenciosamente (exceto os 4 `xfail` documentados na Task 12, que são novos, não removções).

- [ ] **Step 3: Documentar a única mudança de resultado em teste pré-existente**

Confirmar que a ÚNICA alteração de expectativa em um teste que já existia antes desta adaptação é `test_all_legacy_map_entries_covered` (`backend/tests/test_hierarchical_classification.py`), já justificada inline no próprio teste (Task 10): o conjunto de códigos esperado passou de 15 para 16 devido à introdução do código `"16"` (RE-07). Rodar especificamente esse teste e confirmar que passa com a nova expectativa:

Run: `cd backend && python -m pytest tests/test_hierarchical_classification.py::TestDeriveLegacyPhase::test_all_legacy_map_entries_covered -v`
Expected: PASS

- [ ] **Step 4: Confirmar que os 2 asserts de confiança hardcoded permanecem inalterados**

Run: `cd backend && python -m pytest tests/test_document_phase_classifier_execucao.py -v -k confianca`
Expected: PASS — `test_confianca_reduzida_no_override` continua afirmando `resultado.confidence == 0.70` para `P0_execucao_posterior_transito` sem nenhuma mudança (a abstenção introduzida na Task 8 muda `resultado.phase` para `"16"` apenas quando chamado via `classify_with_trace` SEM filtrar por confidence diretamente — como este teste específico não verifica `resultado.phase`, apenas `resultado.confidence`, ele continua passando; o campo `confidence` nunca foi alterado por nenhuma task deste plano).

- [ ] **Step 5: Commit (apenas se algum ajuste foi necessário durante a verificação)**

Se todas as verificações acima passarem sem qualquer edição adicional, não há o que commitar nesta task — ela é puramente de verificação. Se algum ajuste pontual for necessário para reconciliar uma divergência não prevista, documentar a causa raiz no commit:

```bash
git add -A
git commit -m "test: confirm full regression suite passes after doctree rule adaptation"
```

---

## Task 14: Extensão de `reclassify_hierarchical.py` + diff de produção

**Files:**
- Modify: `backend/scripts/reclassify_hierarchical.py`
- Test: `backend/tests/test_reclassify_hierarchical.py` (novo)

- [ ] **Step 1: Write the failing test**

```python
"""
Testes para a extensão --full-reclassify de reclassify_hierarchical.py
(spec §8.3): reconstrói FusionMovimento a partir dos digests persistidos em
raw_data.__meta__ e re-executa classify_with_trace() com as regras atuais.
"""
from datetime import datetime

from backend.scripts.reclassify_hierarchical import (
    _reconstruir_movimentos_fusion, _reconstruir_movimentos_pav_tree,
    _reclassify_full_from_meta,
)


class TestReconstruirMovimentosFusion:
    def test_reconstroi_a_partir_do_digest_persistido(self):
        meta = {
            "fusion_movements": [
                {"date": "2024-01-01T00:00:00", "description": "52", "code": "Sentença", "detail": ""},
            ]
        }
        movs = _reconstruir_movimentos_fusion(meta)
        assert len(movs) == 1
        assert movs[0].tipo_local == "Sentença"
        assert movs[0].tipo_cnj == "52"
        assert movs[0].data == datetime.fromisoformat("2024-01-01T00:00:00")

    def test_lista_vazia_quando_chave_ausente(self):
        assert _reconstruir_movimentos_fusion({}) == []

    def test_ignora_movimento_malformado(self):
        meta = {"fusion_movements": [{"date": "data-invalida", "code": "X"}]}
        assert _reconstruir_movimentos_fusion(meta) == []


class TestReconstruirMovimentosPavTree:
    def test_reconstroi_apenas_name_e_date_disponiveis(self):
        """LIMITAÇÃO CONHECIDA: o digest de pav_tree_documents só grava
        {"name", "date"}; tipo_cnj/descricao ficam vazios na reconstrução."""
        meta = {"pav_tree_documents": [{"name": "Sentença", "date": "2024-01-01T00:00:00"}]}
        movs = _reconstruir_movimentos_pav_tree(meta)
        assert len(movs) == 1
        assert movs[0].tipo_local == "Sentença"
        assert movs[0].tipo_cnj == ""
        assert movs[0].descricao == ""


class TestReclassifyFullFromMeta:
    def test_reexecuta_classificacao_e_deriva_hierarquia(self):
        meta = {
            "fusion_classe_processual": "Ação Cível",
            "fusion_movements": [
                {"date": "2024-01-01T00:00:00", "description": "", "code": "Sentença", "detail": ""},
            ],
            "datajud_phase": "Indefinido",
        }
        stage, substage, transit, modo, fusion_phase_nova, pav_phase_nova = _reclassify_full_from_meta(meta)
        assert fusion_phase_nova == "02"
        assert pav_phase_nova is None
        assert stage == 1
        assert modo == "fusion_preferred"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_reclassify_hierarchical.py -v`
Expected: FAIL com `ImportError: cannot import name '_reconstruir_movimentos_fusion'`

- [ ] **Step 3: Write minimal implementation**

Edit `backend/scripts/reclassify_hierarchical.py`. Old:

```python
from backend.database import SessionLocal
from backend.models import Process, SearchHistory
from backend.services.document_phase_classifier import DocumentPhaseClassifier
from backend.services.phase_analyzer import PhaseAnalyzer
from backend.services.fusion_api_client import FusionMovimento
from backend.services.process_service import (
    _consolidar_tres_fontes, _extrair_hierarquia_da_fonte,
)
from backend.services.hierarchical_classification import (
    PHASE_TO_STAGE_SUBSTAGE, derive_legacy_phase,
    _PHASES_WITH_IMPLICIT_TRANSIT,
)
from datetime import datetime
```

New:

```python
from backend.database import SessionLocal
from backend.models import Process, SearchHistory
from backend.services.document_phase_classifier import DocumentPhaseClassifier
from backend.services.phase_analyzer import PhaseAnalyzer
from backend.services.fusion_api_client import FusionMovimento
from backend.services.process_service import (
    _consolidar_tres_fontes, _extrair_hierarquia_da_fonte,
)
from backend.services.hierarchical_classification import (
    PHASE_TO_STAGE_SUBSTAGE, derive_legacy_phase,
    _PHASES_WITH_IMPLICIT_TRANSIT,
)
from datetime import datetime


def _reconstruir_movimentos_fusion(meta: dict) -> list:
    """
    Reconstrói FusionMovimento a partir de meta['fusion_movements'], o digest
    persistido por process_service.py no formato
    {"date", "description", "code", "detail"} (mapeado de volta para
    tipo_cnj=description, tipo_local=code, descricao=detail).
    """
    movimentos = []
    for m in meta.get("fusion_movements", []) or []:
        try:
            movimentos.append(FusionMovimento(
                data=datetime.fromisoformat(m["date"]),
                tipo_local=m.get("code", ""),
                tipo_cnj=m.get("description", ""),
                descricao=m.get("detail", ""),
            ))
        except (KeyError, ValueError) as e:
            logger.warning(f"Movimento Fusion malformado ignorado: {m} ({e})")
    return movimentos


def _reconstruir_movimentos_pav_tree(meta: dict) -> list:
    """
    Reconstrói FusionMovimento a partir de meta['pav_tree_documents'].

    LIMITAÇÃO CONHECIDA: o digest persistido por process_service.py (bloco
    "PAV Document Tree") só grava {"name", "date"}, então tipo_cnj e
    descricao são reconstruídos vazios aqui. Regras que dependem
    exclusivamente de tipo_cnj/descricao (nunca de tipo_local) perdem
    precisão neste modo --full-reclassify. Aceitável para o diff de impacto
    (--dry-run), não substitui uma nova consulta real ao Fusion/PAV.
    """
    movimentos = []
    for m in meta.get("pav_tree_documents", []) or []:
        try:
            movimentos.append(FusionMovimento(
                data=datetime.fromisoformat(m["date"]),
                tipo_local=m.get("name", ""),
                tipo_cnj="",
                descricao="",
            ))
        except (KeyError, ValueError) as e:
            logger.warning(f"Documento PAV Tree malformado ignorado: {m} ({e})")
    return movimentos


def _reclassify_full_from_meta(meta: dict) -> tuple:
    """
    Modo --full-reclassify (spec §8.3): re-executa classify_with_trace() com
    as regras ATUAIS sobre os movimentos reconstruídos, em vez de reaproveitar
    o 'rule_applied'/'stage' já persistido de uma execução anterior (isso é o
    que _reclassify_from_meta faz, e continua disponível para o modo legado).

    Retorna (stage, substage, transit, modo, fusion_phase_nova, pav_phase_nova).
    """
    classe_processual = meta.get("fusion_classe_processual") or ""

    fusion_movs = _reconstruir_movimentos_fusion(meta)
    fusion_phase_nova = None
    fusion_result = None
    if fusion_movs:
        fusion_result = DocumentPhaseClassifier.classify_with_trace(fusion_movs, classe_processual)
        fusion_phase_nova = fusion_result.phase

    pav_movs = _reconstruir_movimentos_pav_tree(meta)
    pav_phase_nova = None
    pav_result = None
    if pav_movs:
        pav_result = DocumentPhaseClassifier.classify_with_trace(pav_movs, classe_processual)
        pav_phase_nova = pav_result.phase

    datajud_phase = meta.get("datajud_phase", "")

    _, modo = _consolidar_tres_fontes(
        datajud_phase, fusion_phase_nova or "Indefinido", pav_phase_nova or "Indefinido"
    )

    sim_meta = {
        "datajud_stage": meta.get("datajud_stage"),
        "datajud_substage": meta.get("datajud_substage"),
        "datajud_transit": meta.get("datajud_transit"),
        "fusion_stage": fusion_result.stage if fusion_result else None,
        "fusion_substage": fusion_result.substage if fusion_result else None,
        "fusion_transit": fusion_result.transit_julgado if fusion_result else None,
        "pav_tree_stage": pav_result.stage if pav_result else None,
        "pav_tree_substage": pav_result.substage if pav_result else None,
        "pav_tree_transit": pav_result.transit_julgado if pav_result else None,
    }
    stage, substage, transit = _extrair_hierarquia_da_fonte(modo, sim_meta)
    return stage, substage, transit, modo, fusion_phase_nova, pav_phase_nova
```

Now wire the new `--full-reclassify` flag into `reclassify_all` and the CLI. Old:

```python
def reclassify_all(dry_run: bool = False, limit: int = 0):
    """Re-classifica todos os processos no banco."""
    db = SessionLocal()
    try:
        query = db.query(Process)
        if limit > 0:
            query = query.limit(limit)

        processes = query.all()
        total = len(processes)
        updated = 0
        skipped = 0
        divergences = []

        logger.info(f"Reclassificando {total} processos (dry_run={dry_run})")

        for i, process in enumerate(processes):
            raw_data = process.raw_data or {}
            meta = raw_data.get("__meta__", {})

            # Tentar via meta completo primeiro
            stage, substage, transit, source = _reclassify_from_meta(meta)

            if stage is None:
                # Fallback: derivar do código de fase legacy
                stage, substage, transit = _reclassify_from_phase(process.phase)
                source = "legacy_fallback"
```

New:

```python
def reclassify_all(dry_run: bool = False, limit: int = 0, full_reclassify: bool = False):
    """Re-classifica todos os processos no banco.

    full_reclassify=True (spec §8.3): reconstrói os movimentos a partir dos
    digests em raw_data.__meta__ e RE-EXECUTA classify_with_trace() com as
    regras atuais (doctree), em vez de apenas re-derivar stage/substage a
    partir da fase já persistida. Use com --dry-run para gerar o diff de
    impacto (fase antiga × fase nova) antes do rollout em produção.
    """
    db = SessionLocal()
    try:
        query = db.query(Process)
        if limit > 0:
            query = query.limit(limit)

        processes = query.all()
        total = len(processes)
        updated = 0
        skipped = 0
        divergences = []
        phase_divergences = []

        logger.info(f"Reclassificando {total} processos (dry_run={dry_run}, full_reclassify={full_reclassify})")

        for i, process in enumerate(processes):
            raw_data = process.raw_data or {}
            meta = raw_data.get("__meta__", {})

            if full_reclassify:
                stage, substage, transit, source, fusion_phase_nova, pav_phase_nova = _reclassify_full_from_meta(meta)
                old_fusion_phase = meta.get("fusion_phase_override", "")
                old_pav_phase = meta.get("pav_tree_phase", "")
                if fusion_phase_nova and fusion_phase_nova != old_fusion_phase.split()[0:1]:
                    if fusion_phase_nova != (old_fusion_phase.split()[0] if old_fusion_phase.split() else ""):
                        phase_divergences.append({
                            "number": process.number, "fonte": "fusion",
                            "fase_antiga": old_fusion_phase, "fase_nova": fusion_phase_nova,
                        })
                if pav_phase_nova and pav_phase_nova != (old_pav_phase.split()[0] if old_pav_phase.split() else ""):
                    phase_divergences.append({
                        "number": process.number, "fonte": "pav_tree",
                        "fase_antiga": old_pav_phase, "fase_nova": pav_phase_nova,
                    })
            else:
                # Tentar via meta completo primeiro
                stage, substage, transit, source = _reclassify_from_meta(meta)

            if stage is None:
                # Fallback: derivar do código de fase legacy
                stage, substage, transit = _reclassify_from_phase(process.phase)
                source = "legacy_fallback"
```

Further down in the same function, extend the final summary log. Old:

```python
        if divergences:
            logger.warning(f"Divergências encontradas: {len(divergences)}")
            for d in divergences[:20]:
                logger.warning(
                    f"  {d['number']}: old={d['old_phase']} → derived={d['new_legacy']} "
                    f"(stage={d['stage']}, substage={d['substage']}, transit={d['transit']}, source={d['source']})"
                )
            if len(divergences) > 20:
                logger.warning(f"  ... e mais {len(divergences) - 20} divergências")
        else:
            logger.info("Nenhuma divergência encontrada")

    finally:
        db.close()
```

New:

```python
        if divergences:
            logger.warning(f"Divergências encontradas: {len(divergences)}")
            for d in divergences[:20]:
                logger.warning(
                    f"  {d['number']}: old={d['old_phase']} → derived={d['new_legacy']} "
                    f"(stage={d['stage']}, substage={d['substage']}, transit={d['transit']}, source={d['source']})"
                )
            if len(divergences) > 20:
                logger.warning(f"  ... e mais {len(divergences) - 20} divergências")
        else:
            logger.info("Nenhuma divergência encontrada")

        if full_reclassify:
            if phase_divergences:
                logger.warning(f"Divergências de FASE (--full-reclassify): {len(phase_divergences)}")
                for d in phase_divergences[:20]:
                    logger.warning(
                        f"  {d['number']} [{d['fonte']}]: {d['fase_antiga']} → {d['fase_nova']}"
                    )
                if len(phase_divergences) > 20:
                    logger.warning(f"  ... e mais {len(phase_divergences) - 20} divergências de fase")
            else:
                logger.info("Nenhuma divergência de fase encontrada (--full-reclassify)")

    finally:
        db.close()
```

Finally, wire the CLI flag. Old:

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reclassificação hierárquica de processos")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simula, sem gravar")
    parser.add_argument("--limit", type=int, default=0, help="Limitar a N processos (0=todos)")
    args = parser.parse_args()

    reclassify_all(dry_run=args.dry_run, limit=args.limit)
```

New:

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reclassificação hierárquica de processos")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simula, sem gravar")
    parser.add_argument("--limit", type=int, default=0, help="Limitar a N processos (0=todos)")
    parser.add_argument(
        "--full-reclassify", action="store_true",
        help=(
            "Reconstrói os movimentos a partir dos digests em raw_data.__meta__ e "
            "re-executa DocumentPhaseClassifier.classify_with_trace() com as regras "
            "atuais (doctree), em vez de apenas re-derivar stage/substage da fase já "
            "persistida. Use com --dry-run para gerar o diff de impacto antes do rollout."
        ),
    )
    args = parser.parse_args()

    reclassify_all(dry_run=args.dry_run, limit=args.limit, full_reclassify=args.full_reclassify)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_reclassify_hierarchical.py -v`
Expected: PASS (5 testes)

- [ ] **Step 5: Rodar o diff de impacto em modo dry-run (não é código, é a execução exigida pelo spec §8.3)**

Run: `cd backend && python -m backend.scripts.reclassify_hierarchical --dry-run --full-reclassify --limit 500`
Expected: o script conclui sem erro, imprime `Reclassificando N processos (dry_run=True, full_reclassify=True)` e, ao final, ou `Nenhuma divergência de fase encontrada (--full-reclassify)` ou a lista de até 20 divergências de fase (processo, fonte, fase antiga, fase nova). Nenhuma escrita no banco ocorre (`dry_run=True`). Este comando deve ser rodado contra um banco com dados reais (não vazio) antes do rollout desta adaptação em produção, para quantificar quantos processos mudariam de fase e quantos passariam a cair em `"16"`.

- [ ] **Step 6: Commit**

```bash
git add backend/scripts/reclassify_hierarchical.py backend/tests/test_reclassify_hierarchical.py
git commit -m "feat: add --full-reclassify to reclassify_hierarchical.py for pre-rollout impact diff"
```

---

## Task 15: Frontend — `phases.js` e `phaseColors.js`

**Files:**
- Modify: `frontend/src/constants/phases.js`
- Modify: `frontend/src/utils/phaseColors.js`
- Test: `frontend/src/tests/phases16.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
import { describe, it, expect } from 'vitest';
import {
  VALID_PHASES, PHASE_BY_CODE, STAGES, LEGACY_PHASE_TO_HIERARCHY,
  hierarchyToLegacyPhase, isValidPhase,
} from '../constants/phases';
import { getPhaseColorClasses, getStageColorClasses } from '../utils/phaseColors';

describe('Fase 16 — Indeterminado / Revisão Humana', () => {
  it('existe em VALID_PHASES com código 16', () => {
    expect(PHASE_BY_CODE['16']).toBeDefined();
    expect(PHASE_BY_CODE['16'].code).toBe('16');
    expect(PHASE_BY_CODE['16'].type).toBe('Controle');
  });

  it('é reconhecida como fase válida pelo nome', () => {
    expect(isValidPhase(PHASE_BY_CODE['16'].name)).toBe(true);
  });

  it('Stage 6 (Controle) existe em STAGES', () => {
    expect(STAGES[6]).toBeDefined();
    expect(STAGES[6].label).toBe('Controle / Revisão Humana');
  });

  it('LEGACY_PHASE_TO_HIERARCHY mapeia 16 para stage 6, substage null', () => {
    expect(LEGACY_PHASE_TO_HIERARCHY['16']).toEqual({ stage: 6, substage: null, transit: 'na' });
  });

  it('hierarchyToLegacyPhase(6, null, "na") retorna "16"', () => {
    expect(hierarchyToLegacyPhase(6, null, 'na')).toBe('16');
  });

  it('getPhaseColorClasses para fase 16 não usa a classe padrão de fallback cinza', () => {
    const classes = getPhaseColorClasses(PHASE_BY_CODE['16'].name);
    expect(classes).not.toContain('bg-gray-100');
  });

  it('getStageColorClasses(6) não usa a classe padrão de fallback cinza', () => {
    const classes = getStageColorClasses(6);
    expect(classes).not.toContain('bg-gray-100');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npx vitest run src/tests/phases16.test.js`
Expected: FAIL — `PHASE_BY_CODE['16']` é `undefined`, `STAGES[6]` é `undefined`, `LEGACY_PHASE_TO_HIERARCHY['16']` é `undefined`, `hierarchyToLegacyPhase(6, null, 'na')` retorna `'01'` (fallback).

- [ ] **Step 3: Write minimal implementation**

Edit `frontend/src/constants/phases.js`. Old:

```javascript
  // Fases Transversais e Finais (13, 15)
  SUSPENSO_SOBRESTADO: {
    code: '13',
    name: 'Suspenso / Sobrestado',
    type: 'Transversal',
    color: 'lime'
  },
  ARQUIVADO: {
    code: '15',
    name: 'Arquivado Definitivamente',
    type: 'Final',
    color: 'slate'
  }
};
```

New:

```javascript
  // Fases Transversais e Finais (13, 15)
  SUSPENSO_SOBRESTADO: {
    code: '13',
    name: 'Suspenso / Sobrestado',
    type: 'Transversal',
    color: 'lime'
  },
  ARQUIVADO: {
    code: '15',
    name: 'Arquivado Definitivamente',
    type: 'Final',
    color: 'slate'
  },

  // Fase de Controle (16) — RE-07 do doctree: abstenção calibrada
  INDETERMINADO_REVISAO_HUMANA: {
    code: '16',
    name: 'Indeterminado — Revisão Humana',
    type: 'Controle',
    color: 'cyan'
  }
};
```

Old:

```javascript
export const STAGES = {
  1: { value: 1, label: 'Conhecimento', color: 'blue' },
  2: { value: 2, label: 'Execução', color: 'orange' },
  3: { value: 3, label: 'Suspensão / Sobrestamento', color: 'lime' },
  4: { value: 4, label: 'Arquivamento', color: 'slate' },
  5: { value: 5, label: 'Conversão em Renda', color: 'green' },
};
```

New:

```javascript
export const STAGES = {
  1: { value: 1, label: 'Conhecimento', color: 'blue' },
  2: { value: 2, label: 'Execução', color: 'orange' },
  3: { value: 3, label: 'Suspensão / Sobrestamento', color: 'lime' },
  4: { value: 4, label: 'Arquivamento', color: 'slate' },
  5: { value: 5, label: 'Conversão em Renda', color: 'green' },
  6: { value: 6, label: 'Controle / Revisão Humana', color: 'cyan' },
};
```

Old:

```javascript
export function hierarchyToLegacyPhase(stage, substage, transit) {
  const s = Number(stage);
  if (s === 4) return '15';
  if (s === 3) return '13';
  if (s === 5) return '14';
  if (s === 2) {
    if (substage === '2.1') return '10';
    if (substage === '2.2') return '12';
    if (substage === '2.3') return '11';
    return '10';
  }
  if (s === 1) {
    if (substage === '1.1') return '01';
    if (substage === '1.2') return transit === 'sim' ? '03' : '02';
    if (substage === '1.3') return '04';
    if (substage === '1.4') return transit === 'sim' ? '06' : '05';
    if (substage === '1.5') return '07';
    if (substage === '1.6') return transit === 'sim' ? '09' : '08';
    return '01';
  }
  return '01';
}
```

New:

```javascript
export function hierarchyToLegacyPhase(stage, substage, transit) {
  const s = Number(stage);
  if (s === 6) return '16';
  if (s === 4) return '15';
  if (s === 3) return '13';
  if (s === 5) return '14';
  if (s === 2) {
    if (substage === '2.1') return '10';
    if (substage === '2.2') return '12';
    if (substage === '2.3') return '11';
    return '10';
  }
  if (s === 1) {
    if (substage === '1.1') return '01';
    if (substage === '1.2') return transit === 'sim' ? '03' : '02';
    if (substage === '1.3') return '04';
    if (substage === '1.4') return transit === 'sim' ? '06' : '05';
    if (substage === '1.5') return '07';
    if (substage === '1.6') return transit === 'sim' ? '09' : '08';
    return '01';
  }
  return '01';
}
```

Old:

```javascript
export const LEGACY_PHASE_TO_HIERARCHY = {
  '01': { stage: 1, substage: '1.1', transit: 'na'  },
  '02': { stage: 1, substage: '1.2', transit: 'nao' },
  '03': { stage: 1, substage: '1.2', transit: 'sim' },
  '04': { stage: 1, substage: '1.3', transit: 'na'  },
  '05': { stage: 1, substage: '1.4', transit: 'nao' },
  '06': { stage: 1, substage: '1.4', transit: 'sim' },
  '07': { stage: 1, substage: '1.5', transit: 'na'  },
  '08': { stage: 1, substage: '1.6', transit: 'nao' },
  '09': { stage: 1, substage: '1.6', transit: 'sim' },
  '10': { stage: 2, substage: '2.1', transit: 'na'  },
  '11': { stage: 2, substage: '2.3', transit: 'na'  },
  '12': { stage: 2, substage: '2.2', transit: 'na'  },
  '13': { stage: 3, substage: null,  transit: 'na'  },
  '14': { stage: 5, substage: null,  transit: 'na'  },
  '15': { stage: 4, substage: null,  transit: 'na'  },
};
```

New:

```javascript
export const LEGACY_PHASE_TO_HIERARCHY = {
  '01': { stage: 1, substage: '1.1', transit: 'na'  },
  '02': { stage: 1, substage: '1.2', transit: 'nao' },
  '03': { stage: 1, substage: '1.2', transit: 'sim' },
  '04': { stage: 1, substage: '1.3', transit: 'na'  },
  '05': { stage: 1, substage: '1.4', transit: 'nao' },
  '06': { stage: 1, substage: '1.4', transit: 'sim' },
  '07': { stage: 1, substage: '1.5', transit: 'na'  },
  '08': { stage: 1, substage: '1.6', transit: 'nao' },
  '09': { stage: 1, substage: '1.6', transit: 'sim' },
  '10': { stage: 2, substage: '2.1', transit: 'na'  },
  '11': { stage: 2, substage: '2.3', transit: 'na'  },
  '12': { stage: 2, substage: '2.2', transit: 'na'  },
  '13': { stage: 3, substage: null,  transit: 'na'  },
  '14': { stage: 5, substage: null,  transit: 'na'  },
  '15': { stage: 4, substage: null,  transit: 'na'  },
  '16': { stage: 6, substage: null,  transit: 'na'  },
};
```

Now edit `frontend/src/utils/phaseColors.js`. Old (in `getPhaseColorClasses`):

```javascript
    'green': 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 border border-green-200 dark:border-green-800',
    'slate': 'bg-slate-100 text-slate-800 dark:bg-slate-900/40 dark:text-slate-300 border border-slate-200 dark:border-slate-800',
  };

  return colorMap[phaseInfo.color] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300 border border-gray-200 dark:border-gray-800';
}

/**
 * Get Tailwind CSS background color class for a phase's progress bar
```

New:

```javascript
    'green': 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 border border-green-200 dark:border-green-800',
    'slate': 'bg-slate-100 text-slate-800 dark:bg-slate-900/40 dark:text-slate-300 border border-slate-200 dark:border-slate-800',
    'cyan': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-800',
  };

  return colorMap[phaseInfo.color] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300 border border-gray-200 dark:border-gray-800';
}

/**
 * Get Tailwind CSS background color class for a phase's progress bar
```

Old (in `getPhaseProgressBarClasses`):

```javascript
    'green': 'bg-green-500 dark:bg-green-400',
    'slate': 'bg-slate-500 dark:bg-slate-400',
  };

  return colorMap[phaseInfo.color] || 'bg-gray-500 dark:bg-gray-400';
}

/**
 * Get a normalized phase name for display
```

New:

```javascript
    'green': 'bg-green-500 dark:bg-green-400',
    'slate': 'bg-slate-500 dark:bg-slate-400',
    'cyan': 'bg-cyan-500 dark:bg-cyan-400',
  };

  return colorMap[phaseInfo.color] || 'bg-gray-500 dark:bg-gray-400';
}

/**
 * Get a normalized phase name for display
```

Old (in `getStageColorClasses`):

```javascript
  const colorMap = {
    'blue': 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800',
    'orange': 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300 border border-orange-200 dark:border-orange-800',
    'lime': 'bg-lime-100 text-lime-800 dark:bg-lime-900/40 dark:text-lime-300 border border-lime-200 dark:border-lime-800',
    'slate': 'bg-slate-100 text-slate-800 dark:bg-slate-900/40 dark:text-slate-300 border border-slate-200 dark:border-slate-800',
    'green': 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 border border-green-200 dark:border-green-800',
  };

  return colorMap[stageInfo.color] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300 border border-gray-200 dark:border-gray-800';
}
```

New:

```javascript
  const colorMap = {
    'blue': 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800',
    'orange': 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300 border border-orange-200 dark:border-orange-800',
    'lime': 'bg-lime-100 text-lime-800 dark:bg-lime-900/40 dark:text-lime-300 border border-lime-200 dark:border-lime-800',
    'slate': 'bg-slate-100 text-slate-800 dark:bg-slate-900/40 dark:text-slate-300 border border-slate-200 dark:border-slate-800',
    'green': 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 border border-green-200 dark:border-green-800',
    'cyan': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-800',
  };

  return colorMap[stageInfo.color] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300 border border-gray-200 dark:border-gray-800';
}
```

Old (in `getStageProgressBarClasses`):

```javascript
  const colorMap = {
    1: 'bg-blue-500 dark:bg-blue-400',
    2: 'bg-orange-500 dark:bg-orange-400',
    3: 'bg-lime-500 dark:bg-lime-400',
    4: 'bg-slate-500 dark:bg-slate-400',
    5: 'bg-green-500 dark:bg-green-400',
  };
  return colorMap[stage] || 'bg-gray-500 dark:bg-gray-400';
}
```

New:

```javascript
  const colorMap = {
    1: 'bg-blue-500 dark:bg-blue-400',
    2: 'bg-orange-500 dark:bg-orange-400',
    3: 'bg-lime-500 dark:bg-lime-400',
    4: 'bg-slate-500 dark:bg-slate-400',
    5: 'bg-green-500 dark:bg-green-400',
    6: 'bg-cyan-500 dark:bg-cyan-400',
  };
  return colorMap[stage] || 'bg-gray-500 dark:bg-gray-400';
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && npx vitest run src/tests/phases16.test.js`
Expected: PASS (7 testes)

- [ ] **Step 5: Rodar a suíte completa do frontend como guarda de regressão**

Run: `cd frontend && npx vitest run`
Expected: 100% dos testes pré-existentes continuam PASS (nenhum teste asserta `ALL_PHASES.length === 15` contra o módulo real — confirmado por busca prévia; o único teste com `toBe(6)` para `ALL_PHASES.length` usa um MOCK de 6 fases próprio do componente, não o módulo real `phases.js`, e não é afetado).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/constants/phases.js frontend/src/utils/phaseColors.js frontend/src/tests/phases16.test.js
git commit -m "feat: add phase 16 (Indeterminado - Revisao Humana) and Stage 6 to frontend"
```

---

## Autorrevisão

**1. Cobertura do spec:**

| Seção do spec | Task(s) |
|---|---|
| §2.1 (regras Python puras, sem LLM) | Tasks 2-8 (nenhuma chamada a LLM em runtime) |
| §2.2 (código "16") | Tasks 8, 9, 10 |
| §2.3 (classe única compartilhada) | Todas as tasks de regra (2-8) alteram `DocumentPhaseClassifier`, não uma classe nova |
| §2.4 (teor fora de escopo) | Task 12 (`T-14` xfail com justificativa) |
| §2.5 (gancho LLM) | Task 11 |
| §3 RE-01 | Nota "Decisões técnicas resolvidas" + Task 12 (xfail `T-04` documentado) |
| §3 RE-02 (ruído nunca decide) | Task 3 |
| §3 RE-03.1 (14>15) | Task 4 |
| §3 RE-03.2 (11 vs 12) | Task 5 |
| §3 RE-03.3 (sobrestamento sem mudança estrutural) | Nota explícita em Task 12 (`T-09` xfail, spec autoriza "sem mudança estrutural") |
| §3 RE-03.4 (domínio pegajoso) | Coberto estruturalmente pela bifurcação de branch já existente (sem task dedicada, spec não pede mudança de código) |
| §3 RE-04 (autoria) | Task 2 |
| §3 RE-05 (trânsito inferido) | Task 6 |
| §3 RE-06 (conversão em renda) | Task 4 |
| §3 RE-07 (abstenção) | Task 8 |
| §3 RE-08, RE-09 (invariantes documentais) | Já são o comportamento de fato (sem mudança de código); confirmado por `T-10` na Task 12 |
| §3 RE-10 (ERR × 16) | Resolvido: lista vazia mantém fallback `01`/`10` sem abstenção nem ERR (Task 8's gate ignora `rule_applied == "empty_list_fallback"` porque `confidence is None` para esse caso) |
| §3 RE-11 (trava de classe) | Task 7 (conflito) + comportamento já estrutural para o caso simples (`T-11`/`T-12` na Task 12) |
| §3 RE-12 (despacho ruído) | Task 3 |
| §4.1, §4.2 (modelo de dados) | Task 1 |
| §5.1 (escala de confiança) | Decisão documentada + Task 8 |
| §5.2 (consolidação) | Task 9 |
| §5.3 (16 × Indefinido) | Task 9 (tratamento uniforme e distinto) |
| §6.1 (sem migração) | Confirmado na investigação (`models.py`), nenhuma task de migração necessária |
| §6.2 (hierarquia) | Task 10 |
| §6.3 (frontend) | Task 15 |
| §7 (gancho LLM) | Task 11 |
| §8.1 (regressão) | Task 13 |
| §8.2 (testes-minimos.json) | Task 12 |
| §8.3 (diff produção) | Task 14 |
| §9 (fora de escopo) | Respeitado integralmente — nenhuma task implementa leitura de teor, chamada real a LLM, ou altera `VALID_PHASE_CODES` |

**2. Scan de placeholders proibidos:** nenhuma ocorrência de "TBD", "implementar depois", "adicionar tratamento apropriado", "similar à Task N" sem código, ou passo sem código real. Todo código mostrado é completo e sintaticamente válido Python/JavaScript.

**3. Consistência de nomes/tipos entre tasks:**
- `autor` (campo, não `author`) — definido na Task 1, usado identicamente nas Tasks 2, 12.
- `fase_provavel`/`motivo_abstencao` — definidos na Task 1, escritos exclusivamente por `_aplicar_abstencao` (Task 8), lidos na Task 8/11/12.
- `Stage.CONTROLE` (não `Stage.CONTROLE_HUMANO` nem `Stage.REVISAO`) — definido na Task 10, usado identicamente em `PHASE_TO_STAGE_SUBSTAGE`/`_LEGACY_MAP` (Task 10) e no frontend `STAGES[6]`/`LEGACY_PHASE_TO_HIERARCHY['16']` (Task 15).
- Nomes de regra (`P0c_conversao_renda`, `E0_conversao_renda`, `E1b_suspensao_parcial`, `P2b_transito_inferido`, `E2b_conflito_classe_pecas`) — definidos nas Tasks 4-7, referenciados identicamente em `_MOTIVO_ABSTENCAO_BY_RULE` (Task 8) e nos testes de cada task.
- `_scan(pattern, use_match=False)` — closure introduzida na Task 3 dentro de cada branch; Tasks 4-7 reutilizam a MESMA assinatura ao adicionar novos scans, sem redefinir a função.
- `abstention_resolver` — parâmetro definido na Task 11 com a assinatura `Optional[Callable[[List[FusionMovimento], ClassificationResult], ClassificationResult]]`, idêntica à descrita no spec §7.

**Gaps deixados conscientemente fora do escopo desta adaptação (com justificativa):**
1. **RE-01 — detecção de título executivo por conteúdo (sem `classe_processual`).** Fora de escopo porque `classe_processual` é sempre populada em produção (Fusion ou DataJud); implementar um detector de conteúdo seria código morto em produção, construído só para satisfazer casos sintéticos do doctree (`T-04` em `testes-minimos.json`, marcado `xfail`).
2. **F-13 — trava financeira do arquivamento com destinação incerta.** Fronteiras F-01 a F-13 não são portadas nesta fase por decisão explícita do spec §1 (`T-08`, `xfail`).
3. **RE-03.3 — priorização por recência entre TODOS os tipos de âncora (não só por tipo).** O spec declara explicitamente "sem mudança estrutural" para esta regra; o pipeline P1-P6 continua priorizando por TIPO de âncora, não pela âncora mais recente entre todos os tipos (`T-09`, `xfail`).
4. **RE-12, segunda metade — fallback de teor.** Fora de escopo por decisão explícita do spec §2.4/§9, pendente de confirmação do formato do MCP-PAV (`T-14`, `xfail`).
5. **Chamada real a LLM no `abstention_resolver`.** Reservado apenas como interface (Task 11); a implementação de provider/prompt/parsing é trabalho futuro por decisão explícita do spec §7/§9.
6. **`VALID_PHASE_CODES` em `backend/constants.py`.** Deliberadamente não tocado — ver nota na seção de decisões técnicas.
