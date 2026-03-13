"""
Tests for classification_rules.py — _verificar_baixa_definitiva with reactivation.

Validates that code 22 (Baixa Definitiva) is properly invalidated when
posterior reactivation movements (900, 12617, 849, 36) exist.
"""
import pytest
from datetime import datetime, timezone

from backend.services.classification_rules import (
    ClassificadorFases,
    ProcessoJudicial,
    MovimentoProcessual,
    GrauJurisdicao,
    CodigosCNJ,
    FaseProcessual,
)


def _mov(codigo: int, data_str: str, grau=GrauJurisdicao.G1) -> MovimentoProcessual:
    """Helper: criar MovimentoProcessual a partir de código e data."""
    dt = datetime.strptime(data_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return MovimentoProcessual(
        codigo=codigo, descricao=f"Movimento {codigo}", data=dt, grau=grau
    )


def _processo(movimentos, situacao="MOVIMENTO", classe_codigo=7):
    """Helper: criar ProcessoJudicial com movimentos."""
    return ProcessoJudicial(
        numero="0000001-00.2024.8.19.0001",
        classe_codigo=classe_codigo,
        classe_descricao="Procedimento Comum Cível",
        grau_atual=GrauJurisdicao.G1,
        situacao=situacao,
        movimentos=movimentos,
        documentos=[],
        polo_fazenda="RE",
    )


class TestBaixaDefinitivaComReativacao:
    """_verificar_baixa_definitiva deve considerar reativação posterior."""

    def test_codigo_22_sem_reativacao_esta_baixado(self):
        """Código 22 sem reativação → processo está baixado (Fase 15)."""
        movs = [
            _mov(26, "2024-01-01"),    # Distribuído
            _mov(246, "2024-06-01"),   # Sentença
            _mov(22, "2024-09-01"),    # Baixa Definitiva
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))
        assert resultado.fase == FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_codigo_22_com_reativacao_900_nao_esta_baixado(self):
        """Código 22 seguido de reativação 900 → NÃO está baixado."""
        movs = [
            _mov(26, "2024-01-01"),    # Distribuído
            _mov(22, "2024-06-01"),    # Baixa Definitiva
            _mov(900, "2024-09-01"),   # Levantamento de Sobrestamento (reativação)
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))
        assert resultado.fase != FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_codigo_22_com_reativacao_849_nao_esta_baixado(self):
        """Código 22 seguido de reativação 849 → NÃO está baixado."""
        movs = [
            _mov(22, "2024-01-01"),    # Baixa Definitiva
            _mov(849, "2024-06-01"),   # Retorno de Autos (reativação)
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))
        assert resultado.fase != FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_codigo_22_com_reativacao_12617_nao_esta_baixado(self):
        """Código 22 seguido de reativação 12617 → NÃO está baixado."""
        movs = [
            _mov(22, "2024-01-01"),
            _mov(12617, "2024-06-01"),  # Reativação
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))
        assert resultado.fase != FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_codigo_22_com_reativacao_36_nao_esta_baixado(self):
        """Código 22 seguido de redistribuição 36 → NÃO está baixado."""
        movs = [
            _mov(22, "2024-01-01"),
            _mov(36, "2024-06-01"),    # Redistribuição (reativação)
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))
        assert resultado.fase != FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_situacao_baixado_com_reativacao_posterior(self):
        """situacao='BAIXADO' mas com reativação posterior → NÃO confiar."""
        movs = [
            _mov(22, "2024-01-01"),
            _mov(900, "2024-06-01"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs, situacao="BAIXADO"))
        assert resultado.fase != FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_situacao_baixado_sem_reativacao(self):
        """situacao='BAIXADO' sem movimentos de reativação → está baixado."""
        movs = [
            _mov(26, "2024-01-01"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs, situacao="BAIXADO"))
        assert resultado.fase == FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_ciclo_baixa_reativacao_baixa(self):
        """22 → 900 → 22 → resultado: BAIXADO (última baixa sem reativação)."""
        movs = [
            _mov(22, "2024-01-01"),    # Primeira baixa
            _mov(900, "2024-03-01"),   # Reativação
            _mov(22, "2024-09-01"),    # Segunda baixa (final)
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))
        assert resultado.fase == FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_reativacao_anterior_a_baixa_nao_invalida(self):
        """Reativação ANTES da baixa não invalida a baixa."""
        movs = [
            _mov(900, "2024-01-01"),   # Reativação (antes da baixa)
            _mov(22, "2024-06-01"),    # Baixa Definitiva (posterior)
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))
        assert resultado.fase == FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_sem_baixa_nem_situacao_nao_arquivado(self):
        """Sem código 22 e sem situação BAIXADO → NÃO arquivado."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(246, "2024-06-01"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))
        assert resultado.fase != FaseProcessual.ARQUIVADO_DEFINITIVAMENTE
