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


# ====================================================================
# Falha 1: Arquivamento seguido de movimentos posteriores
# ====================================================================

class TestArquivamentoComAtividadePosterior:
    """Arquivamento NÃO deve forçar Fase 15 se há atividade posterior."""

    def test_arquivamento_com_peticao_posterior_nao_retorna_15(self):
        """Arquivamento + >5 movimentos posteriores → NÃO é Fase 15."""
        movimentos = [
            _mov("Arquivamento", "01/01/2024 10:00"),
            _mov("Despacho", "01/02/2024 10:00"),
            _mov("Intimação", "01/03/2024 10:00"),
            _mov("Decisão", "01/04/2024 10:00"),
            _mov("Citação", "01/05/2024 10:00"),
            _mov("Audiência", "01/06/2024 10:00"),
            _mov("Sentença", "01/07/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result != "15"

    def test_arquivamento_com_desarquivamento_posterior(self):
        """Arquivamento + Desarquivamento + >5 atividades → NÃO é Fase 15."""
        movimentos = [
            _mov("Sentença", "01/01/2024 10:00"),
            _mov("Arquivamento", "01/02/2024 10:00"),
            _mov("Desarquivamento", "01/03/2024 10:00"),
            _mov("Despacho", "01/04/2024 10:00"),
            _mov("Intimação", "01/05/2024 10:00"),
            _mov("Decisão", "01/06/2024 10:00"),
            _mov("Citação", "01/07/2024 10:00"),
            _mov("Audiência", "01/08/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result != "15"

    def test_arquivamento_sem_atividade_posterior_retorna_15(self):
        """Arquivamento como último movimento → É Fase 15."""
        movimentos = [
            _mov("Sentença", "01/01/2024 10:00"),
            _mov("Trânsito em Julgado", "01/02/2024 10:00"),
            _mov("Arquivamento", "01/03/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "15"

    def test_arquivamento_com_redistribuicao_posterior(self):
        """Arquivamento + >5 atividades com redistribuição → NÃO Fase 15."""
        movimentos = [
            _mov("Arquivamento", "01/01/2024 10:00"),
            _mov("Redistribuição", "01/02/2024 10:00"),
            _mov("Despacho", "01/03/2024 10:00"),
            _mov("Intimação", "01/04/2024 10:00"),
            _mov("Decisão", "01/05/2024 10:00"),
            _mov("Citação", "01/06/2024 10:00"),
            _mov("Audiência", "01/07/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result != "15"

    def test_arquivamento_com_poucos_movimentos_posteriores_mantem_15(self):
        """Arquivamento + poucos movimentos posteriores (<=5) → mantém Fase 15."""
        movimentos = [
            _mov("Arquivamento", "01/01/2024 10:00"),
            _mov("Intimação", "01/02/2024 10:00"),
            _mov("Citação", "01/03/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "15"

    def test_arquivamento_unico_movimento_retorna_15(self):
        """Arquivamento como único movimento → Fase 15."""
        result = DocumentPhaseClassifier.classify(
            [_mov("Arquivamento")], "Ação Cível"
        )
        assert result == "15"

    def test_multiplos_arquivamentos_com_desarquivamento_intercalado(self):
        """Arq → Desarq → Arq final (sem posterior) → Fase 15."""
        movimentos = [
            _mov("Arquivamento", "01/01/2024 10:00"),
            _mov("Desarquivamento", "01/02/2024 10:00"),
            _mov("Arquivamento", "01/06/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "15"

    def test_execucao_arquivamento_com_citacao_posterior(self):
        """Execução: Arquivamento + >5 atividades → NÃO Fase 15."""
        movimentos = [
            _mov("Arquivamento", "01/01/2024 10:00"),
            _mov("Citação", "01/02/2024 10:00"),
            _mov("Despacho", "01/03/2024 10:00"),
            _mov("Intimação", "01/04/2024 10:00"),
            _mov("Decisão", "01/05/2024 10:00"),
            _mov("Mandado", "01/06/2024 10:00"),
            _mov("Diligência", "01/07/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Execução Fiscal")
        assert result != "15"

    def test_execucao_arquivamento_final_retorna_15(self):
        """Execução: Arquivamento como último movimento → Fase 15."""
        movimentos = [
            _mov("Petição", "01/01/2024 10:00"),
            _mov("Arquivamento", "01/06/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Execução Fiscal")
        assert result == "15"


# ====================================================================
# Falha 2: Ordenamento progressivo de fases
# ====================================================================

class TestOrdenamentoProgressivo:
    """Fases são progressivas — classe de execução nunca retorna conhecimento."""

    def test_classe_execucao_nunca_retorna_fase_conhecimento(self):
        """Classe de execução → sempre Fase 10+ (nunca 01-09)."""
        classes_exec = [
            "Cumprimento de sentença",
            "Execução fiscal",
            "Execução",
            "Execução de Título Extrajudicial",
        ]
        for cls_name in classes_exec:
            result = DocumentPhaseClassifier.classify([], cls_name)
            assert int(result) >= 10, f"{cls_name} retornou fase {result}"

    def test_execucao_vazia_retorna_10(self):
        """Execução sem movimentos → Fase 10 (fallback)."""
        result = DocumentPhaseClassifier.classify([], "Execução Fiscal")
        assert result == "10"

    def test_muitos_movimentos_sem_ancora_alerta_no_trace(self):
        """Processo com 20+ movimentos sem âncoras gera rule ALERT."""
        movimentos = [
            _mov(f"Ato Ordinatório {i}", f"{i:02d}/01/2024 10:00")
            for i in range(1, 22)
        ]
        result = DocumentPhaseClassifier.classify_with_trace(movimentos, "Ação Cível")
        assert result.phase == "01"
        assert "ALERT" in result.rule_applied


# ====================================================================
# Falha 3: Considerar conjunto completo de movimentos
# ====================================================================

class TestContextSummaryEConfidence:
    """ClassificationResult deve incluir contexto e confiança."""

    def test_trace_inclui_context_summary(self):
        """classify_with_trace deve preencher context_summary."""
        movimentos = [
            _mov("Sentença", "01/01/2024 10:00"),
            _mov("Trânsito em Julgado", "01/03/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify_with_trace(movimentos, "Ação Cível")
        assert result.context_summary is not None
        assert result.context_summary.get("total") == 2
        assert result.context_summary["anchor_counts"]["transito"] >= 1
        assert result.context_summary["anchor_counts"]["sentenca"] >= 1

    def test_confidence_preenchida(self):
        """classify_with_trace deve preencher campo confidence."""
        movimentos = [
            _mov("Sentença", "01/01/2024 10:00"),
            _mov("Trânsito em Julgado", "01/03/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify_with_trace(movimentos, "Ação Cível")
        assert result.confidence is not None
        assert 0.0 < result.confidence <= 1.0

    def test_confidence_alta_com_multiplas_ancoras_coerentes(self):
        """Sentença + Trânsito → confiança alta (>= 0.85)."""
        movimentos = [
            _mov("Sentença", "01/01/2024 10:00"),
            _mov("Trânsito em Julgado", "01/03/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify_with_trace(movimentos, "Ação Cível")
        assert result.confidence >= 0.85

    def test_confidence_baixa_fallback_muitos_movimentos(self):
        """Fallback com muitos movimentos → confiança baixa (<= 0.50)."""
        movimentos = [
            _mov(f"Ato Ordinatório {i}", f"{i:02d}/01/2024 10:00")
            for i in range(1, 22)
        ]
        result = DocumentPhaseClassifier.classify_with_trace(movimentos, "Ação Cível")
        assert result.confidence is not None
        assert result.confidence <= 0.50

    def test_to_dict_inclui_novos_campos(self):
        """to_dict() deve incluir confidence e context_summary."""
        movimentos = [_mov("Sentença", "01/01/2024 10:00")]
        result = DocumentPhaseClassifier.classify_with_trace(movimentos, "Ação Cível")
        d = result.to_dict()
        assert "confidence" in d
        assert "context_summary" in d


# ====================================================================
# Suspensão com atividade posterior
# ====================================================================

class TestSuspensaoComAtividadePosterior:
    """Suspensão NÃO deve forçar Fase 13 se há atividade posterior."""

    def test_suspensao_com_despacho_posterior_nao_retorna_13(self):
        """Suspensão + >5 atividades posteriores → NÃO é Fase 13."""
        movimentos = [
            _mov("Suspensão", "01/01/2024 10:00"),
            _mov("Despacho", "01/02/2024 10:00"),
            _mov("Intimação", "01/03/2024 10:00"),
            _mov("Decisão", "01/04/2024 10:00"),
            _mov("Citação", "01/05/2024 10:00"),
            _mov("Audiência", "01/06/2024 10:00"),
            _mov("Mandado", "01/07/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result != "13"

    def test_suspensao_sem_atividade_posterior_retorna_13(self):
        """Suspensão como último evento relevante → Fase 13."""
        movimentos = [
            _mov("Petição Inicial", "01/01/2024 10:00"),
            _mov("Suspensão", "01/06/2024 10:00"),
        ]
        result = DocumentPhaseClassifier.classify(movimentos, "Ação Cível")
        assert result == "13"
