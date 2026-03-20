from backend.services.phase_analyzer import PhaseAnalyzer


def test_fazenda_re_flow_current_contract():
    """Valida o contrato do analisador para classe 7 (procedimento comum).

    Código 246 (Proferida Sentença) avança para Fase 02, NÃO arquiva.
    Apenas código 22 (Baixa Definitiva) gera Fase 15.
    """
    movements = [{"codigo": 26, "nome": "Distribuído", "dataHora": "2024-01-01"}]
    assert PhaseAnalyzer.analyze(7, movements) == "01 Conhecimento - Antes da Sentença"

    movements.insert(0, {"codigo": 123, "nome": "Citação Realizada", "dataHora": "2024-01-15"})
    assert PhaseAnalyzer.analyze(7, movements) == "01 Conhecimento - Antes da Sentença"

    movements.insert(0, {"codigo": 12177, "nome": "Juntada de Contestação", "dataHora": "2024-02-01"})
    assert PhaseAnalyzer.analyze(7, movements) == "01 Conhecimento - Antes da Sentença"

    movements.insert(0, {"codigo": 25, "nome": "Despacho Saneador", "dataHora": "2024-03-01"})
    assert PhaseAnalyzer.analyze(7, movements) == "01 Conhecimento - Antes da Sentença"

    # Sentença proferida (246) → Fase 02, processo ainda NÃO está arquivado
    movements.insert(0, {"codigo": 246, "nome": "Sentença Proferida", "dataHora": "2024-06-01"})
    assert PhaseAnalyzer.analyze(7, movements) == "02 Conhecimento - Sentença sem Trânsito em Julgado"

    # Baixa Definitiva (22) → agora sim arquivado (Fase 15)
    movements.insert(0, {"codigo": 22, "nome": "Baixa Definitiva", "dataHora": "2024-08-01"})
    assert PhaseAnalyzer.analyze(7, movements) == "15 Arquivado Definitivamente"


def test_fazenda_autora_flow_current_contract():
    """Valida o contrato atual do analisador para classe 1116 (execução fiscal)."""
    movements = [{"codigo": 26, "nome": "Distribuído", "dataHora": "2024-01-01"}]
    assert PhaseAnalyzer.analyze(1116, movements) == "10 Execução"

    movements.insert(0, {"codigo": 123, "nome": "Citação Realizada", "dataHora": "2024-02-01"})
    assert PhaseAnalyzer.analyze(1116, movements) == "10 Execução"

    movements.insert(0, {"codigo": 0, "nome": "Penhora Realizada", "dataHora": "2024-03-01"})
    assert PhaseAnalyzer.analyze(1116, movements) == "10 Execução"

    movements.insert(0, {"codigo": 0, "nome": "Juntada de Embargos", "dataHora": "2024-04-01"})
    assert PhaseAnalyzer.analyze(1116, movements) == "10 Execução"


def test_instance_logic_consistency():
    """Garante consistência entre auto-detecção e grau explicitamente informado.

    Processo com sentença (246) + remessa ao tribunal (970) deve ser classificado
    na fase de recurso pendente em 2ª instância (Fase 04), não como arquivado.
    O Retorno dos Autos (60303) indica a baixa das instâncias superiores e trânsito.
    """
    movements = [
        {"codigo": 26, "nome": "Distribuído", "dataHora": "2024-01-01"},
        {"codigo": 246, "nome": "Sentença", "dataHora": "2024-06-01"},
        {"codigo": 970, "nome": "Remessa ao Tribunal", "dataHora": "2024-07-01"},
    ]

    auto_phase = PhaseAnalyzer.analyze(7, movements)
    g2_phase = PhaseAnalyzer.analyze(7, movements, grau="G2")
    # Ambas as formas devem concordar sobre a instância de tramitação
    assert auto_phase == g2_phase
    # Sentença + remessa = Recurso 2ª Instância Pendente (Fase 04), NÃO arquivado
    assert auto_phase == "04 Conhecimento - Recurso 2ª Instância - Pendente Julgamento"

    movements.insert(0, {"codigo": 60303, "nome": "Retorno dos Autos", "dataHora": "2024-12-01"})
    # Com a nova regra, Retorno dos Autos = trânsito em julgado
    assert PhaseAnalyzer.analyze(7, movements) == "06 Conhecimento - Recurso 2ª Instância - Transitado em Julgado"


def test_desapropriacao_fase_execucao():
    """Classe 90 (Desapropriação) deve ser classificada como Fase 10 Execução.

    Após julgamento (246) e reativação (849), a desapropriação entra na fase
    de execução: pagamento da diferença entre depósito inicial e valor devido.
    Baixa definitiva real (22) ainda arquiva o processo normalmente.
    """
    # Fluxo típico de desapropriação em execução
    movements = [
        {"codigo": 26,  "nome": "Distribuído",  "dataHora": "1989-01-06"},
        {"codigo": 246, "nome": "Definitivo",   "dataHora": "2007-09-06"},
        {"codigo": 849, "nome": "Reativação",   "dataHora": "2018-10-31"},
        {"codigo": 85,  "nome": "Petição",      "dataHora": "2026-01-30"},
    ]
    assert PhaseAnalyzer.analyze(90, movements) == "10 Execução"

    # Com apenas distribuição (início do processo) — ainda execução
    movements_inicio = [{"codigo": 26, "nome": "Distribuído", "dataHora": "2024-01-01"}]
    assert PhaseAnalyzer.analyze(90, movements_inicio) == "10 Execução"

    # Baixa Definitiva real (22) ainda arquiva corretamente
    movements_baixa = [
        {"codigo": 26, "nome": "Distribuído",      "dataHora": "2024-01-01"},
        {"codigo": 22, "nome": "Baixa Definitiva", "dataHora": "2024-08-01"},
    ]
    assert PhaseAnalyzer.analyze(90, movements_baixa) == "15 Arquivado Definitivamente"
