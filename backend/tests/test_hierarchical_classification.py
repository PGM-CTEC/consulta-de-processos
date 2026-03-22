"""
Testes para a classificação hierárquica em 3 campos.

Cobre:
- derive_legacy_phase: mapeamento (stage, substage, transit) → código legacy "01"-"15"
- detect_transit_from_class: detecção de trânsito pela classe processual (código)
- detect_transit_from_class_text: detecção de trânsito pela classe processual (texto)
- PHASE_TO_STAGE_SUBSTAGE: mapeamento reverso legacy → (stage, substage)
- Regressão: round-trip phase → (stage, substage, transit) → phase
- Integração: ClassificadorFases e DocumentPhaseClassifier produzem campos hierárquicos
- Consolidação: _extrair_hierarquia_da_fonte seleciona fonte vencedora
"""

import pytest
from datetime import datetime, timezone

from backend.services.hierarchical_classification import (
    Stage, Substage, Transit,
    HierarchicalResult,
    derive_legacy_phase,
    detect_transit_from_class,
    detect_transit_from_class_text,
    PHASE_TO_STAGE_SUBSTAGE,
    CLASSES_EXECUCAO_ORIGINARIA,
    CLASSES_CUMPRIMENTO_SENTENCA,
    _LEGACY_MAP,
)
from backend.services.classification_rules import (
    ClassificadorFases, ProcessoJudicial, MovimentoProcessual,
    GrauJurisdicao, ResultadoClassificacao,
)
from backend.services.document_phase_classifier import (
    DocumentPhaseClassifier, ClassificationResult,
)
from backend.services.process_service import _extrair_hierarquia_da_fonte


# ============================================================
# derive_legacy_phase — Mapeamento hierárquico → legacy
# ============================================================

class TestDeriveLegacyPhase:
    """Testa que derive_legacy_phase mapeia corretamente para os 15 códigos."""

    @pytest.mark.parametrize("stage,substage,transit,expected", [
        # Conhecimento sem trânsito
        (1, "1.1", "nao", "01"),
        (1, "1.2", "nao", "02"),
        (1, "1.3", "nao", "04"),
        (1, "1.4", "nao", "05"),
        (1, "1.5", "nao", "07"),
        (1, "1.6", "nao", "08"),
        # Conhecimento com trânsito
        (1, "1.1", "sim", "03"),
        (1, "1.2", "sim", "03"),
        (1, "1.3", "sim", "06"),
        (1, "1.4", "sim", "06"),
        (1, "1.5", "sim", "09"),
        (1, "1.6", "sim", "09"),
        # Conhecimento com "na"
        (1, "1.1", "na", "01"),
        (1, "1.2", "na", "02"),
        # Execução
        (2, "2.1", "sim", "10"),
        (2, "2.1", "nao", "10"),
        (2, "2.1", "na", "10"),
        (2, "2.2", "sim", "12"),
        (2, "2.3", "sim", "11"),
        # Suspensão
        (3, None, "sim", "13"),
        (3, None, "nao", "13"),
        (3, None, "na", "13"),
        # Arquivamento
        (4, None, "sim", "15"),
        (4, None, "nao", "15"),
        # Conversão
        (5, None, "sim", "14"),
        (5, None, "nao", "14"),
    ])
    def test_mappings(self, stage, substage, transit, expected):
        assert derive_legacy_phase(stage, substage, transit) == expected

    def test_fallback_unknown_combo(self):
        """Combinação desconhecida retorna '01' como fallback."""
        assert derive_legacy_phase(99, "9.9", "unknown") == "01"

    def test_all_legacy_map_entries_covered(self):
        """Todos os 15 códigos são alcançáveis pelo _LEGACY_MAP."""
        all_codes = set(_LEGACY_MAP.values())
        expected_codes = {f"{i:02d}" for i in range(1, 16)}
        assert expected_codes == all_codes


# ============================================================
# PHASE_TO_STAGE_SUBSTAGE — Mapeamento reverso legacy → hierárquico
# ============================================================

class TestPhaseToStageSubstage:
    """Testa que todos os 15 códigos legacy mapeiam para (stage, substage)."""

    def test_all_15_codes_present(self):
        for i in range(1, 16):
            code = f"{i:02d}"
            assert code in PHASE_TO_STAGE_SUBSTAGE, f"Código {code} não encontrado"

    @pytest.mark.parametrize("code,expected_stage,expected_substage", [
        ("01", Stage.CONHECIMENTO, Substage.ANTES_SENTENCA),
        ("02", Stage.CONHECIMENTO, Substage.SENTENCA_PROFERIDA),
        ("03", Stage.CONHECIMENTO, Substage.SENTENCA_PROFERIDA),  # transit=sim
        ("04", Stage.CONHECIMENTO, Substage.PENDENTE_TRIBUNAL_LOCAL),
        ("05", Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_LOCAL),
        ("06", Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_LOCAL),  # transit=sim
        ("07", Stage.CONHECIMENTO, Substage.PENDENTE_TRIBUNAL_SUPERIOR),
        ("08", Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_SUPERIOR),
        ("09", Stage.CONHECIMENTO, Substage.JULGAMENTO_TRIBUNAL_SUPERIOR),  # transit=sim
        ("10", Stage.EXECUCAO, Substage.EXECUCAO_NORMAL),
        ("11", Stage.EXECUCAO, Substage.EXECUCAO_SUSPENSA_TOTAL),
        ("12", Stage.EXECUCAO, Substage.EXECUCAO_SUSPENSA_PARCIAL),
        ("13", Stage.SUSPENSAO, None),
        ("14", Stage.CONVERSAO, None),
        ("15", Stage.ARQUIVAMENTO, None),
    ])
    def test_reverse_mapping(self, code, expected_stage, expected_substage):
        stage, substage = PHASE_TO_STAGE_SUBSTAGE[code]
        assert stage == expected_stage
        assert substage == expected_substage


# ============================================================
# Regressão: round-trip phase → hierarchy → phase
# ============================================================

class TestRoundTrip:
    """Verifica que derive_legacy_phase reconstrói o código correto."""

    # Mapeamento completo: (fase_original, transit esperado) → mesma fase
    _ROUND_TRIP_CASES = [
        ("01", "nao"),
        ("02", "nao"),
        ("03", "sim"),
        ("04", "nao"),
        ("05", "nao"),
        ("06", "sim"),
        ("07", "nao"),
        ("08", "nao"),
        ("09", "sim"),
        ("10", "sim"),   # Execução: transit irrelevante
        ("11", "sim"),
        ("12", "sim"),
        ("13", "nao"),
        ("14", "nao"),
        ("15", "nao"),
    ]

    @pytest.mark.parametrize("original_phase,transit", _ROUND_TRIP_CASES)
    def test_round_trip(self, original_phase, transit):
        """Fase legacy → (stage, substage) → derive → mesma fase."""
        stage, substage = PHASE_TO_STAGE_SUBSTAGE[original_phase]
        derived = derive_legacy_phase(stage, substage, transit)
        assert derived == original_phase, (
            f"Round-trip falhou: {original_phase} → ({stage}, {substage}, {transit}) → {derived}"
        )


# ============================================================
# detect_transit_from_class — Detecção por código numérico
# ============================================================

class TestDetectTransitFromClass:
    """Testa detecção de trânsito pela classe processual (código numérico)."""

    def test_execucao_fiscal_na(self):
        assert detect_transit_from_class(1116, "Execução Fiscal") == Transit.NA

    def test_execucao_titulo_extrajudicial_na(self):
        assert detect_transit_from_class(159, "Execução de Título Extrajudicial") == Transit.NA

    def test_cumprimento_sentenca_sim(self):
        assert detect_transit_from_class(156, "Cumprimento de Sentença") == Transit.SIM

    def test_cumprimento_sentenca_contra_fp_sim(self):
        assert detect_transit_from_class(12078, "Cumprimento de Sentença contra a Fazenda Pública") == Transit.SIM

    def test_cumprimento_provisorio_none(self):
        """Cumprimento provisório NÃO implica trânsito."""
        assert detect_transit_from_class(156, "Cumprimento Provisório de Sentença") is None

    def test_classe_desconhecida_none(self):
        """Classe normal retorna None (requer análise de movimentos)."""
        assert detect_transit_from_class(7, "Procedimento Comum") is None

    def test_all_exec_originaria_codes(self):
        for code in CLASSES_EXECUCAO_ORIGINARIA:
            assert detect_transit_from_class(code, "") == Transit.NA

    def test_all_cumprimento_codes(self):
        for code in CLASSES_CUMPRIMENTO_SENTENCA:
            assert detect_transit_from_class(code, "Cumprimento de Sentença") == Transit.SIM


# ============================================================
# detect_transit_from_class_text — Detecção por texto normalizado
# ============================================================

class TestDetectTransitFromClassText:
    """Testa detecção de trânsito pela descrição textual da classe."""

    def test_execucao_fiscal_na(self):
        assert detect_transit_from_class_text("execucao fiscal") == Transit.NA

    def test_execucao_titulo_extrajudicial_na(self):
        assert detect_transit_from_class_text("execucao de titulo extrajudicial") == Transit.NA

    def test_cumprimento_sim(self):
        assert detect_transit_from_class_text("cumprimento de sentenca") == Transit.SIM

    def test_cumprimento_provisorio_none(self):
        assert detect_transit_from_class_text("cumprimento provisorio de sentenca") is None

    def test_procedimento_comum_none(self):
        assert detect_transit_from_class_text("procedimento comum") is None


# ============================================================
# HierarchicalResult — Dataclass
# ============================================================

class TestHierarchicalResult:

    def test_to_dict(self):
        hr = HierarchicalResult(
            stage=Stage.CONHECIMENTO,
            substage=Substage.SENTENCA_PROFERIDA,
            transit_julgado=Transit.SIM,
            phase_legacy="03",
            confidence=0.9,
            rules_applied=["T1", "K5"],
        )
        d = hr.to_dict()
        assert d["stage"] == 1
        assert d["stage_label"] == "Conhecimento"
        assert d["substage"] == "1.2"
        assert d["substage_label"] == "Sentença Proferida"
        assert d["transit_julgado"] == "sim"
        assert d["phase_legacy"] == "03"
        assert d["confidence"] == 0.9
        assert d["rules_applied"] == ["T1", "K5"]

    def test_default_rules_applied(self):
        hr = HierarchicalResult(stage=1, substage=None, transit_julgado="nao", phase_legacy="01")
        assert hr.rules_applied == []


# ============================================================
# Integração: ClassificadorFases produz campos hierárquicos
# ============================================================

class TestClassificadorFasesHierarquia:
    """Verifica que ClassificadorFases preenche stage/substage/transit."""

    def _make_processo(self, classe_codigo=7, classe_descricao="Procedimento Comum",
                       movimentos=None, grau=GrauJurisdicao.G1, situacao="MOVIMENTO"):
        return ProcessoJudicial(
            numero="0000001-00.2020.8.19.0001",
            classe_codigo=classe_codigo,
            classe_descricao=classe_descricao,
            grau_atual=grau,
            situacao=situacao,
            movimentos=movimentos or [],
            documentos=[],
            polo_fazenda="RE",
        )

    def test_fase_01_hierarquia(self):
        """Processo sem movimentos → 01 → stage=1, substage=1.1, transit=nao."""
        processo = self._make_processo()
        resultado = ClassificadorFases().classificar(processo)
        assert resultado.fase.value == "01"
        assert resultado.stage == Stage.CONHECIMENTO
        assert resultado.substage == Substage.ANTES_SENTENCA
        assert resultado.transit_julgado == Transit.NAO

    def test_execucao_fiscal_hierarquia(self):
        """Execução fiscal → stage=2, transit=na."""
        processo = self._make_processo(classe_codigo=1116, classe_descricao="Execução Fiscal")
        resultado = ClassificadorFases().classificar(processo)
        assert resultado.stage == Stage.EXECUCAO
        assert resultado.transit_julgado == Transit.NA

    def test_cumprimento_sentenca_hierarquia(self):
        """Cumprimento de sentença → transit=sim."""
        processo = self._make_processo(classe_codigo=156, classe_descricao="Cumprimento de Sentença")
        resultado = ClassificadorFases().classificar(processo)
        assert resultado.transit_julgado == Transit.SIM

    def test_resultado_to_hierarchical(self):
        """ResultadoClassificacao.to_hierarchical() retorna HierarchicalResult."""
        processo = self._make_processo()
        resultado = ClassificadorFases().classificar(processo)
        hr = resultado.to_hierarchical()
        assert isinstance(hr, HierarchicalResult)
        assert hr.stage == resultado.stage
        assert hr.substage == resultado.substage
        assert hr.transit_julgado == resultado.transit_julgado

    def test_resultado_to_dict_includes_hierarchy(self):
        """ResultadoClassificacao.to_dict() inclui campos hierárquicos."""
        processo = self._make_processo()
        resultado = ClassificadorFases().classificar(processo)
        d = resultado.to_dict()
        assert "stage" in d
        assert "substage" in d
        assert "transit_julgado" in d

    def test_arquivamento_hierarquia(self):
        """Baixa definitiva (cod 22) → stage=4 (Arquivamento)."""
        movs = [
            MovimentoProcessual(
                codigo=22, descricao="Baixa Definitiva",
                data=datetime(2023, 1, 1, tzinfo=timezone.utc),
                grau=GrauJurisdicao.G1,
            )
        ]
        processo = self._make_processo(movimentos=movs, situacao="BAIXADO")
        resultado = ClassificadorFases().classificar(processo)
        assert resultado.fase.value == "15"
        assert resultado.stage == Stage.ARQUIVAMENTO


# ============================================================
# Integração: DocumentPhaseClassifier produz campos hierárquicos
# ============================================================

class TestDocumentPhaseClassifierHierarquia:
    """Verifica que DocumentPhaseClassifier preenche stage/substage/transit."""

    def _make_movement(self, tipo_cnj, data_str="2024-01-15"):
        from backend.services.fusion_api_client import FusionMovimento
        return FusionMovimento(
            data=datetime.fromisoformat(data_str),
            tipo_cnj=tipo_cnj,
            tipo_local=tipo_cnj,
            descricao=tipo_cnj,
        )

    def test_fallback_01_hierarquia(self):
        """Sem âncoras → 01 → stage=1, substage=1.1, transit=nao."""
        movs = [self._make_movement("Juntada de Petição")]
        result = DocumentPhaseClassifier.classify_with_trace(movs, "Procedimento Comum")
        assert result.phase == "01"
        assert result.stage == Stage.CONHECIMENTO
        assert result.substage == Substage.ANTES_SENTENCA
        assert result.transit_julgado == Transit.NAO

    def test_sentenca_hierarquia(self):
        """Sentença → 02 → stage=1, substage=1.2, transit=nao."""
        movs = [self._make_movement("Sentença")]
        result = DocumentPhaseClassifier.classify_with_trace(movs, "Procedimento Comum")
        assert result.phase == "02"
        assert result.stage == Stage.CONHECIMENTO
        assert result.substage == Substage.SENTENCA_PROFERIDA
        assert result.transit_julgado == Transit.NAO

    def test_exec_fiscal_transit_na(self):
        """Execução fiscal → transit=na."""
        movs = [self._make_movement("Juntada de Petição")]
        result = DocumentPhaseClassifier.classify_with_trace(movs, "Execução Fiscal")
        assert result.transit_julgado == Transit.NA

    def test_cumprimento_sentenca_transit_sim(self):
        """Cumprimento de sentença → transit=sim."""
        movs = [self._make_movement("Juntada de Petição")]
        result = DocumentPhaseClassifier.classify_with_trace(movs, "Cumprimento de Sentença")
        assert result.transit_julgado == Transit.SIM

    def test_to_dict_includes_hierarchy(self):
        """ClassificationResult.to_dict() inclui campos hierárquicos."""
        movs = [self._make_movement("Juntada de Petição")]
        result = DocumentPhaseClassifier.classify_with_trace(movs, "Procedimento Comum")
        d = result.to_dict()
        assert "stage" in d
        assert "substage" in d
        assert "transit_julgado" in d


# ============================================================
# PhaseAnalyzer — analyze_full e analyze_unified_full
# ============================================================

class TestPhaseAnalyzerHierarquia:
    """Verifica que PhaseAnalyzer retorna ResultadoClassificacao com hierarquia."""

    def test_analyze_full_returns_resultado(self):
        from backend.services.phase_analyzer import PhaseAnalyzer
        resultado = PhaseAnalyzer.analyze_full(
            class_code=7, movements=[], tribunal="TJRJ", grau="G1",
            process_number="0000001-00.2020.8.19.0001"
        )
        assert isinstance(resultado, ResultadoClassificacao)
        assert resultado.stage is not None
        assert resultado.transit_julgado in ("sim", "nao", "na")

    def test_analyze_full_exec_fiscal(self):
        from backend.services.phase_analyzer import PhaseAnalyzer
        resultado = PhaseAnalyzer.analyze_full(
            class_code=1116, movements=[], tribunal="TJRJ", grau="G1",
            process_number="0000001-00.2020.8.19.0001"
        )
        assert resultado.transit_julgado == Transit.NA

    def test_analyze_unified_full_returns_resultado(self):
        from backend.services.phase_analyzer import PhaseAnalyzer
        instances = [{
            "grau": "G1",
            "tribunal": "TJRJ",
            "movimentos": [],
            "classe": {"codigo": 7, "nome": "Procedimento Comum"},
        }]
        resultado = PhaseAnalyzer.analyze_unified_full(
            instances, process_number="0000001-00.2020.8.19.0001"
        )
        assert isinstance(resultado, ResultadoClassificacao)
        assert resultado.stage is not None


# ============================================================
# _extrair_hierarquia_da_fonte — Seleção de fonte vencedora
# ============================================================

class TestExtrairHierarquiaDaFonte:
    """Testa a extração de campos hierárquicos baseado no modo de consolidação."""

    _META = {
        "pav_tree_stage": 1, "pav_tree_substage": "1.4", "pav_tree_transit": "nao",
        "fusion_stage": 2, "fusion_substage": "2.1", "fusion_transit": "sim",
        "datajud_stage": 1, "datajud_substage": "1.1", "datajud_transit": "nao",
    }

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

    def test_missing_keys_returns_none(self):
        """Meta sem keys de hierarquia retorna None para todos."""
        meta = {"datajud_phase": "01 Antes da Sentença"}
        assert _extrair_hierarquia_da_fonte("datajud_fallback", meta) == (None, None, None)


# ============================================================
# Stage/Substage/Transit — Constantes
# ============================================================

class TestConstants:

    def test_stage_labels_complete(self):
        for val in [1, 2, 3, 4, 5]:
            assert val in Stage.LABELS

    def test_substage_labels_complete(self):
        for ss in ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "2.1", "2.2", "2.3"]:
            assert ss in Substage.LABELS

    def test_transit_values(self):
        assert Transit.SIM == "sim"
        assert Transit.NAO == "nao"
        assert Transit.NA == "na"
