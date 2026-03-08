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
