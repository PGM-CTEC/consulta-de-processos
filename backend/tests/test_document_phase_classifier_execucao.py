"""
Testes para detecção de execução posterior ao trânsito no DocumentPhaseClassifier.

Valida que documentos com "Execução / Cumprimento de Sentença" posteriores ao trânsito
disparam a reclassificação de fases de conhecimento (01-09) para execução (10).
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


class TestExecutacaoPosteriorTransito:
    """Cenários onde o override de execução DEVE atuar."""

    def test_transito_com_execucao_posterior_vira_fase_10(self):
        """Trânsito + documento 'Execução / Cumprimento de Sentença' posterior → fase 10."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
            _mov("Execução / Cumprimento de Sentença", "2026-03-10"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "10", f"Expected phase 10, got {resultado.phase}"
        assert resultado.rule_applied == "P0_execucao_posterior_transito"
        assert resultado.confidence == 0.70

    def test_multiplos_documentos_execucao_usa_mais_recente(self):
        """Com múltiplos documentos de execução, usa o mais recente como decisivo."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
            _mov("Cumprimento de Sentença", "2026-01-01"),
            _mov("Cálculo - Execução", "2026-03-15"),  # Mais recente
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "10"
        assert "Cálculo - Execução" in resultado.decisive_movement

    def test_normalizacao_acentos_execucao(self):
        """'EXECUÇÃO / Cumprimento de Sentença' com acentos deve ser detectado."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
            _mov("EXECUÇÃO / Cumprimento de Sentença", "2026-03-10"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "10"

    def test_sem_acentos_execucao(self):
        """'execucao' sem acentos deve ser detectado."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
            _mov("execucao iniciada", "2026-03-10"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "10"


class TestExecutacaoNaoAtua:
    """Cenários onde o override de execução NÃO deve atuar."""

    def test_execucao_anterior_ao_transito_sem_override(self):
        """Execução ANTERIOR ao trânsito → sem override, retorna fase 03."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Cumprimento de Sentença", "2024-06-01"),  # ANTES do trânsito
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "03"
        assert resultado.rule_applied == "P2_transito_em_julgado"

    def test_transito_sem_documentos_execucao(self):
        """Trânsito puro sem documentos de execução → fase 03."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Sentença", "2025-01-15"),
            _mov("Certidão de Trânsito em Julgado", "2025-02-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "03"
        assert "P0_execucao" not in resultado.rule_applied

    def test_classe_execucao_ja_era_fase_10(self):
        """Processo com classe de execução já é fase 10 (não precisa override)."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Citação", "2024-06-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(
            movs, "Execução Fiscal"
        )

        assert resultado.phase == "10"
        assert "P0_execucao" not in resultado.rule_applied

    def test_execucao_sem_arquivamento_posterior(self):
        """Execução posterior ao trânsito SEM arquivamento posterior → fase 10."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
            _mov("Cumprimento de Sentença", "2026-01-01"),
            # Sem arquivamento posterior
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.phase == "10"  # Execução posterior ao trânsito


class TestContextoExecucao:
    """Validar rastreabilidade e metadados da execução."""

    def test_anchor_execucao_em_context_summary(self):
        """anchor_counts deve incluir contagem de documentos de execução."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
            _mov("Cumprimento de Sentença", "2026-01-01"),
            _mov("Penhora", "2026-02-01"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.context_summary["anchor_counts"]["execucao"] == 2

    def test_confianca_reduzida_no_override(self):
        """Confiança deve ser 0.70 quando há execução posterior ao trânsito."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
            _mov("Execução / Cumprimento de Sentença", "2026-03-10"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert resultado.confidence == 0.70

    def test_movimento_decisivo_eh_execucao(self):
        """Movimento decisivo deve ser o documento de execução, não o trânsito."""
        movs = [
            _mov("Distribuição", "2024-01-01"),
            _mov("Certidão de Trânsito em Julgado", "2025-01-15"),
            _mov("Cumprimento de Sentença", "2026-03-10"),
        ]
        resultado = DocumentPhaseClassifier.classify_with_trace(movs, "Ação Ordinária")

        assert "Cumprimento" in resultado.decisive_movement
        assert "2026-03-10" in resultado.decisive_movement_date
