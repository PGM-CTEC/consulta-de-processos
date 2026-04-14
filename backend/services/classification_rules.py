"""
Classificador de Fases Processuais - PGM-Rio
=============================================
Algoritmo de pré-filtragem baseado em regras determinísticas para classificação
de fases processuais a partir de dados do MNI/CNJ.

Este módulo realiza a classificação inicial que será posteriormente validada
por um agente de IA/LLM.

Autor: Coordenação de Tecnologia - PGM-Rio
Versão: 1.0 (Ported)
Data: Fevereiro/2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime
import json
import logging
import unicodedata

from services.hierarchical_classification import (
    Stage, Substage, Transit, HierarchicalResult,
    derive_legacy_phase, detect_transit_from_class,
    PHASE_TO_STAGE_SUBSTAGE,
)

logger = logging.getLogger(__name__)


def _normalizar_texto(texto: str) -> str:
    """Remove acentos, lowercase, normaliza espaços."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_text.lower().split())


# Padrões textuais em descrições de movimentos que indicam fase de execução.
# Pré-normalizados (sem acentos, lowercase) para comparação eficiente.
_PADROES_DESCRICAO_EXECUCAO_RAW = [
    "execução",
    "cumprimento de sentença",
    "penhora",
    "hasta pública",
    "leilão judicial",
    "expropriação",
    "arresto",
    "bloqueio de valores",
    "bacenjud",
]
_PADROES_DESCRICAO_EXECUCAO = [_normalizar_texto(p) for p in _PADROES_DESCRICAO_EXECUCAO_RAW]

class FaseProcessual(Enum):
    """Enumeração das 15 fases processuais definidas."""
    
    CONHECIMENTO_ANTES_SENTENCA = "01"
    CONHECIMENTO_SENTENCA_SEM_TRANSITO = "02"
    CONHECIMENTO_SENTENCA_COM_TRANSITO = "03"
    CONHECIMENTO_RECURSO_2INST_PENDENTE = "04"
    CONHECIMENTO_RECURSO_2INST_JULGADO_SEM_TRANSITO = "05"
    CONHECIMENTO_RECURSO_2INST_TRANSITADO = "06"
    CONHECIMENTO_RECURSO_SUP_PENDENTE = "07"
    CONHECIMENTO_RECURSO_SUP_JULGADO_SEM_TRANSITO = "08"
    CONHECIMENTO_RECURSO_SUP_TRANSITADO = "09"
    EXECUCAO = "10"
    EXECUCAO_SUSPENSA = "11"
    EXECUCAO_SUSPENSA_PARCIAL = "12"
    SUSPENSO_SOBRESTADO = "13"
    CONVERSAO_EM_RENDA = "14"
    ARQUIVADO_DEFINITIVAMENTE = "15"
    
    @property
    def descricao(self) -> str:
        descricoes = {
            "01": "Conhecimento - Antes da Sentença",
            "02": "Conhecimento - Sentença sem Trânsito em Julgado",
            "03": "Conhecimento - Sentença com Trânsito em Julgado",
            "04": "Conhecimento - Recurso 2ª Instância - Pendente Julgamento",
            "05": "Conhecimento - Recurso 2ª Instância - Julgado sem Trânsito",
            "06": "Conhecimento - Recurso 2ª Instância - Transitado em Julgado",
            "07": "Conhecimento - Recurso Tribunais Superiores - Pendente Julgamento",
            "08": "Conhecimento - Recurso Tribunais Superiores - Julgado sem Trânsito",
            "09": "Conhecimento - Recurso Tribunais Superiores - Transitado em Julgado",
            "10": "Execução",
            "11": "Execução Suspensa",
            "12": "Execução Suspensa Parcialmente",
            "13": "Suspenso / Sobrestado",
            "14": "Conversão em Renda",
            "15": "Arquivado Definitivamente",
        }
        return descricoes.get(self.value, "Fase Desconhecida")


class GrauJurisdicao(Enum):
    """Graus de jurisdição."""
    G1 = "G1"      # 1ª Instância
    G2 = "G2"      # 2ª Instância (TJ, TRF)
    SUP = "SUP"    # Tribunais Superiores (STJ, STF, TST)
    TR = "TR"      # Turma Recursal (Juizados)
    JE = "JE"      # Juizado Especial


@dataclass
class MovimentoProcessual:
    """Representa um movimento processual do CNJ."""
    codigo: int
    descricao: str
    data: datetime
    grau: GrauJurisdicao
    complementos: Dict[str, str] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.codigo, self.data))


@dataclass
class DocumentoProcessual:
    """Representa um documento processual do CNJ."""
    codigo: int
    descricao: str
    data_juntada: datetime


@dataclass
class ProcessoJudicial:
    """Representa um processo judicial com seus dados do MNI."""
    numero: str
    classe_codigo: int
    classe_descricao: str
    grau_atual: GrauJurisdicao
    situacao: str  # MOVIMENTO, BAIXADO, SUSPENSO, etc.
    movimentos: List[MovimentoProcessual] = field(default_factory=list)
    documentos: List[DocumentoProcessual] = field(default_factory=list)
    polo_fazenda: str = "RE"  # "AU" = Autora, "RE" = Ré
    
    @property
    def ultimo_movimento(self) -> Optional[MovimentoProcessual]:
        """Retorna o movimento mais recente."""
        if not self.movimentos:
            return None
        return max(self.movimentos, key=lambda m: m.data)
    
    def tem_movimento(self, codigos: Set[int]) -> bool:
        """Verifica se existe algum movimento com os códigos especificados."""
        return any(m.codigo in codigos for m in self.movimentos)
    
    def tem_movimento_sem_posterior(self, codigo_inicial: Set[int], codigo_cancelamento: Set[int]) -> bool:
        """
        Verifica se existe movimento inicial sem movimento de cancelamento posterior.
        Útil para sobrestamentos onde precisa verificar se houve levantamento.
        """
        movimentos_iniciais = [m for m in self.movimentos if m.codigo in codigo_inicial]
        if not movimentos_iniciais:
            return False
        
        ultimo_inicial = max(movimentos_iniciais, key=lambda m: m.data)
        movimentos_cancelamento = [m for m in self.movimentos 
                                   if m.codigo in codigo_cancelamento and m.data > ultimo_inicial.data]
        
        return len(movimentos_cancelamento) == 0
    
    def get_movimentos_por_grau(self, grau: GrauJurisdicao) -> List[MovimentoProcessual]:
        """Retorna movimentos de um grau específico."""
        return [m for m in self.movimentos if m.grau == grau]
    
    def ultimo_grau_tramitacao(self) -> GrauJurisdicao:
        """Identifica o último grau onde houve tramitação relevante."""
        if not self.movimentos:
            return self.grau_atual
        
        # Ordena por data e pega o grau do último movimento relevante
        movimentos_ordenados = sorted(self.movimentos, key=lambda m: m.data, reverse=True)
        return movimentos_ordenados[0].grau


@dataclass
class ResultadoClassificacao:
    """Resultado da classificação com contexto para o LLM."""
    fase: FaseProcessual
    confianca: float  # 0.0 a 1.0
    regras_aplicadas: List[str]
    movimentos_determinantes: List[MovimentoProcessual]
    alertas: List[str]
    contexto_llm: Dict

    # Classificação hierárquica (3 campos)
    stage: int = 1
    substage: Optional[str] = None
    transit_julgado: str = "nao"

    def to_dict(self) -> Dict:
        """Converte para dicionário para serialização."""
        return {
            "fase_codigo": self.fase.value,
            "fase_descricao": self.fase.descricao,
            "confianca": self.confianca,
            "regras_aplicadas": self.regras_aplicadas,
            "movimentos_determinantes": [
                {"codigo": m.codigo, "descricao": m.descricao, "data": m.data.isoformat()}
                for m in self.movimentos_determinantes
            ],
            "alertas": self.alertas,
            "contexto_llm": self.contexto_llm,
            "stage": self.stage,
            "substage": self.substage,
            "transit_julgado": self.transit_julgado,
        }

    def to_json(self) -> str:
        """Serializa para JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_hierarchical(self) -> HierarchicalResult:
        """Converte para resultado hierárquico."""
        return HierarchicalResult(
            stage=self.stage,
            substage=self.substage,
            transit_julgado=self.transit_julgado,
            phase_legacy=self.fase.value,
            rules_applied=self.regras_aplicadas,
            confidence=self.confianca,
        )


class CodigosCNJ:
    """Centraliza os códigos de movimentos e classes do CNJ."""
    
    # === MOVIMENTOS DE JULGAMENTO (Hierarquia 193) ===
    TRANSITO_JULGADO = 848
    PROFERIDA_SENTENCA = 246
    PROFERIDO_ACORDAO = 50
    BAIXA_DEFINITIVA = 22
    
    # Julgamentos com resolução de mérito
    JULGAMENTO_PROCEDENTE = 198
    JULGAMENTO_IMPROCEDENTE = 200
    JULGAMENTO_PROCEDENTE_PARTE = 220
    JULGAMENTO_SEM_RESOLUCAO_MERITO = 219
    HOMOLOGACAO_ACORDO = 235
    HOMOLOGACAO_TRANSACAO = 236
    
    MOVIMENTOS_SENTENCA = {246, 198, 200, 219, 220, 235, 236}
    MOVIMENTOS_ACORDAO = {50, 198, 200, 219, 220}  # Em G2/SUP
    MOVIMENTOS_JULGAMENTO = {246, 50, 198, 200, 219, 220, 235, 236}
    
    # === MOVIMENTOS DE REMESSA ===
    REMETIDOS_AUTOS = 970
    REMESSA_TRIBUNAL = 22881
    RECEBIDO_TRIBUNAL = 132
    DISTRIBUIDO = 26
    RETORNO_AUTOS = 60303
    
    MOVIMENTOS_REMESSA_SUPERIOR = {970, 22881}
    
    # === MOVIMENTOS DE SOBRESTAMENTO/SUSPENSÃO ===
    SUSPENSO_REPERCUSSAO_GERAL = 265
    SUSPENSO_PREJUDICIALIDADE = 893
    SUSPENSO_DECISAO_JUDICIAL = 898
    SOBRESTADO_RECURSO_REPETITIVO_STJ = 12099
    SUSPENSO_IRDR = 12100
    SOBRESTADO_IAC = 12155
    SOBRESTADO_GRUPO_REPRESENTATIVOS = 12224
    
    MOVIMENTOS_SOBRESTAMENTO = {265, 893, 898, 12099, 12100, 12155, 12224}
    
    # Movimentos de levantamento de sobrestamento
    LEVANTAMENTO_SOBRESTAMENTO = {12107, 12108, 12109, 12153, 12154, 12156, 12225}
    
    # === MOVIMENTOS DE EXECUÇÃO ===
    EMBARGOS_RECEBIDOS_EFEITO_SUSPENSIVO = 11372
    CITACAO_REALIZADA = 123
    PENHORA_REALIZADA = 176
    
    # === CLASSES PROCESSUAIS ===
    # Classes de Conhecimento
    CLASSES_CONHECIMENTO = {
        7,      # Procedimento Comum Cível
        65,     # Ação Civil Pública
        120,    # Mandado de Segurança Cível
        1707,   # Procedimento do Juizado Especial Cível
        175,    # Ação Popular
        26,     # Ação Anulatória
        1310,   # Ação de Improbidade Administrativa
        63,     # Ação Rescisória
        119,    # Mandado de Injunção
        116,    # Habeas Data
        36,     # Ação Declaratória
        64,     # Ação de Obrigação de Fazer/Não Fazer
        # Adicionar outras conforme necessidade
    }
    
    # Classes de Execução
    CLASSES_EXECUCAO = {
        1116,   # Execução Fiscal
        156,    # Cumprimento de Sentença
        12078,  # Cumprimento de Sentença contra Fazenda Pública
        159,    # Execução de Título Extrajudicial
        229,    # Execução de Alimentos
        1727,   # Cumprimento de Sentença (Juizado)
        165,    # Execução Contra a Fazenda Pública
        90,     # Desapropriação — execução do pagamento da diferença entre depósito e valor devido
        # Adicionar outras conforme necessidade
    }
    
    # === MOVIMENTOS DE REATIVAÇÃO/DESARQUIVAMENTO ===
    # Sincronizado com phase_analyzer.py: CODIGOS_REATIVACAO
    CODIGOS_REATIVACAO = {900, 12617, 849, 36}

    # === DOCUMENTOS ===
    DOC_SENTENCA = 80
    DOC_ACORDAO = 81
    DOC_CONTESTACAO = 50
    DOC_APELACAO = 7
    DOC_RECURSO_ESPECIAL = 67
    DOC_RECURSO_EXTRAORDINARIO = 66
    DOC_EMBARGOS_EXECUCAO = 56
    DOC_IMPUGNACAO_CUMPRIMENTO = 59


class ClassificadorFases:
    """
    Classificador de fases processuais baseado em regras determinísticas.

    Implementa o algoritmo de classificação que analisa classe processual,
    movimentos e documentos para determinar a fase atual do processo.
    """

    def __init__(self):
        self.codigos = CodigosCNJ()

    def classificar(self, processo: ProcessoJudicial) -> ResultadoClassificacao:
        """
        Classifica o processo em uma das 15 fases definidas.

        Aplica as regras por código em ordem de prioridade, depois aplica
        override por descrição textual de movimentos quando pertinente.
        Após, computa os campos hierárquicos (stage, substage, transit_julgado).
        """
        resultado = self._classificar_por_codigos(processo)
        resultado = self._aplicar_override_por_descricao(processo, resultado)
        self._computar_hierarquia(processo, resultado)
        return resultado

    def _computar_hierarquia(self, processo: ProcessoJudicial, resultado: ResultadoClassificacao):
        """Computa stage, substage e transit_julgado a partir da fase classificada."""
        fase_code = resultado.fase.value
        stage, substage = PHASE_TO_STAGE_SUBSTAGE.get(fase_code, (Stage.CONHECIMENTO, Substage.ANTES_SENTENCA))
        resultado.stage = stage
        resultado.substage = substage

        # Decisão 3: Transit em julgado (independente do stage)
        # T0: Classe é execução originária → na
        transit_from_class = detect_transit_from_class(
            processo.classe_codigo, processo.classe_descricao
        )
        if transit_from_class is not None:
            resultado.transit_julgado = transit_from_class
        elif self._verificar_transito_julgado(processo):
            resultado.transit_julgado = Transit.SIM
        else:
            resultado.transit_julgado = Transit.NAO

    def _classificar_por_codigos(self, processo: ProcessoJudicial) -> ResultadoClassificacao:
        """
        Classificação primária baseada em códigos numéricos CNJ.

        Regras em ordem de prioridade:
        1. Baixa Definitiva (Fase 15)
        2. Sobrestamento (Fase 13)
        3. Execução (Fases 10-14)
        4. Conhecimento por instância (Fases 01-09)
        """
        regras_aplicadas = []
        alertas = []
        movimentos_determinantes = []
        
        # === PRIORIDADE 1: Verificar Baixa Definitiva ===
        if self._verificar_baixa_definitiva(processo):
            mov_baixa = self._get_movimento(processo, {CodigosCNJ.BAIXA_DEFINITIVA})
            if mov_baixa:
                movimentos_determinantes.append(mov_baixa)
            
            regras_aplicadas.append("REGRA_BAIXA: Movimento 22 (Baixa Definitiva) presente OU situação = BAIXADO")
            
            return self._criar_resultado(
                fase=FaseProcessual.ARQUIVADO_DEFINITIVAMENTE,
                confianca=0.95,
                regras=regras_aplicadas,
                movimentos=movimentos_determinantes,
                alertas=alertas,
                processo=processo
            )
        
        # === PRIORIDADE 2: Verificar Sobrestamento/Suspensão ===
        if self._verificar_sobrestamento_ativo(processo):
            mov_sobr = self._get_ultimo_movimento_conjunto(processo, CodigosCNJ.MOVIMENTOS_SOBRESTAMENTO)
            if mov_sobr:
                movimentos_determinantes.append(mov_sobr)
            
            regras_aplicadas.append(f"REGRA_SOBRESTAMENTO: Movimento de sobrestamento ativo sem levantamento posterior")
            
            # Verificar se é execução suspensa ou sobrestamento geral
            if self._eh_classe_execucao(processo):
                # Verificar se suspensão é total ou parcial
                if self._verificar_suspensao_parcial(processo):
                    regras_aplicadas.append("REGRA_EXEC_SUSP_PARCIAL: Impugnação/Embargos parciais identificados")
                    return self._criar_resultado(
                        fase=FaseProcessual.EXECUCAO_SUSPENSA_PARCIAL,
                        confianca=0.75,
                        regras=regras_aplicadas,
                        movimentos=movimentos_determinantes,
                        alertas=["Verificar complementos para confirmar parcialidade"],
                        processo=processo
                    )
                else:
                    regras_aplicadas.append("REGRA_EXEC_SUSP: Execução com suspensão total")
                    return self._criar_resultado(
                        fase=FaseProcessual.EXECUCAO_SUSPENSA,
                        confianca=0.85,
                        regras=regras_aplicadas,
                        movimentos=movimentos_determinantes,
                        alertas=alertas,
                        processo=processo
                    )
            else:
                # Processo de conhecimento sobrestado
                return self._criar_resultado(
                    fase=FaseProcessual.SUSPENSO_SOBRESTADO,
                    confianca=0.90,
                    regras=regras_aplicadas,
                    movimentos=movimentos_determinantes,
                    alertas=alertas,
                    processo=processo
                )
        
        # === PRIORIDADE 3: Verificar se é Execução ===
        if self._eh_classe_execucao(processo):
            return self._classificar_fase_execucao(processo, regras_aplicadas, alertas)
        
        # === PRIORIDADE 4: Conhecimento - Classificar por Instância ===
        return self._classificar_fase_conhecimento(processo, regras_aplicadas, alertas)
    
    # ==================== MÉTODOS DE VERIFICAÇÃO ====================
    
    def _verificar_baixa_definitiva(self, processo: ProcessoJudicial) -> bool:
        """
        Verifica se processo está baixado definitivamente.

        Considera movimentos de reativação/desarquivamento posteriores à baixa.
        Se há reativação após a última baixa, o processo NÃO está arquivado.
        """
        # Verificar código 22 (Baixa Definitiva) sem reativação posterior
        if processo.tem_movimento_sem_posterior(
            {CodigosCNJ.BAIXA_DEFINITIVA},
            CodigosCNJ.CODIGOS_REATIVACAO
        ):
            return True

        # Verificar situação "BAIXADO"/"ARQUIVADO" com validação cruzada
        if processo.situacao and processo.situacao.upper() in ["BAIXADO", "ARQUIVADO"]:
            # Se não há nenhum movimento de reativação, confiar na situação
            if not processo.tem_movimento(CodigosCNJ.CODIGOS_REATIVACAO):
                return True
            # Há reativação — verificar se a última baixa é posterior
            return processo.tem_movimento_sem_posterior(
                {CodigosCNJ.BAIXA_DEFINITIVA},
                CodigosCNJ.CODIGOS_REATIVACAO
            )

        return False
    
    def _verificar_sobrestamento_ativo(self, processo: ProcessoJudicial) -> bool:
        """Verifica se há sobrestamento ativo (sem levantamento posterior)."""
        return processo.tem_movimento_sem_posterior(
            CodigosCNJ.MOVIMENTOS_SOBRESTAMENTO,
            CodigosCNJ.LEVANTAMENTO_SOBRESTAMENTO
        )
    
    def _verificar_suspensao_parcial(self, processo: ProcessoJudicial) -> bool:
        """
        Verifica se a suspensão é parcial (impugnação de parte do crédito).
        Análise heurística baseada em complementos.
        """
        for mov in processo.movimentos:
            if mov.codigo in CodigosCNJ.MOVIMENTOS_SOBRESTAMENTO:
                complementos = mov.complementos
                # Verificar se complemento indica parcialidade
                if "parcial" in str(complementos).lower():
                    return True
        return False
    
    def _eh_classe_execucao(self, processo: ProcessoJudicial) -> bool:
        """
        Verifica se a classe processual é de execução.
        Usa código CNJ + fallback por descrição para cobrir variantes como
        'Execução de Título Extrajudicial contra a Fazenda Pública'.
        """
        if processo.classe_codigo in CodigosCNJ.CLASSES_EXECUCAO:
            return True
        # Fallback por descrição normalizada
        if processo.classe_descricao:
            desc_norm = _normalizar_texto(processo.classe_descricao)
            if desc_norm.startswith("execucao") or desc_norm.startswith("cumprimento"):
                return True
        return False
    
    def _verificar_transito_julgado(self, processo: ProcessoJudicial) -> bool:
        """
        Verifica se há trânsito em julgado.
        Considera:
        1. Movimento explícito de Trânsito em Julgado (848)
        2. Baixa das instâncias superiores (60303 - Retorno dos Autos)
        3. Menção textual a certidão/trânsito na movimentação
        """
        if processo.tem_movimento({CodigosCNJ.TRANSITO_JULGADO}):
            return True
            
        # Verificar baixa de instâncias superiores (Retorno de Autos)
        if processo.tem_movimento({CodigosCNJ.RETORNO_AUTOS}):
            return True
            
        # Buscar por menção textual expressa na movimentação
        termos_transito = ["trânsito em julgado", "transitou em julgado", "certidão de trânsito"]
        for mov in processo.movimentos:
            texto_mov = f"{mov.descricao} {mov.complementos}".lower()
            if any(termo in texto_mov for termo in termos_transito):
                return True
                
        return False
    
    def _verificar_sentenca(self, processo: ProcessoJudicial, grau: GrauJurisdicao = None) -> bool:
        """Verifica se há sentença proferida (opcionalmente em grau específico)."""
        movimentos = processo.movimentos
        if grau:
            movimentos = processo.get_movimentos_por_grau(grau)
        return any(m.codigo in CodigosCNJ.MOVIMENTOS_SENTENCA for m in movimentos)
    
    def _verificar_acordao(self, processo: ProcessoJudicial, grau: GrauJurisdicao = None) -> bool:
        """Verifica se há acórdão proferido (opcionalmente em grau específico)."""
        movimentos = processo.movimentos
        if grau:
            movimentos = processo.get_movimentos_por_grau(grau)
        return any(m.codigo == CodigosCNJ.PROFERIDO_ACORDAO for m in movimentos)
    
    def _verificar_remessa_tribunal(self, processo: ProcessoJudicial) -> bool:
        """Verifica se houve remessa ao tribunal superior."""
        return processo.tem_movimento(CodigosCNJ.MOVIMENTOS_REMESSA_SUPERIOR)
    
    def _verificar_conversao_renda(self, processo: ProcessoJudicial) -> bool:
        """
        Verifica se houve conversão em renda de depósito judicial.
        Análise heurística - requer validação por LLM.
        """
        # Verificar se Fazenda é autora E há indicação de depósito/conversão
        if processo.polo_fazenda != "AU":
            return False
        
        # Buscar por movimentos ou documentos relacionados a depósito/alvará
        palavras_chave = ["conversão", "renda", "depósito", "alvará", "levantamento"]
        for mov in processo.movimentos:
            desc_lower = mov.descricao.lower()
            if any(p in desc_lower for p in palavras_chave):
                return True
        
        return False
    
    # ==================== MÉTODOS DE CLASSIFICAÇÃO ====================
    
    def _classificar_fase_execucao(
        self, 
        processo: ProcessoJudicial,
        regras_aplicadas: List[str],
        alertas: List[str]
    ) -> ResultadoClassificacao:
        """Classifica processo de execução nas fases 10-14."""
        
        movimentos_determinantes = []
        
        # Verificar conversão em renda (Fase 14)
        if self._verificar_conversao_renda(processo):
            regras_aplicadas.append("REGRA_CONVERSAO: Fazenda autora com indicação de conversão em renda")
            alertas.append("Conversão em renda identificada por heurística - requer validação LLM")
            
            return self._criar_resultado(
                fase=FaseProcessual.CONVERSAO_EM_RENDA,
                confianca=0.60,  # Baixa confiança, precisa validação
                regras=regras_aplicadas,
                movimentos=movimentos_determinantes,
                alertas=alertas,
                processo=processo
            )
        
        # Execução em tramitação normal (Fase 10)
        regras_aplicadas.append("REGRA_EXECUCAO: Classe de execução sem suspensão")
        
        return self._criar_resultado(
            fase=FaseProcessual.EXECUCAO,
            confianca=0.85,
            regras=regras_aplicadas,
            movimentos=movimentos_determinantes,
            alertas=alertas,
            processo=processo
        )
    
    def _classificar_fase_conhecimento(
        self,
        processo: ProcessoJudicial,
        regras_aplicadas: List[str],
        alertas: List[str]
    ) -> ResultadoClassificacao:
        """Classifica processo de conhecimento nas fases 01-09."""
        
        movimentos_determinantes = []
        grau_atual = processo.grau_atual
        ultimo_grau = processo.ultimo_grau_tramitacao()
        
        tem_transito = self._verificar_transito_julgado(processo)
        tem_sentenca_g1 = self._verificar_sentenca(processo, GrauJurisdicao.G1)
        tem_acordao_g2 = self._verificar_acordao(processo, GrauJurisdicao.G2)
        tem_remessa_tribunal = self._verificar_remessa_tribunal(processo)
        
        # Adicionar movimento de trânsito se existir
        if tem_transito:
            mov_transito = self._get_movimento(processo, {CodigosCNJ.TRANSITO_JULGADO})
            if mov_transito:
                movimentos_determinantes.append(mov_transito)
        
        # === TRIBUNAIS SUPERIORES (Fases 07, 08, 09) ===
        if ultimo_grau == GrauJurisdicao.SUP or grau_atual == GrauJurisdicao.SUP:
            tem_julgamento_sup = self._verificar_acordao(processo, GrauJurisdicao.SUP) or \
                                self._verificar_sentenca(processo, GrauJurisdicao.SUP)
            
            if tem_transito:
                regras_aplicadas.append("REGRA_SUP_TRANSITO: Último grau = SUP + Trânsito em Julgado")
                return self._criar_resultado(
                    fase=FaseProcessual.CONHECIMENTO_RECURSO_SUP_TRANSITADO,
                    confianca=0.90,
                    regras=regras_aplicadas,
                    movimentos=movimentos_determinantes,
                    alertas=alertas,
                    processo=processo
                )
            
            if tem_julgamento_sup:
                regras_aplicadas.append("REGRA_SUP_JULGADO: Grau = SUP + Julgamento proferido + Sem trânsito")
                mov_julg = self._get_ultimo_movimento_conjunto(processo, CodigosCNJ.MOVIMENTOS_JULGAMENTO)
                if mov_julg and mov_julg.grau == GrauJurisdicao.SUP:
                    movimentos_determinantes.append(mov_julg)
                
                return self._criar_resultado(
                    fase=FaseProcessual.CONHECIMENTO_RECURSO_SUP_JULGADO_SEM_TRANSITO,
                    confianca=0.85,
                    regras=regras_aplicadas,
                    movimentos=movimentos_determinantes,
                    alertas=alertas,
                    processo=processo
                )
            
            regras_aplicadas.append("REGRA_SUP_PENDENTE: Grau = SUP + Recurso distribuído + Sem julgamento")
            return self._criar_resultado(
                fase=FaseProcessual.CONHECIMENTO_RECURSO_SUP_PENDENTE,
                confianca=0.80,
                regras=regras_aplicadas,
                movimentos=movimentos_determinantes,
                alertas=alertas,
                processo=processo
            )
        
        # === 2ª INSTÂNCIA (Fases 04, 05, 06) ===
        if ultimo_grau == GrauJurisdicao.G2 or grau_atual == GrauJurisdicao.G2 or tem_remessa_tribunal:
            
            if tem_transito:
                regras_aplicadas.append("REGRA_G2_TRANSITO: Último grau = G2 + Trânsito em Julgado")
                return self._criar_resultado(
                    fase=FaseProcessual.CONHECIMENTO_RECURSO_2INST_TRANSITADO,
                    confianca=0.90,
                    regras=regras_aplicadas,
                    movimentos=movimentos_determinantes,
                    alertas=alertas,
                    processo=processo
                )
            
            if tem_acordao_g2:
                regras_aplicadas.append("REGRA_G2_JULGADO: Grau = G2 + Acórdão proferido + Sem trânsito")
                mov_acordao = self._get_movimento(processo, {CodigosCNJ.PROFERIDO_ACORDAO})
                if mov_acordao:
                    movimentos_determinantes.append(mov_acordao)
                
                return self._criar_resultado(
                    fase=FaseProcessual.CONHECIMENTO_RECURSO_2INST_JULGADO_SEM_TRANSITO,
                    confianca=0.85,
                    regras=regras_aplicadas,
                    movimentos=movimentos_determinantes,
                    alertas=alertas,
                    processo=processo
                )
            
            regras_aplicadas.append("REGRA_G2_PENDENTE: Remessa ao Tribunal + Sem acórdão")
            return self._criar_resultado(
                fase=FaseProcessual.CONHECIMENTO_RECURSO_2INST_PENDENTE,
                confianca=0.80,
                regras=regras_aplicadas,
                movimentos=movimentos_determinantes,
                alertas=alertas,
                processo=processo
            )
        
        # === 1ª INSTÂNCIA (Fases 01, 02, 03) ===
        if tem_transito:
            regras_aplicadas.append("REGRA_G1_TRANSITO: Grau = G1 + Sentença + Trânsito em Julgado")
            return self._criar_resultado(
                fase=FaseProcessual.CONHECIMENTO_SENTENCA_COM_TRANSITO,
                confianca=0.90,
                regras=regras_aplicadas,
                movimentos=movimentos_determinantes,
                alertas=alertas,
                processo=processo
            )
        
        if tem_sentenca_g1:
            regras_aplicadas.append("REGRA_G1_SENTENCA: Grau = G1 + Sentença proferida + Sem trânsito + Sem remessa")
            mov_sent = self._get_ultimo_movimento_conjunto(processo, CodigosCNJ.MOVIMENTOS_SENTENCA)
            if mov_sent:
                movimentos_determinantes.append(mov_sent)
            
            return self._criar_resultado(
                fase=FaseProcessual.CONHECIMENTO_SENTENCA_SEM_TRANSITO,
                confianca=0.85,
                regras=regras_aplicadas,
                movimentos=movimentos_determinantes,
                alertas=alertas,
                processo=processo
            )
        
        # Fase residual: antes da sentença
        regras_aplicadas.append("REGRA_G1_INICIAL: Grau = G1 + Sem sentença")
        return self._criar_resultado(
            fase=FaseProcessual.CONHECIMENTO_ANTES_SENTENCA,
            confianca=0.80,
            regras=regras_aplicadas,
            movimentos=movimentos_determinantes,
            alertas=alertas,
            processo=processo
        )
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _get_movimento(self, processo: ProcessoJudicial, codigos: Set[int]) -> Optional[MovimentoProcessual]:
        """Retorna o primeiro movimento encontrado com os códigos especificados."""
        for mov in processo.movimentos:
            if mov.codigo in codigos:
                return mov
        return None
    
    def _get_ultimo_movimento_conjunto(
        self, 
        processo: ProcessoJudicial, 
        codigos: Set[int]
    ) -> Optional[MovimentoProcessual]:
        """Retorna o movimento mais recente dentre os códigos especificados."""
        movimentos_filtrados = [m for m in processo.movimentos if m.codigo in codigos]
        if not movimentos_filtrados:
            return None
        return max(movimentos_filtrados, key=lambda m: m.data)
    
    def _criar_resultado(
        self,
        fase: FaseProcessual,
        confianca: float,
        regras: List[str],
        movimentos: List[MovimentoProcessual],
        alertas: List[str],
        processo: ProcessoJudicial
    ) -> ResultadoClassificacao:
        """Cria o resultado da classificação com contexto para o LLM."""
        
        contexto_llm = self._gerar_contexto_llm(processo, fase, confianca, regras, alertas)
        
        return ResultadoClassificacao(
            fase=fase,
            confianca=confianca,
            regras_aplicadas=regras,
            movimentos_determinantes=movimentos,
            alertas=alertas,
            contexto_llm=contexto_llm
        )
    
    def _gerar_contexto_llm(
        self,
        processo: ProcessoJudicial,
        fase: FaseProcessual,
        confianca: float,
        regras: List[str],
        alertas: List[str]
    ) -> Dict:
        """
        Gera contexto estruturado para validação por LLM.
        
        Este contexto será usado como entrada para um agente de IA
        que validará ou ajustará a classificação.
        """
        
        # Resumo dos últimos N movimentos
        ultimos_movimentos = sorted(processo.movimentos, key=lambda m: m.data, reverse=True)[:10]
        
        return {
            "processo": {
                "numero": processo.numero,
                "classe": {
                    "codigo": processo.classe_codigo,
                    "descricao": processo.classe_descricao,
                    "tipo": "EXECUÇÃO" if self._eh_classe_execucao(processo) else "CONHECIMENTO"
                },
                "grau_atual": processo.grau_atual.value,
                "situacao_sistema": processo.situacao,
                "polo_fazenda": "AUTORA" if processo.polo_fazenda == "AU" else "RÉ"
            },
            "classificacao_algoritmo": {
                "fase_codigo": fase.value,
                "fase_descricao": fase.descricao,
                "confianca": confianca,
                "regras_aplicadas": regras
            },
            "analise": {
                "tem_sentenca": self._verificar_sentenca(processo),
                "tem_acordao_g2": self._verificar_acordao(processo, GrauJurisdicao.G2),
                "tem_transito_julgado": self._verificar_transito_julgado(processo),
                "tem_remessa_tribunal": self._verificar_remessa_tribunal(processo),
                "tem_sobrestamento_ativo": self._verificar_sobrestamento_ativo(processo),
                "ultimo_grau_tramitacao": processo.ultimo_grau_tramitacao().value
            },
            "ultimos_movimentos": [
                {
                    "codigo": m.codigo,
                    "descricao": m.descricao,
                    "data": m.data.isoformat(),
                    "grau": m.grau.value
                }
                for m in ultimos_movimentos
            ],
            "alertas": alertas,
            "instrucao_validacao": self._gerar_instrucao_validacao(fase, confianca, alertas)
        }
    
    def _gerar_instrucao_validacao(
        self, 
        fase: FaseProcessual, 
        confianca: float,
        alertas: List[str]
    ) -> str:
        """Gera instrução para o LLM validador."""
        
        instrucao = f"""
TAREFA: Validar a classificação de fase processual realizada pelo algoritmo.

CLASSIFICAÇÃO PROPOSTA: {fase.value} - {fase.descricao}
CONFIANÇA DO ALGORITMO: {confianca:.0%}

INSTRUÇÕES:
1. Analise os movimentos processuais listados
2. Verifique se a fase proposta está correta considerando:
   - A sequência lógica dos movimentos
   - O grau de jurisdição atual
   - A existência de trânsito em julgado
   - Eventuais sobrestamentos ou suspensões
3. Se a classificação estiver correta, confirme
4. Se houver inconsistência, proponha a fase correta com justificativa

ALERTAS A VERIFICAR:
{chr(10).join(f'- {a}' for a in alertas) if alertas else '- Nenhum alerta específico'}

RESPONDA NO FORMATO:
{{
    "classificacao_validada": true/false,
    "fase_correta": "XX",
    "justificativa": "...",
    "observacoes": "..."
}}
"""
        return instrucao.strip()

    # ==================== OVERRIDE POR DESCRIÇÃO ====================

    _FASES_CONHECIMENTO = {"01", "02", "03", "04", "05", "06", "07", "08", "09"}

    def _aplicar_override_por_descricao(
        self,
        processo: ProcessoJudicial,
        resultado: ResultadoClassificacao,
    ) -> ResultadoClassificacao:
        """
        Pós-processamento: analisa descrições textuais dos movimentos para
        detectar transição de fase não capturada pelos códigos numéricos.

        Só atua quando:
        - A classificação por código resultou em fase de conhecimento (01-09)
        - Existem movimentos POSTERIORES ao movimento decisivo cuja descrição
          contém termos indicativos de fase de execução
        """
        if resultado.fase.value not in self._FASES_CONHECIMENTO:
            return resultado

        # Determinar limiar temporal: data do movimento decisivo mais recente
        data_limiar = None
        if resultado.movimentos_determinantes:
            data_limiar = max(m.data for m in resultado.movimentos_determinantes)

        # Buscar movimentos posteriores com descrição indicando execução
        movs_execucao = []
        for mov in processo.movimentos:
            if data_limiar and mov.data <= data_limiar:
                continue
            desc_norm = _normalizar_texto(mov.descricao)
            if any(padrao in desc_norm for padrao in _PADROES_DESCRICAO_EXECUCAO):
                movs_execucao.append(mov)

        if not movs_execucao:
            return resultado

        # Override: movimento mais recente como decisivo
        mov_decisivo = max(movs_execucao, key=lambda m: m.data)
        fase_original = resultado.fase

        resultado.alertas.append(
            f"OVERRIDE_DESCRICAO: Fase alterada de {fase_original.value} "
            f"({fase_original.descricao}) para 10 (Execução) — "
            f"movimento '{mov_decisivo.descricao}' em {mov_decisivo.data.isoformat()}"
        )
        resultado.regras_aplicadas.append(
            "REGRA_OVERRIDE_DESCRICAO: Descrição de movimento posterior indica fase de execução"
        )
        resultado.movimentos_determinantes.append(mov_decisivo)
        resultado.fase = FaseProcessual.EXECUCAO
        resultado.confianca = min(resultado.confianca, 0.70)

        logger.info(
            "Override por descrição para processo %s: %s -> 10, "
            "movimento decisivo: '%s' em %s",
            processo.numero, fase_original.value,
            mov_decisivo.descricao, mov_decisivo.data.isoformat(),
        )

        return resultado
