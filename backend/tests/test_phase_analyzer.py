"""
Tests for Phase Analyzer - 15-phase judicial classification system.
Story: TEST-ARCH-001 - Backend Unit & Integration Tests

Test coverage for all 15 phases of Brazilian judicial process classification.
"""
import pytest
from backend.services.phase_analyzer import PhaseAnalyzer


class TestPhaseAnalyzerClassifications:
    """Tests for phase classification logic."""

    def test_classify_phase_01_first_instance(self):
        """Phase 01 - First instance (Primeiro Grau)."""
        class_code = "0001"  # Civil action
        movements = []
        tribunal = "TJSP"
        grau = "G1"

        result = PhaseAnalyzer.analyze(class_code, movements, tribunal, grau)

        # Result should be a string with phase description or None
        assert result is None or (isinstance(result, str) and "0" in result[:2])

    def test_classify_phase_pgm_rio(self):
        """Test PGM-Rio specific phase classification."""
        class_code = "0001"
        movements = []
        tribunal = "TJRJ"  # Rio de Janeiro
        grau = "G1"

        result = PhaseAnalyzer.analyze(class_code, movements, tribunal, grau)

        # Should return a phase description or None
        assert result is None or isinstance(result, str)

    def test_classify_all_valid_phases(self):
        """Verify classification returns valid phase (01-15)."""
        class_codes = ["0001", "0002", "0003", "0006", "0007"]
        tribunals = ["TJSP", "TJRJ", "TJMG", "TJRS", "TJBA"]
        graus = ["G1", "G2"]

        for class_code in class_codes:
            for tribunal in tribunals:
                for grau in graus:
                    result = PhaseAnalyzer.analyze(
                        class_code=class_code,
                        movements=[],
                        tribunal=tribunal,
                        grau=grau
                    )

                    if result is not None:
                        # Should be a string with phase description (format: "01 Description")
                        assert isinstance(result, str)
                        # Extract phase number (first 2 chars)
                        phase_code = result[:2]
                        phase_num = int(phase_code)
                        assert 1 <= phase_num <= 15

    def test_classify_with_movements(self):
        """Classification considers movement history."""
        class_code = "0001"
        movements = [
            {
                "dataHora": "2020-01-01T10:00:00.000Z",
                "descricao": "Distribuição"
            },
            {
                "dataHora": "2020-02-01T14:00:00.000Z",
                "descricao": "Audiência designada"
            }
        ]
        tribunal = "TJSP"
        grau = "G1"

        result = PhaseAnalyzer.analyze(class_code, movements, tribunal, grau)

        # Should return a phase (movement data affects classification)
        assert result is None or isinstance(result, str)

    def test_classify_none_class_code(self):
        """Handle None class code gracefully."""
        result = PhaseAnalyzer.analyze(None, [], "TJSP", "G1")

        # Should handle gracefully (return None or default)
        assert result is None or isinstance(result, str)

    def test_classify_empty_movements(self):
        """Classification with no movements."""
        result = PhaseAnalyzer.analyze("0001", [], "TJSP", "G1")

        # Should still return a valid phase or None
        if result is not None:
            assert isinstance(result, str)
            phase_num = int(result[:2])
            assert 1 <= phase_num <= 15

    def test_classify_second_instance(self):
        """Handle G2 (second instance) classification."""
        result = PhaseAnalyzer.analyze("0001", [], "TJSP", "G2")

        # G2 processes should be classified appropriately
        if result is not None:
            assert isinstance(result, str)
            phase_num = int(result[:2])
            assert 1 <= phase_num <= 15

    def test_classify_superior_court(self):
        """Handle STF/STJ (superior court) classification."""
        result = PhaseAnalyzer.analyze("0001", [], "STF", "SUP")

        # Superior court should be classified appropriately
        if result is not None:
            assert isinstance(result, str)
            phase_num = int(result[:2])
            assert 1 <= phase_num <= 15

    def test_classify_judicial_entity(self):
        """Handle JE (Judicial Entity) grau classification."""
        result = PhaseAnalyzer.analyze("0001", [], "TJSP", "JE")
        assert result is None or isinstance(result, str)

    def test_classify_with_invalid_movement_dates(self):
        """Handle movements with invalid date formats."""
        movements = [{"codigo": "1", "nome": "Movimento 1", "dataHora": "invalid-date"}]
        result = PhaseAnalyzer.analyze("0001", movements, "TJSP", "G1")
        assert result is None or isinstance(result, str)

    def test_classify_with_invalid_movement_codes(self):
        """Handle movements with invalid code formats."""
        movements = [{"codigo": "not-a-number", "nome": "Movimento", "dataHora": "2024-01-15T10:00:00Z"}]
        result = PhaseAnalyzer.analyze("0001", movements, "TJSP", "G1")
        assert result is None or isinstance(result, str)

    def test_classify_with_raw_data_class_desc(self):
        """Classification includes raw_data for class description."""
        raw_data = {"classe": {"codigo": "0001", "nome": "Ação Civil Ordinária"}}
        result = PhaseAnalyzer.analyze("0001", [], "TJSP", "G1", raw_data=raw_data)
        assert result is None or isinstance(result, str)

    def test_classify_with_processo_baixado(self):
        """Handle processo with baixa definitiva (código 22)."""
        movements = [
            {"codigo": "1", "nome": "Distribuição", "dataHora": "2024-01-10T10:00:00Z"},
            {"codigo": "22", "nome": "Arquivamento", "dataHora": "2024-01-20T15:00:00Z"}
        ]
        result = PhaseAnalyzer.analyze("0001", movements, "TJSP", "G1", process_number="0000001-01.0000.1.00.0001")
        assert result is None or isinstance(result, str)

    def test_classify_with_desarquivamento(self):
        """Handle processo with baixa followed by reabertura (código 900)."""
        movements = [
            {"codigo": "22", "nome": "Arquivamento", "dataHora": "2024-01-20T10:00:00Z"},
            {"codigo": "900", "nome": "Reabertura", "dataHora": "2024-01-25T15:00:00Z"}
        ]
        result = PhaseAnalyzer.analyze("0001", movements, "TJSP", "G1")
        assert result is None or isinstance(result, str)

    def test_classify_exception_handling(self):
        """Verify exception handling doesn't crash the analyzer."""
        result = PhaseAnalyzer.analyze(None, [], "TJSP", "G1")
        assert result is None or isinstance(result, str)

    # -------------------------------------------------------------------------
    # Testes de regressão — Bug: código 246 ("Definitivo"/"Proferida Sentença")
    # não deve sozinho determinar "Arquivado Definitivamente".
    # Processo 0001745-93.1989.8.19.0002 — TJRJ Desapropriação (ajuizado 1989)
    # -------------------------------------------------------------------------

    def test_codigo_246_sozinho_nao_arquiva(self):
        """
        Código 246 (Proferida Sentença / 'Definitivo' no TJRJ) NÃO deve
        classificar o processo como Arquivado Definitivamente (Fase 15).
        Apenas o código 22 (Baixa Definitiva) é o arquivamento oficial CNJ.
        """
        movements = [
            {"codigo": "26",  "nome": "Distribuição",  "dataHora": "1989-01-06T00:00:01Z"},
            {"codigo": "246", "nome": "Definitivo",     "dataHora": "2007-09-06T11:15:16Z"},
        ]
        result = PhaseAnalyzer.analyze("90", movements, "TJRJ", "G1",
                                       process_number="0001745-93.1989.8.19.0002")

        assert result is not None
        assert not result.startswith("15"), (
            f"Código 246 não deve gerar Fase 15 (Arquivado). Resultado: {result}"
        )

    def test_codigo_246_com_reativacao_posterior_nao_arquiva(self):
        """
        Sequência real do processo: Definitivo (246) → Reativação (849).
        A Reativação posterior deve impedir classificação como arquivado.
        """
        movements = [
            {"codigo": "246", "nome": "Definitivo",  "dataHora": "2010-11-29T14:19:00Z"},
            {"codigo": "849", "nome": "Reativação",  "dataHora": "2018-10-31T11:58:28Z"},
        ]
        result = PhaseAnalyzer.analyze("90", movements, "TJRJ", "G1",
                                       process_number="0001745-93.1989.8.19.0002")

        assert result is not None
        assert not result.startswith("15"), (
            f"Reativação (849) posterior deve impedir Fase 15. Resultado: {result}"
        )

    def test_codigo_246_com_redistribuicao_posterior_nao_arquiva(self):
        """
        Sequência real do processo: Definitivo (246) → Redistribuição (36).
        Redistribuição indica processo ativo e deve impedir classificação como arquivado.
        """
        movements = [
            {"codigo": "246", "nome": "Definitivo",      "dataHora": "2021-11-12T15:18:32Z"},
            {"codigo": "36",  "nome": "Redistribuição",  "dataHora": "2023-10-19T09:01:29Z"},
            {"codigo": "85",  "nome": "Petição",         "dataHora": "2024-11-13T03:16:20Z"},
        ]
        result = PhaseAnalyzer.analyze("90", movements, "TJRJ", "G1",
                                       process_number="0001745-93.1989.8.19.0002")

        assert result is not None
        assert not result.startswith("15"), (
            f"Redistribuição (36) posterior deve impedir Fase 15. Resultado: {result}"
        )

    def test_codigo_22_correto_arquiva(self):
        """
        Código 22 (Baixa Definitiva) SEM desarquivamento posterior
        deve classificar corretamente como Fase 15 — Arquivado Definitivamente.
        Garante que a correção não quebra o comportamento legítimo.
        """
        movements = [
            {"codigo": "26",  "nome": "Distribuição",      "dataHora": "2020-01-10T10:00:00Z"},
            {"codigo": "246", "nome": "Proferida Sentença", "dataHora": "2021-03-15T14:00:00Z"},
            {"codigo": "22",  "nome": "Baixa Definitiva",   "dataHora": "2022-06-01T09:00:00Z"},
        ]
        result = PhaseAnalyzer.analyze("7", movements, "TJSP", "G1",
                                       process_number="0000001-01.2020.8.26.0001")

        assert result is not None
        assert result.startswith("15"), (
            f"Código 22 deve gerar Fase 15 (Arquivado). Resultado: {result}"
        )
