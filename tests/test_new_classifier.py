import pytest
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.classification_rules import (
    ClassificadorFases, ProcessoJudicial, MovimentoProcessual, 
    GrauJurisdicao, FaseProcessual, CodigosCNJ
)

def test_classificacao_baixa_definitiva():
    processo = ProcessoJudicial(
        numero="0000000-00.0000.0.00.0000",
        classe_codigo=7,
        classe_descricao="Procedimento Comum",
        grau_atual=GrauJurisdicao.G1,
        situacao="MOVIMENTO",
        movimentos=[
            MovimentoProcessual(
                codigo=22,
                descricao="Baixa Definitiva",
                data=datetime.now(),
                grau=GrauJurisdicao.G1
            )
        ]
    )
    classificador = ClassificadorFases()
    resultado = classificador.classificar(processo)
    assert resultado.fase == FaseProcessual.ARQUIVADO_DEFINITIVAMENTE
    assert resultado.confianca >= 0.95

def test_classificacao_execucao_fiscal_inicial():
    processo = ProcessoJudicial(
        numero="1111111-11.1111.1.11.1111",
        classe_codigo=1116, # Execução Fiscal
        classe_descricao="Execução Fiscal",
        grau_atual=GrauJurisdicao.G1,
        situacao="MOVIMENTO",
        polo_fazenda="AU",
        movimentos=[
            MovimentoProcessual(
                codigo=26,
                descricao="Distribuído",
                data=datetime.now(),
                grau=GrauJurisdicao.G1
            )
        ]
    )
    classificador = ClassificadorFases()
    resultado = classificador.classificar(processo)
    assert resultado.fase == FaseProcessual.EXECUCAO
    assert "REGRA_EXECUCAO" in resultado.regras_aplicadas[0]

def test_classificacao_conhecimento_sentenca_sem_transito():
    processo = ProcessoJudicial(
        numero="2222222-22.2222.2.22.2222",
        classe_codigo=7, # Procedimento Comum
        classe_descricao="Procedimento Comum",
        grau_atual=GrauJurisdicao.G1,
        situacao="MOVIMENTO",
        movimentos=[
            MovimentoProcessual(
                codigo=246,
                descricao="Sentença Proferida",
                data=datetime.now(),
                grau=GrauJurisdicao.G1
            )
        ]
    )
    classificador = ClassificadorFases()
    resultado = classificador.classificar(processo)
    assert resultado.fase == FaseProcessual.CONHECIMENTO_SENTENCA_SEM_TRANSITO

def test_classificacao_conhecimento_transito_julgado():
    processo = ProcessoJudicial(
        numero="3333333-33.3333.3.33.3333",
        classe_codigo=7,
        classe_descricao="Procedimento Comum",
        grau_atual=GrauJurisdicao.G1,
        situacao="MOVIMENTO",
        movimentos=[
            MovimentoProcessual(
                codigo=246,
                descricao="Sentença",
                data=datetime(2023, 1, 1),
                grau=GrauJurisdicao.G1
            ),
            MovimentoProcessual(
                codigo=848,
                descricao="Trânsito em Julgado",
                data=datetime(2023, 2, 1),
                grau=GrauJurisdicao.G1
            )
        ]
    )
    classificador = ClassificadorFases()
    resultado = classificador.classificar(processo)
    assert resultado.fase == FaseProcessual.CONHECIMENTO_SENTENCA_COM_TRANSITO

if __name__ == "__main__":
    # Manually run tests if executed as script
    try:
        test_classificacao_baixa_definitiva()
        print("test_classificacao_baixa_definitiva: OK")
        test_classificacao_execucao_fiscal_inicial()
        print("test_classificacao_execucao_fiscal_inicial: OK")
        test_classificacao_conhecimento_sentenca_sem_transito()
        print("test_classificacao_conhecimento_sentenca_sem_transito: OK")
        test_classificacao_conhecimento_transito_julgado()
        print("test_classificacao_conhecimento_transito_julgado: OK")
        print("All manual tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
