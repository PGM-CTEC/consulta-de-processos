"""
Tests for description-based phase override in ClassificadorFases.

Validates that movement descriptions (e.g., "Execução / Cumprimento de sentença")
trigger a reclassification from knowledge phases (01-09) to execution (10) when
they appear AFTER the decisive movement of the code-based classification.
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


def _mov(codigo: int, data_str: str, grau=GrauJurisdicao.G1, descricao=None) -> MovimentoProcessual:
    """Helper: criar MovimentoProcessual com descrição opcional."""
    dt = datetime.strptime(data_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return MovimentoProcessual(
        codigo=codigo,
        descricao=descricao or f"Movimento {codigo}",
        data=dt,
        grau=grau,
    )


def _processo(movimentos, situacao="MOVIMENTO", classe_codigo=7) -> ProcessoJudicial:
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


class TestOverrideDescricaoBugReal:
    """Reprodução do bug real: processo 0807280-10.2025.8.19.0001."""

    def test_transito_com_execucao_posterior_vira_fase_10(self):
        """
        Processo com trânsito em julgado (fase 03) mas com movimentos posteriores
        descrevendo 'Execução / Cumprimento de sentença' deve ir para fase 10.
        """
        movs = [
            _mov(26, "2024-01-01"),                                          # Distribuído
            _mov(246, "2025-01-15"),                                         # Sentença
            _mov(848, "2025-06-01"),                                         # Trânsito em Julgado
            _mov(132, "2026-03-10", descricao="Execução / Cumprimento de sentença"),  # Posterior
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        assert resultado.fase == FaseProcessual.EXECUCAO
        assert any("OVERRIDE_DESCRICAO" in r for r in resultado.regras_aplicadas)
        assert any("OVERRIDE_DESCRICAO" in a for a in resultado.alertas)


class TestOverrideNaoAtua:
    """Cenários onde o override NÃO deve alterar a classificação."""

    def test_conhecimento_sem_descricao_execucao(self):
        """Processo de conhecimento puro sem descrições de execução — mantém fase original."""
        movs = [
            _mov(26, "2024-01-01"),    # Distribuído
            _mov(246, "2025-01-15"),    # Sentença
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        # Deve ser fase 02 (sentença sem trânsito) sem override
        assert resultado.fase == FaseProcessual.CONHECIMENTO_SENTENCA_SEM_TRANSITO
        assert not any("OVERRIDE_DESCRICAO" in r for r in resultado.regras_aplicadas)

    def test_processo_ja_classificado_execucao_por_classe(self):
        """Processo com classe de execução — já é fase 10, sem override."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(123, "2024-06-01", descricao="Citação na Execução"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs, classe_codigo=1116))  # Execução Fiscal

        assert resultado.fase == FaseProcessual.EXECUCAO
        # Não deve ter override — já era execução por classe
        assert not any("OVERRIDE_DESCRICAO" in r for r in resultado.regras_aplicadas)

    def test_processo_arquivado_ignora_descricao(self):
        """Processo arquivado (fase 15) não deve ser alterado por descrições."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(22, "2025-01-01"),                                          # Baixa Definitiva
            _mov(132, "2025-06-01", descricao="Execução / Cumprimento de sentença"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        assert resultado.fase == FaseProcessual.ARQUIVADO_DEFINITIVAMENTE

    def test_descricao_execucao_anterior_ao_transito_nao_dispara(self):
        """Descrição de execução ANTERIOR ao trânsito — sem override (filtro temporal)."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(132, "2024-06-01", descricao="Cumprimento de sentença"),  # ANTES do trânsito
            _mov(848, "2025-01-01"),                                        # Trânsito em Julgado
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        # Deve ser fase 03 (trânsito) — descrição anterior não dispara override
        assert resultado.fase == FaseProcessual.CONHECIMENTO_SENTENCA_COM_TRANSITO
        assert not any("OVERRIDE_DESCRICAO" in r for r in resultado.regras_aplicadas)


class TestOverrideTemporalPositivo:
    """Cenários onde o override DEVE atuar (temporal correto)."""

    def test_descricao_posterior_ao_transito_dispara(self):
        """Descrição de execução POSTERIOR ao trânsito → override para fase 10."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(848, "2025-01-01"),                                              # Trânsito
            _mov(132, "2026-03-10", descricao="Execução / Cumprimento de sentença"),  # Posterior
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        assert resultado.fase == FaseProcessual.EXECUCAO

    def test_multiplas_descricoes_usa_mais_recente(self):
        """Com múltiplas descrições de execução, usa a mais recente como decisivo."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(848, "2025-01-01"),
            _mov(132, "2026-01-01", descricao="Cumprimento de sentença"),
            _mov(176, "2026-03-15", descricao="Penhora realizada"),  # Mais recente
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        assert resultado.fase == FaseProcessual.EXECUCAO
        # O movimento decisivo mais recente deve estar no resultado
        movs_det = resultado.movimentos_determinantes
        mov_override = [m for m in movs_det if "Penhora" in m.descricao]
        assert len(mov_override) == 1

    def test_sentenca_sem_transito_com_execucao_posterior(self):
        """Fase 02 (sentença sem trânsito) + descrição execução posterior → fase 10."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(246, "2025-06-01"),                                           # Sentença
            _mov(132, "2026-03-10", descricao="Execução / Cumprimento de sentença"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        assert resultado.fase == FaseProcessual.EXECUCAO


class TestNormalizacaoTexto:
    """Verificar que acentos e case são normalizados corretamente."""

    def test_acento_e_maiusculas(self):
        """'Execução / Cumprimento de Sentença' com acentos e maiúsculas deve ser matchado."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(848, "2025-01-01"),
            _mov(132, "2026-03-10", descricao="EXECUÇÃO / Cumprimento de Sentença"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        assert resultado.fase == FaseProcessual.EXECUCAO

    def test_sem_acentos(self):
        """'execucao' sem acentos também deve ser matchado."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(848, "2025-01-01"),
            _mov(132, "2026-03-10", descricao="execucao iniciada"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        assert resultado.fase == FaseProcessual.EXECUCAO


class TestMetadados:
    """Verificar regras, alertas e confiança do override."""

    def test_regras_e_alertas_presentes(self):
        """Override deve adicionar regra e alerta específicos."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(848, "2025-01-01"),
            _mov(132, "2026-03-10", descricao="Cumprimento de sentença"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        assert any("REGRA_OVERRIDE_DESCRICAO" in r for r in resultado.regras_aplicadas)
        assert any("OVERRIDE_DESCRICAO" in a for a in resultado.alertas)

    def test_confianca_reduzida(self):
        """Confiança deve ser no máximo 0.70 após override."""
        movs = [
            _mov(26, "2024-01-01"),
            _mov(848, "2025-01-01"),
            _mov(132, "2026-03-10", descricao="Penhora realizada"),
        ]
        classificador = ClassificadorFases()
        resultado = classificador.classificar(_processo(movs))

        assert resultado.confianca <= 0.70
