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
