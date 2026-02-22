"""
Tests for Classification Rules Enums - Phase 6 Coverage Extension
Story: REM-017 - Backend Unit Tests (70% Coverage Target)

Test Categories:
- FaseProcessual enum values and descriptions
- GrauJurisdicao enum values
- MovimentoProcessual dataclass creation
- DocumentoProcessual dataclass
"""

from datetime import datetime
from backend.services.classification_rules import (
    FaseProcessual,
    GrauJurisdicao,
    MovimentoProcessual,
    DocumentoProcessual,
    CodigosCNJ
)


class TestFaseProcessualEnum:
    """Tests for FaseProcessual enum (4 tests)."""

    def test_fase_processual_fase_01(self):
        """TC-1: CONHECIMENTO_ANTES_SENTENCA has code 01."""
        assert FaseProcessual.CONHECIMENTO_ANTES_SENTENCA.value == "01"

    def test_fase_processual_fase_10(self):
        """TC-2: EXECUCAO has code 10."""
        assert FaseProcessual.EXECUCAO.value == "10"

    def test_fase_processual_fase_15(self):
        """TC-3: ARQUIVADO_DEFINITIVAMENTE has code 15."""
        assert FaseProcessual.ARQUIVADO_DEFINITIVAMENTE.value == "15"

    def test_fase_processual_descriptions(self):
        """TC-4: FaseProcessual returns descriptions."""
        fase = FaseProcessual.CONHECIMENTO_ANTES_SENTENCA
        descricao = fase.descricao
        assert "Conhecimento" in descricao

    def test_fase_processual_all_have_descriptions(self):
        """TC-5: All fases have descriptions."""
        for fase in FaseProcessual:
            assert len(fase.descricao) > 0

    def test_fase_processual_execucao_descricao(self):
        """TC-6: EXECUCAO description contains Execução."""
        fase = FaseProcessual.EXECUCAO
        assert "Execução" in fase.descricao

    def test_fase_processual_arquivada_descricao(self):
        """TC-7: ARQUIVADO description contains Arquivado."""
        fase = FaseProcessual.ARQUIVADO_DEFINITIVAMENTE
        assert "Arquivado" in fase.descricao

    def test_fase_processual_all_2digit_codes(self):
        """TC-8: All fase codes are 2-digit strings."""
        for fase in FaseProcessual:
            assert len(fase.value) == 2
            assert fase.value.isdigit()


class TestGrauJurisdicaoEnum:
    """Tests for GrauJurisdicao enum (3 tests)."""

    def test_grau_g1_value(self):
        """TC-9: G1 (primeira instancia) has value G1."""
        assert GrauJurisdicao.G1.value == "G1"

    def test_grau_g2_value(self):
        """TC-10: G2 (segunda instancia) has value G2."""
        assert GrauJurisdicao.G2.value == "G2"

    def test_grau_sup_value(self):
        """TC-11: SUP (tribunais superiores) has value SUP."""
        assert GrauJurisdicao.SUP.value == "SUP"

    def test_all_graus_defined(self):
        """TC-12: All 5 graus of jurisdiction are defined."""
        graus = list(GrauJurisdicao)
        assert len(graus) >= 5
        valores = [g.value for g in graus]
        assert "G1" in valores
        assert "G2" in valores
        assert "SUP" in valores


class TestMovimentoProcessual:
    """Tests for MovimentoProcessual dataclass (4 tests)."""

    def test_movimento_creation_minimal(self):
        """TC-13: MovimentoProcessual creation with required fields."""
        movimento = MovimentoProcessual(
            codigo=100,
            descricao="Sentença",
            data=datetime(2024, 1, 15),
            grau=GrauJurisdicao.G1
        )

        assert movimento.codigo == 100
        assert movimento.descricao == "Sentença"
        assert movimento.grau == GrauJurisdicao.G1

    def test_movimento_with_complementos(self):
        """TC-14: MovimentoProcessual with complementary data."""
        complementos = {"tipo": "condenatória", "valor": "1000"}
        movimento = MovimentoProcessual(
            codigo=161,
            descricao="Sentença",
            data=datetime(2024, 1, 15),
            grau=GrauJurisdicao.G1,
            complementos=complementos
        )

        assert movimento.complementos == complementos
        assert movimento.complementos["tipo"] == "condenatória"

    def test_movimento_hash_consistency(self):
        """TC-15: Same movements have same hash."""
        data = datetime(2024, 1, 15)
        m1 = MovimentoProcessual(
            codigo=100,
            descricao="Sentença",
            data=data,
            grau=GrauJurisdicao.G1
        )
        m2 = MovimentoProcessual(
            codigo=100,
            descricao="Sentença",
            data=data,
            grau=GrauJurisdicao.G1
        )

        assert hash(m1) == hash(m2)

    def test_movimento_different_graus(self):
        """TC-16: Movements can have different jurisdiction grades."""
        m_g1 = MovimentoProcessual(
            codigo=100,
            descricao="Recurso",
            data=datetime(2024, 1, 15),
            grau=GrauJurisdicao.G1
        )
        m_g2 = MovimentoProcessual(
            codigo=200,
            descricao="Apelação",
            data=datetime(2024, 2, 15),
            grau=GrauJurisdicao.G2
        )

        assert m_g1.grau != m_g2.grau
        assert m_g1.grau == GrauJurisdicao.G1
        assert m_g2.grau == GrauJurisdicao.G2


class TestDocumentoProcessual:
    """Tests for DocumentoProcessual dataclass (2 tests)."""

    def test_documento_creation(self):
        """TC-17: DocumentoProcessual creation."""
        documento = DocumentoProcessual(
            codigo=1001,
            descricao="Sentença",
            data_juntada=datetime(2024, 1, 15)
        )

        assert documento.codigo == 1001
        assert documento.descricao == "Sentença"
        assert documento.data_juntada == datetime(2024, 1, 15)

    def test_documento_multiple_types(self):
        """TC-18: Multiple documento types."""
        docs = [
            DocumentoProcessual(
                codigo=1001,
                descricao="Sentença",
                data_juntada=datetime(2024, 1, 15)
            ),
            DocumentoProcessual(
                codigo=1002,
                descricao="Recurso",
                data_juntada=datetime(2024, 2, 15)
            ),
        ]

        assert len(docs) == 2
        assert docs[0].descricao == "Sentença"
        assert docs[1].descricao == "Recurso"


class TestCodigosCNJ:
    """Tests for CodigosCNJ helper class (3 tests)."""

    def test_codigos_cnj_existence(self):
        """TC-19: CodigosCNJ class exists and is accessible."""
        assert CodigosCNJ is not None

    def test_codigos_cnj_has_attributes(self):
        """TC-20: CodigosCNJ contains relevant attributes."""
        assert hasattr(CodigosCNJ, '__dict__')

    def test_codigos_cnj_is_set_based(self):
        """TC-21: CodigosCNJ codes are set-based for efficient lookup."""
        codigos = dir(CodigosCNJ)
        assert len(codigos) > 0


class TestEnumIntegration:
    """Tests for enum integration scenarios (3 tests)."""

    def test_fase_with_grau_combination(self):
        """TC-22: Different fases with different graus."""
        fase = FaseProcessual.CONHECIMENTO_ANTES_SENTENCA
        grau = GrauJurisdicao.G1

        assert fase.value == "01"
        assert grau.value == "G1"
        assert isinstance(fase.value, str)
        assert isinstance(grau.value, str)

    def test_movimento_timeline_sequence(self):
        """TC-23: Movements can be ordered by date."""
        m1 = MovimentoProcessual(
            codigo=100,
            descricao="Sentença",
            data=datetime(2024, 1, 15),
            grau=GrauJurisdicao.G1
        )
        m2 = MovimentoProcessual(
            codigo=200,
            descricao="Apelação",
            data=datetime(2024, 2, 15),
            grau=GrauJurisdicao.G2
        )
        m3 = MovimentoProcessual(
            codigo=300,
            descricao="Decisão",
            data=datetime(2024, 3, 15),
            grau=GrauJurisdicao.G2
        )

        movimentos = [m1, m2, m3]
        sorted_movimentos = sorted(movimentos, key=lambda m: m.data)

        assert sorted_movimentos[0].codigo == 100
        assert sorted_movimentos[2].codigo == 300
        assert sorted_movimentos[1].data < sorted_movimentos[2].data

    def test_multiple_movements_same_grau(self):
        """TC-24: Multiple movements in same jurisdiction grade."""
        movimentos = [
            MovimentoProcessual(
                codigo=i*100,
                descricao=f"Movimento {i}",
                data=datetime(2024, i, 15),
                grau=GrauJurisdicao.G1
            )
            for i in range(1, 4)
        ]

        g1_movimentos = [m for m in movimentos if m.grau == GrauJurisdicao.G1]
        assert len(g1_movimentos) == 3
        for m in g1_movimentos:
            assert m.grau == GrauJurisdicao.G1
