"""
Testes para detecção de Acórdão/Certidão de Julgamento no DocumentPhaseClassifier.

Valida que documentos de acórdão posteriores à remessa disparam Fase 05
(Conhecimento — Recurso 2ª Instância — Julgado sem Trânsito em Julgado).
"""

import pytest
from datetime import datetime, timezone

from backend.services.document_phase_classifier import (
    FusionMovimento,
    DocumentPhaseClassifier,
)


def _mov(tipo_local: str, data_str: str, tipo_cnj: str = "52") -> FusionMovimento:
    """Helper: criar FusionMovimento."""
    dt = datetime.strptime(data_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return FusionMovimento(data=dt, tipo_local=tipo_local, tipo_cnj=tipo_cnj)


class TestAcordaoAposRemessa:
    """Fase 05: Acórdão posterior à remessa → julgado na 2ª instância sem trânsito."""

    def test_remessa_seguida_de_acordao_retorna_fase_05(self):
        """Remessa + Acórdão posterior → Fase 05, regra P4a."""
        movs = [
            _mov("Distribuição", "2022-01-01"),
            _mov("Sentença", "2022-06-01"),
            _mov("Remessa", "2022-08-01"),
            _mov("Acórdão", "2023-03-15"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "05", f"Expected phase 05, got {resultado.phase}"
        assert resultado.rule_applied == "P3a_acordao_apos_remessa"

    def test_remessa_sem_acordao_retorna_fase_04(self):
        """Remessa sem Acórdão posterior → Fase 04 (regressão)."""
        movs = [
            _mov("Distribuição", "2022-01-01"),
            _mov("Sentença", "2022-06-01"),
            _mov("Remessa", "2022-08-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "04", f"Expected phase 04, got {resultado.phase}"
        assert resultado.rule_applied == "P3_sentenca_com_remessa_posterior"

    def test_certidao_de_julgamento_posterior_a_remessa_retorna_fase_05(self):
        """'Certidão de julgamento' posterior à remessa → Fase 05."""
        movs = [
            _mov("Distribuição", "2022-01-01"),
            _mov("Remessa", "2022-08-01"),
            _mov("Certidão de Julgamento", "2023-04-10"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "05", f"Expected phase 05, got {resultado.phase}"
        assert resultado.rule_applied == "P4a_acordao_apos_remessa"

    def test_remessa_sem_sentenca_com_acordao_retorna_fase_05(self):
        """Remessa sem sentença + Acórdão posterior → Fase 05 via P4a."""
        movs = [
            _mov("Distribuição", "2022-01-01"),
            _mov("Remessa", "2022-08-01"),
            _mov("Acórdão", "2023-05-20"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "05", f"Expected phase 05, got {resultado.phase}"
        assert resultado.rule_applied == "P4a_acordao_apos_remessa"

    def test_acordao_sem_remessa_previa_nao_retorna_fase_05(self):
        """Acórdão presente mas sem remessa prévia → não deve retornar Fase 05."""
        movs = [
            _mov("Distribuição", "2022-01-01"),
            _mov("Acórdão", "2023-05-20"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase != "05", f"Phase 05 should not be returned without remessa"

    def test_acordao_anterior_a_remessa_nao_retorna_fase_05(self):
        """Acórdão ANTERIOR à remessa (não posterior) → Fase 04, não 05."""
        movs = [
            _mov("Distribuição", "2022-01-01"),
            _mov("Acórdão", "2022-05-01"),   # acórdão antes da remessa
            _mov("Remessa", "2022-09-01"),   # remessa mais recente
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "04", f"Expected phase 04, got {resultado.phase}"

    def test_acordao_com_transito_posterior_retorna_fase_03(self):
        """Acórdão + Trânsito em Julgado posterior → Fase 03 (P2 tem prioridade)."""
        movs = [
            _mov("Distribuição", "2022-01-01"),
            _mov("Remessa", "2022-08-01"),
            _mov("Acórdão", "2023-03-15"),
            _mov("Certidão de Trânsito em Julgado", "2023-06-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "03", f"Expected phase 03 (transito takes priority), got {resultado.phase}"
        assert resultado.rule_applied == "P2_transito_em_julgado"
