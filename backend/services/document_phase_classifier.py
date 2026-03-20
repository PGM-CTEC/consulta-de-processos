"""
DocumentPhaseClassifier — classifica fase processual a partir dos batismos
de peças do Fusion/PAV (tipoMovimentoLocal).

Usa lógica de âncoras em ordem cronológica decrescente.
Trânsito em Julgado: somente com documento explícito (certidão ou peça nomeada).
Sentença: somente para peças nomeadas exclusivamente como sentença.
'Despacho / Sentença / Decisão' é ignorado (nome genérico do DCP).
"""
import unicodedata
import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FusionMovimento:
    data: datetime
    tipo_local: str      # "batismo" — tipoMovimentoLocal
    tipo_cnj: str        # tipoMovimentoCNJ
    descricao: str = ""  # campo "descricao" da API — texto descritivo mais rico


@dataclass
class ClassificationResult:
    """Resultado estruturado da classificação de fase, com trace de decisão."""
    phase: str                                    # "01"–"15" ou "Indefinido"
    branch: str                                   # "conhecimento" | "execucao"
    classe_normalizada: str                       # classe processual normalizada
    total_movimentos: int                         # total de movimentos analisados
    rule_applied: str                             # regra que disparou (ex: "P2_transito_em_julgado")
    decisive_movement: Optional[str] = None       # tipo_local do movimento decisivo
    decisive_movement_date: Optional[str] = None  # ISO date do movimento decisivo
    anchor_matches: dict = field(default_factory=dict)
    # anchor_matches: posição na lista DESC de cada âncora, ou None
    confidence: Optional[float] = None            # 0.0–1.0, None = não calculado
    context_summary: dict = field(default_factory=dict)
    # context_summary: resumo do conjunto completo de movimentos

    def to_dict(self) -> dict:
        """Retorna dict serializável para JSON."""
        return {
            "phase": self.phase,
            "branch": self.branch,
            "classe_normalizada": self.classe_normalizada,
            "total_movimentos": self.total_movimentos,
            "rule_applied": self.rule_applied,
            "decisive_movement": self.decisive_movement,
            "decisive_movement_date": self.decisive_movement_date,
            "anchor_matches": self.anchor_matches,
            "confidence": self.confidence,
            "context_summary": self.context_summary,
        }


# ---------------------------------------------------------------------------
# Anchor patterns (after normalization)
# ---------------------------------------------------------------------------

# Fase 15 — Arquivado Definitivamente
_ANCHOR_ARQUIVAMENTO = re.compile(r'(\barquivamento\b|baixa\s+definitiva)')

# Fase 03 — Trânsito em Julgado (somente documento explícito)
_ANCHOR_TRANSITO = re.compile(
    r'(certidao\s+de\s+transito\s+em\s+julgado|transito\s+em\s+julgado)'
)

# Fase 02 / 03 — Sentença pura (NÃO "despacho / sentenca / decisao")
# Aceita: "Sentença", "Sentença de Mérito", "Minutar Sentença", "Sentença Parcial", etc.
# Rejeita: "Despacho / Sentença / Decisão" (nome genérico do DCP)
_ANCHOR_SENTENCA = re.compile(
    r'^(minutar\s+)?sentenca(\s+(de\s+merito|homologatoria|parcial|condenatoria|declaratoria|constitutiva))?$'
)

# Desfechos de julgamento que indicam que sentença foi proferida, mesmo
# quando o documento não se chama "Sentença" — captura descrições do Fusion/PAV
# como "Procedência", "Julgado procedente o pedido", etc.
_ANCHOR_SENTENCA_RESULTADO = re.compile(
    r'(^procedencia$|^improcedencia$|'
    r'julg(ando|ou|ado|ada)\s+(im)?procedente|'
    r'parcialmente\s+procedente|'
    r'extincao\s+(do|de)\s+processo\s+com\s+resolucao|'
    r'homologacao\s+de?\s+(acordo|transacao)|'
    r'^sem\s+resolucao\s+de?\s+merito$)'
)

# Fase 04+ — Remessa explícita para instância SUPERIOR (tribunal, G2, STJ, etc.)
_ANCHOR_REMESSA_SUPERIOR = re.compile(
    r'(apelacao|agravo\s+de\s+instrumento|recurso\s+(especial|extraordinario|inominado|ordinario)|'
    r'remessa\s+necessaria|'
    r'remessa\s+(ao|para\s+o?)\s*(tribunal|tj|trf|stj|stf)|'
    r'->\s*(tj|trf|stj|stf))'
)

# Remessa lateral — transferências entre juízos de MESMA instância (intra-G1)
_ANCHOR_REMESSA_LATERAL = re.compile(
    r'(declinio\s+de\s+competencia|redistribuicao)'
)

# Remessa genérica — sinal ambíguo que precisa de contexto (bare word "remessa")
_ANCHOR_REMESSA_GENERICA = re.compile(r'\bremessa\b')

# Combinado para backward-compat em context_summary
_ANCHOR_REMESSA = re.compile(
    r'(remessa\b|declinio\s+de\s+competencia|redistribuicao|apelacao|'
    r'agravo\s+de\s+instrumento|recurso\s+(especial|extraordinario|inominado|ordinario))'
)

# Indicadores de atividade típica de 1ª instância APÓS uma remessa genérica
# Se presentes, a remessa genérica é tratada como lateral (intra-G1), não como recurso
_ANCHOR_ATIVIDADE_G1 = re.compile(
    r'(saneamento|audiencia\s+de\s+instrucao|'
    r'conclus(ao|os)\s+(para\s+)?(despacho|decisao|julgamento|sentenca)|'
    r'decisao\s+(de\s+saneamento|interlocutoria)|'
    r'despacho\s+de\s+(mero\s+expediente|citacao)|'
    r'julgamento|contestacao|replica|impugnacao)'
)

# Fase 05 — Acórdão / Certidão de Julgamento (julgado na 2ª instância, sem trânsito)
# "Certidão de julgamento" ≠ "Certidão de trânsito em julgado"
_ANCHOR_ACORDAO = re.compile(r'(acordao|certidao\s+de\s+julgamento)')

# Fase 13 — Suspenso/Sobrestado
_ANCHOR_SUSPENSO = re.compile(r'(suspensao|sobrestamento|processo\s+suspenso)')

# Reativação EXPLÍCITA — um único match já reverte o arquivamento.
_ANCHOR_REATIVACAO_EXPLICITA = re.compile(
    r'(desarquivamento|reativacao|reaber)'
)

# Atividade substancial posterior a um arquivamento — indica que o processo
# foi reaberto e NÃO está definitivamente arquivado.
_ANCHOR_REATIVACAO = re.compile(
    r'(desarquivamento|reaber|reativacao|redistribui|peticao\s+inicial|citacao|'
    r'despacho|decisao|audiencia|intimacao|mandado|diligencia|'
    r'cumpr\w+\s+sentenca|embargo|sentenca|acordao)'
)

# Fase 10 — Execução/Cumprimento posterior ao Trânsito em Julgado
# Detecta documentos de execução (nomeArquivo/tipo_local)
_ANCHOR_EXECUCAO = re.compile(
    r'(execucao|cumprimento\s+de\s+sentenca|penhora|hasta\s+publica|'
    r'leilao\s+judicial|expropriacao|arresto|bloqueio\s+de\s+valores|bacenjud|'
    r'calculo\s*[-–]\s*execucao)'
)

# Classes processuais que indicam execução (fases 10-12, 14)
_CLASSES_EXECUCAO = {
    "cumprimento de sentenca",
    "cumprimento provisorio de sentenca",
    "execucao fiscal",
    "execucao de titulo extrajudicial",
    "execucao",
    "execucao por quantia certa",
    "execucao de alimentos",
}


def _is_classe_execucao(classe_norm: str) -> bool:
    """
    Verifica se a classe processual normalizada indica execução.
    Usa set exato + fallback por prefixo para cobrir variantes como
    "execucao de titulo extrajudicial contra a fazenda publica".
    """
    if classe_norm in _CLASSES_EXECUCAO:
        return True
    return classe_norm.startswith("execucao") or classe_norm.startswith("cumprimento")


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class DocumentPhaseClassifier:
    """
    Classifica fase processual a partir de movimentos do Fusion/PAV.
    Stateless — todos os métodos são classmethod.
    """

    @classmethod
    def _has_g1_indicators_after(cls, nomes: List[str], remessa_idx: int) -> bool:
        """
        Verifica se há atos típicos de 1ª instância APÓS uma remessa genérica.

        Se existem, a remessa foi intra-G1 (lateral) e NÃO um recurso à 2ª instância.
        """
        if remessa_idx == 0:
            return False
        for i in range(remessa_idx):
            if _ANCHOR_ATIVIDADE_G1.search(nomes[i]):
                return True
        return False

    @classmethod
    def _has_substantive_posterior_activity(cls, nomes: List[str], anchor_idx: int) -> bool:
        """
        Verifica se há atividade substancial POSTERIOR à âncora encontrada.

        A lista ``nomes`` está em ordem DESC (idx 0 = mais recente).
        Movimentos em idx < anchor_idx são mais recentes que a âncora.

        Lógica em dois níveis:
        - Reativação EXPLÍCITA (desarquivamento, reativação, reabertura):
          um único match é suficiente para reverter o arquivamento.
        - Atividade IMPLÍCITA (despachos, petições, etc.):
          exige >5 ocorrências para reverter (threshold conservador).
        """
        if anchor_idx == 0:
            return False  # âncora é o mais recente → nada posterior

        implicit_count = 0
        for i in range(anchor_idx):
            if _ANCHOR_REATIVACAO_EXPLICITA.search(nomes[i]):
                return True  # reativação explícita: um basta
            if _ANCHOR_REATIVACAO.search(nomes[i]):
                implicit_count += 1
        return implicit_count > 5

    @classmethod
    def _build_context_summary(cls, ordered: List[FusionMovimento], nomes: List[str]) -> dict:
        """
        Constrói resumo contextual do conjunto completo de movimentos.
        Permite avaliar a confiança da classificação e identificar
        decisões baseadas em evidência fraca.
        """
        anchor_counts = {
            "arquivamento": sum(1 for n in nomes if _ANCHOR_ARQUIVAMENTO.search(n)),
            "transito": sum(1 for n in nomes if _ANCHOR_TRANSITO.search(n)),
            "sentenca": sum(1 for n in nomes if _ANCHOR_SENTENCA.match(n) or _ANCHOR_SENTENCA_RESULTADO.search(n)),
            "remessa": sum(1 for n in nomes if _ANCHOR_REMESSA.search(n)),
            "acordao": sum(1 for n in nomes if _ANCHOR_ACORDAO.search(n)),
            "suspenso": sum(1 for n in nomes if _ANCHOR_SUSPENSO.search(n)),
            "execucao": sum(1 for n in nomes if _ANCHOR_EXECUCAO.search(n)),
        }
        span_days = 0
        if len(ordered) >= 2:
            span_days = (ordered[0].data - ordered[-1].data).days

        return {
            "total": len(ordered),
            "span_days": span_days,
            "anchor_counts": anchor_counts,
        }

    @classmethod
    def _compute_confidence(cls, anchors: dict, context: dict, rule: str) -> float:
        """
        Calcula confiança da classificação baseado no contexto geral.

        - Âncora confirmada por outras âncoras coerentes → alta confiança
        - Âncora isolada sem contexto confirmatório → confiança reduzida
        - Fallback sem nenhuma âncora → confiança baixa
        """
        counts = context.get("anchor_counts", {})
        total = context.get("total", 0)
        rule_lower = rule.lower()

        # Fallback deve ser avaliado ANTES de checks por substring
        # pois o nome da regra pode conter "sentenca" (ex: P6_fallback_antes_sentenca)
        if "fallback" in rule_lower:
            if total > 15:
                return 0.40  # muitos movimentos sem âncora = baixa confiança
            return 0.60

        if "arquivamento" in rule_lower:
            if counts.get("transito", 0) > 0 and counts.get("sentenca", 0) > 0:
                return 0.95
            if counts.get("sentenca", 0) > 0:
                return 0.85
            return 0.70

        if "transito" in rule_lower:
            if counts.get("sentenca", 0) > 0:
                return 0.90
            return 0.75

        if "sentenca" in rule_lower:
            if total > 3:
                return 0.85
            return 0.70

        return 0.70

    @classmethod
    def classify(cls, movimentos: List[FusionMovimento], classe_processual: str) -> str:
        """
        Retorna código de fase (string "01"–"15").

        Args:
            movimentos: lista ordenada cronologicamente (ASC por data).
            classe_processual: classe do processo no tribunal.

        Returns:
            Fase processual como string de 2 dígitos.
        """
        return cls.classify_with_trace(movimentos, classe_processual).phase

    @classmethod
    def classify_with_trace(
        cls, movimentos: List[FusionMovimento], classe_processual: str
    ) -> ClassificationResult:
        """
        Classifica fase processual e retorna trace completo da decisão.

        Args:
            movimentos: lista ordenada cronologicamente (ASC por data).
            classe_processual: classe do processo no tribunal.

        Returns:
            ClassificationResult com fase, regra aplicada, movimento decisivo, etc.
        """
        classe_norm = cls._normalize(classe_processual)

        if _is_classe_execucao(classe_norm):
            return cls._classify_execucao_traced(movimentos, classe_norm)

        return cls._classify_conhecimento_traced(movimentos, classe_norm)

    # ------------------------------------------------------------------
    # Branch: conhecimento (fases 01–09, 13, 15)
    # ------------------------------------------------------------------

    @classmethod
    def _classify_conhecimento_traced(
        cls, movimentos: List[FusionMovimento], classe_norm: str
    ) -> ClassificationResult:
        if not movimentos:
            return ClassificationResult(
                phase="01", branch="conhecimento", classe_normalizada=classe_norm,
                total_movimentos=0, rule_applied="empty_list_fallback",
                anchor_matches={},
            )

        # Percorre do mais recente para o mais antigo
        ordered = sorted(movimentos, key=lambda m: m.data, reverse=True)
        nomes_triple = [
            (cls._normalize(m.tipo_local), cls._normalize(m.tipo_cnj), cls._normalize(m.descricao))
            for m in ordered
        ]
        # nomes: melhor texto disponível para _has_substantive e _build_context
        nomes = [local or cnj or desc for local, cnj, desc in nomes_triple]

        def _any_match(pattern, local: str, cnj: str, desc: str, use_match: bool = False) -> bool:
            """Verifica se o padrão bate em tipo_local, tipo_cnj OU descricao."""
            fn = pattern.match if use_match else pattern.search
            return bool(fn(local)) or bool(cnj and fn(cnj)) or bool(desc and fn(desc))

        # Escaneia todas as âncoras considerando os três campos
        arq_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_ARQUIVAMENTO, l, c, d)), None
        )
        transito_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_TRANSITO, l, c, d)), None
        )
        sentenca_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_SENTENCA, l, c, d, use_match=True)), None
        )
        # Desfecho de julgamento via descrição (Procedência, Improcedência, etc.)
        sentenca_resultado_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_SENTENCA_RESULTADO, l, c, d)), None
        )
        # Sentença efetiva: o mais recente entre sentença literal e resultado de julgamento
        if sentenca_idx is not None and sentenca_resultado_idx is not None:
            sentenca_idx = min(sentenca_idx, sentenca_resultado_idx)  # menor idx = mais recente em DESC
        elif sentenca_resultado_idx is not None:
            sentenca_idx = sentenca_resultado_idx
        # Remessa: sistema de 3 níveis
        remessa_superior_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_REMESSA_SUPERIOR, l, c, d)), None
        )
        remessa_lateral_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_REMESSA_LATERAL, l, c, d)), None
        )
        remessa_generica_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple)
             if _any_match(_ANCHOR_REMESSA_GENERICA, l, c, d)
             and not (remessa_superior_idx is not None and remessa_superior_idx == i)
             and not (remessa_lateral_idx is not None and remessa_lateral_idx == i)), None
        )

        acordao_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_ACORDAO, l, c, d)), None
        )

        # Resolver remessa_idx efetiva com contexto completo (incluindo acórdão)
        # Superior sempre conta; genérica conta se (a) há acórdão posterior, ou (b) não há G1 posterior
        if remessa_superior_idx is not None:
            remessa_idx = remessa_superior_idx
        elif remessa_generica_idx is not None:
            has_acordao_after = (acordao_idx is not None and acordao_idx < remessa_generica_idx)
            has_g1_after = cls._has_g1_indicators_after(nomes, remessa_generica_idx)
            if has_acordao_after or not has_g1_after:
                remessa_idx = remessa_generica_idx
            else:
                remessa_idx = None  # genérica com G1 posterior e sem acórdão → não é recurso
        else:
            remessa_idx = None  # lateral pura → não é recurso

        suspenso_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_SUSPENSO, l, c, d)), None
        )
        execucao_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_EXECUCAO, l, c, d)), None
        )

        anchors = {
            "arquivamento": arq_idx,
            "transito": transito_idx,
            "sentenca": sentenca_idx,
            "remessa": remessa_idx,
            "acordao": acordao_idx,
            "suspenso": suspenso_idx,
            "execucao": execucao_idx,
        }

        def _decisive(idx):
            """Retorna (melhor texto disponível, ISO date) do movimento na posição idx."""
            if idx is None:
                return None, None
            m = ordered[idx]
            return (m.tipo_local or m.tipo_cnj or m.descricao), m.data.isoformat()

        total = len(movimentos)
        context = cls._build_context_summary(ordered, nomes)

        # P1: Arquivamento — somente se NÃO há atividade substancial posterior
        if arq_idx is not None:
            if not cls._has_substantive_posterior_activity(nomes, arq_idx):
                rule = "P1_arquivamento"
                nome, data = _decisive(arq_idx)
                return ClassificationResult(
                    "15", "conhecimento", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            # Arquivamento invalidado por atividade posterior — continuar avaliação
            anchors["arquivamento_overridden"] = True
            logger.info(
                "Arquivamento ignorado: atividade substancial posterior detectada "
                f"(total_movimentos={total})"
            )

        # P0: Execução posterior ao Trânsito — fase 10
        # Lista está em ordem DESC (idx 0 = mais recente)
        # Se execucao_idx < transito_idx, o documento de execução é POSTERIOR ao trânsito
        if execucao_idx is not None and transito_idx is not None and execucao_idx < transito_idx:
            rule = "P0_execucao_posterior_transito"
            nome, data = _decisive(execucao_idx)
            return ClassificationResult(
                "10", "execucao", classe_norm, total,
                rule, nome, data, anchors,
                0.70, context,
            )

        # P2: Trânsito em Julgado (explícito)
        if transito_idx is not None:
            rule = "P2_transito_em_julgado"
            nome, data = _decisive(transito_idx)
            return ClassificationResult(
                "03", "conhecimento", classe_norm, total,
                rule, nome, data, anchors,
                cls._compute_confidence(anchors, context, rule), context,
            )

        # P3: Sentença
        if sentenca_idx is not None:
            # Se há remessa mais recente que a sentença (índice menor = mais recente),
            # o processo foi remetido à instância superior após a sentença → fase 04
            if remessa_idx is not None and remessa_idx < sentenca_idx:
                # P3a: Se há acórdão mais recente que a remessa → julgado na 2ª instância → fase 05
                if acordao_idx is not None and acordao_idx < remessa_idx:
                    rule = "P3a_acordao_apos_remessa"
                    nome, data = _decisive(acordao_idx)
                    return ClassificationResult(
                        "05", "conhecimento", classe_norm, total,
                        rule, nome, data, anchors,
                        cls._compute_confidence(anchors, context, rule), context,
                    )
                rule = "P3_sentenca_com_remessa_posterior"
                nome, data = _decisive(remessa_idx)
                return ClassificationResult(
                    "04", "conhecimento", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            # Sentença sem remessa posterior nem trânsito → fase 02
            rule = "P3_sentenca_sem_transito"
            nome, data = _decisive(sentenca_idx)
            return ClassificationResult(
                "02", "conhecimento", classe_norm, total,
                rule, nome, data, anchors,
                cls._compute_confidence(anchors, context, rule), context,
            )

        # P4: Remessa sem sentença prévia
        if remessa_idx is not None:
            # P4a: Se há acórdão mais recente que a remessa → julgado na 2ª instância → fase 05
            if acordao_idx is not None and acordao_idx < remessa_idx:
                rule = "P4a_acordao_apos_remessa"
                nome, data = _decisive(acordao_idx)
                return ClassificationResult(
                    "05", "conhecimento", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            rule = "P4_remessa_sem_sentenca"
            nome, data = _decisive(remessa_idx)
            return ClassificationResult(
                "04", "conhecimento", classe_norm, total,
                rule, nome, data, anchors,
                cls._compute_confidence(anchors, context, rule), context,
            )

        # P5: Suspensão — somente se NÃO há atividade substancial posterior
        if suspenso_idx is not None:
            if not cls._has_substantive_posterior_activity(nomes, suspenso_idx):
                rule = "P5_suspensao"
                nome, data = _decisive(suspenso_idx)
                return ClassificationResult(
                    "13", "conhecimento", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            # Suspensão invalidada por atividade posterior
            anchors["suspenso_overridden"] = True

        # Fallback conservador: antes da sentença
        rule = "P6_fallback_antes_sentenca"
        if total > 15:
            rule = "P6_fallback_antes_sentenca_ALERT"
        return ClassificationResult(
            "01", "conhecimento", classe_norm, total,
            rule, None, None, anchors,
            cls._compute_confidence(anchors, context, rule), context,
        )

    # ------------------------------------------------------------------
    # Branch: execução (fases 10–12, 14, 15)
    # ------------------------------------------------------------------

    @classmethod
    def _classify_execucao_traced(
        cls, movimentos: List[FusionMovimento], classe_norm: str
    ) -> ClassificationResult:
        if not movimentos:
            return ClassificationResult(
                phase="10", branch="execucao", classe_normalizada=classe_norm,
                total_movimentos=0, rule_applied="empty_list_fallback",
                anchor_matches={},
            )

        ordered = sorted(movimentos, key=lambda m: m.data, reverse=True)
        nomes_triple = [
            (cls._normalize(m.tipo_local), cls._normalize(m.tipo_cnj), cls._normalize(m.descricao))
            for m in ordered
        ]
        nomes = [local or cnj or desc for local, cnj, desc in nomes_triple]

        def _any_match(pattern, local: str, cnj: str, desc: str, use_match: bool = False) -> bool:
            """Verifica se o padrão bate em tipo_local, tipo_cnj OU descricao."""
            fn = pattern.match if use_match else pattern.search
            return bool(fn(local)) or bool(cnj and fn(cnj)) or bool(desc and fn(desc))

        arq_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_ARQUIVAMENTO, l, c, d)), None
        )
        suspenso_idx = next(
            (i for i, (l, c, d) in enumerate(nomes_triple) if _any_match(_ANCHOR_SUSPENSO, l, c, d)), None
        )

        anchors = {
            "arquivamento": arq_idx,
            "suspenso": suspenso_idx,
        }

        def _decisive(idx):
            if idx is None:
                return None, None
            m = ordered[idx]
            return (m.tipo_local or m.tipo_cnj or m.descricao), m.data.isoformat()

        total = len(movimentos)
        context = cls._build_context_summary(ordered, nomes)

        # E1: Arquivamento — somente se NÃO há atividade substancial posterior
        if arq_idx is not None:
            if not cls._has_substantive_posterior_activity(nomes, arq_idx):
                rule = "E1_arquivamento"
                nome, data = _decisive(arq_idx)
                return ClassificationResult(
                    "15", "execucao", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            anchors["arquivamento_overridden"] = True
            logger.info(
                "Arquivamento (execução) ignorado: atividade substancial posterior "
                f"(total_movimentos={total})"
            )

        # E2: Suspensão de execução — somente se NÃO há atividade substancial posterior
        if suspenso_idx is not None:
            if not cls._has_substantive_posterior_activity(nomes, suspenso_idx):
                rule = "E2_suspensao"
                nome, data = _decisive(suspenso_idx)
                return ClassificationResult(
                    "11", "execucao", classe_norm, total,
                    rule, nome, data, anchors,
                    cls._compute_confidence(anchors, context, rule), context,
                )
            anchors["suspenso_overridden"] = True

        # Fallback: execução em andamento
        rule = "E3_fallback"
        return ClassificationResult(
            "10", "execucao", classe_norm, total,
            rule, None, None, anchors,
            cls._compute_confidence(anchors, context, rule), context,
        )

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    @classmethod
    def _normalize(cls, texto: str) -> str:
        """Remove acentos, converte para minúsculas, normaliza espaços."""
        if not texto:
            return ""
        # Remove acentos via NFD decomposition
        nfkd = unicodedata.normalize("NFKD", texto)
        ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
        # Lowercase, strip, normalizar espaços múltiplos
        return re.sub(r'\s+', ' ', ascii_text.lower().strip())
