"""
rules.py — RE-01..RE-12 + pipeline R1-R7 + fronteiras F-01..F-13.

Implementação determinística das regras estruturantes normativas em
``fase-processual-doctree/references/regras.md`` e casos-fronteira em
``casos-fronteira.md``. Não consulta nenhuma fonte externa; opera apenas sobre
``DocumentPiece`` normalizados.

Saída das funções de classificação por domínio: dicionário parcial com
``fase_codigo``, ``confianca``, ``documentos_determinantes``, ``flags``,
``regra_determinante`` e ``raciocinio``. O classifier.py monta o output final
conforme o schema (output-schema.md), incluindo abstenção (RE-07).
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .normalizer import DocumentPiece, _normalize_text


# ============================================================
# Nomes das 15 fases (+ 16 e ERR)
# ============================================================

FASE_NOMES: Dict[str, str] = {
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
    "16": "Indeterminado — Revisão Humana",
    "ERR": "Erro Técnico",
}


# ============================================================
# Classes processuais executivas (RE-11)
# ============================================================

_EXEC_CLASS_PATTERNS = [
    "execucao fiscal",
    "execucao de titulo extrajudicial",
    "cumprimento de sentenca",
    "cumprimento provisor",
    "execucao contra fazenda publica",
    "execucao de sentenca",
    "execucao por quantia certa",
    "cumprimento provisório".lower().replace("ó", "o"),
]


def classe_e_executiva(classe_norm: Optional[str]) -> bool:
    """RE-11 — detecta classe processual executiva (texto normalizado, sem acentos)."""
    if not classe_norm:
        return False
    c = _normalize_text(classe_norm)
    return any(p in c for p in _EXEC_CLASS_PATTERNS)


# ============================================================
# Helpers sobre DocumentPiece
# ============================================================

def _is_determinante(p: DocumentPiece) -> bool:
    """Peça determinante: não-ruído e tipo reconhecido."""
    return (not p.is_noise) and (not p.tipo.startswith("ruido")) and p.tipo != "peticao_generica"


def _pieces_by_tipo_desc(pieces: List[DocumentPiece], tipo: str) -> List[DocumentPiece]:
    """Filtrar por tipo (substring), mais recente primeiro."""
    matches = [p for p in pieces if p.tipo == tipo or p.tipo.startswith(tipo)]
    matches.sort(key=lambda p: p.sort_key, reverse=True)
    return matches


def _latest_determinante(pieces: List[DocumentPiece]) -> Optional[DocumentPiece]:
    """R1 — peça determinante mais recente, ignorando ruído e despachos genéricos."""
    cands = [p for p in pieces if _is_determinante(p)]
    if not cands:
        # Fallback: peça não-ruído mesmo que tipo genérico (peticao_generica) — mas RE-12 diz
    # que só conta para fase_provavel, não para fase_codigo
        cands = [p for p in pieces if not p.is_noise]
    if not cands:
        return None
    return max(cands, key=lambda p: p.sort_key)


def _has_after(pieces: List[DocumentPiece], ref: DocumentPiece, pattern: str) -> bool:
    """Verifica se há peça DETERMINANTE posterior a ref que case pattern."""
    ref_ts, ref_ord = ref.sort_key
    for p in pieces:
        if p is ref or p.is_noise:
            continue
        p_ts, p_ord = p.sort_key
        if (p_ts, p_ord) > (ref_ts, ref_ord):
            if re.search(pattern, p.titulo) or re.search(pattern, p.nome_arquivo) or p.tipo.startswith(_match_short(pattern)):
                return True
    return False


def _match_short(pattern: str) -> str:
    # helper para _has_after: obter prefixo do pattern castiçal
    m = re.match(r"^\w+", pattern)
    return m.group(0) if m else pattern


def _count_teor_for_teor_keywords(teor: str, keywords: List[str]) -> bool:
    t = _normalize_text(teor)
    return any(k in t for k in keywords)


# ============================================================
# RE-05 — Trânsito em julgado exige certificação
# ============================================================

def _find_certidao_transito(pieces: List[DocumentPiece]) -> Optional[DocumentPiece]:
    """Certidão de trânsito mais recente. Resolve grau pelo contexto (taxonomia §1 nota)."""
    ct = _pieces_by_tipo_desc(pieces, "certidao_transito")
    if not ct:
        return None
    return ct[0]


def _grau_do_ultimo_julgado(pieces: List[DocumentPiece]) -> str:
    """Maior grau do último julgado antes da certidão de trânsito."""
    max_grau = "G1"
    last_grau_g2 = "G2"
    last_grau_sup = "SUP"
    for p in pieces:
        if p.is_noise:
            continue
        if p.tipo in ("sentenca",):
            if p.grau:
                max_grau = max(max_grau, p.grau, key=lambda g: _grau_rank(g))
        elif p.tipo == "acordao_g2":
            max_grau = max(max_grau, "G2", key=lambda g: _grau_rank(g))
        elif p.tipo == "acordao_sup":
            max_grau = max(max_grau, "SUP", key=lambda g: _grau_rank(g))
    return max_grau


def _grau_rank(g: str) -> int:
    return {"": 0, "G1": 1, "JE": 1, "G2": 2, "SUP": 3}.get(g, 0)


def _resolve_grau_certidao(cert: DocumentPiece, pieces: List[DocumentPiece]) -> str:
    if cert.grau:
        return cert.grau
    g = _grau_do_ultimo_julgado(pieces)
    return g


# ============================================================
# RE-06 — Polaridade financeira (taxonomia §5)
# ============================================================

POS_PATTERNS = [
    r"em favor do municipio|em favor da fazenda|favor do mrj|fazenda credora",
    r"conversao em renda|dam conversao|dam de conversao",
    r"comprovante de resgate.*mrj|comprovante.*resgate.*mrj",
    r"resgate mrj|resgate do mrj|satisfacao do credito fiscal",
]

NEG_PATTERNS = [
    r"precatorio|rpv",
    r"em favor do particular|em favor da parte",
    r"honorarios? da parte contraria",
    r"pagamento pelo municipio|deposito pagamento precatorio",
    r"contrario ao ente|contra o ente",
]


def _polaridade(p: DocumentPiece) -> str:
    """Retorna 'positiva', 'negativa' ou 'indeterminada'."""
    blob = _normalize_text(f"{p.titulo} {p.nome_arquivo} {p.teor}")
    if any(re.search(pat, blob) for pat in POS_PATTERNS):
        return "positiva"
    if any(re.search(pat, blob) for pat in NEG_PATTERNS):
        return "negativa"
    return "indeterminada"


# ============================================================
# R2 — Gate de domínio (RE-01 + RE-11)
# ============================================================

def classify_domain(
    pieces: List[DocumentPiece],
    classe_norm: Optional[str],
) -> Tuple[str, str, Optional[DocumentPiece]]:
    """
    R2: decide ``execucao`` ou ``conhecimento``.

    Retorna (dominio, regra, peca_inicial_executiva).
    """
    peca_inicial = next((p for p in pieces if p.tipo == "peticao_inicial"), None)

    # RE-11 — trava de classe executiva (unidirecional)
    if classe_e_executiva(classe_norm):
        return ("execucao", "RE-11", peca_inicial)

    # RE-01 — título extrajudicial identificado pelas peças
    init_titulo = _normalize_text(
        (peca_inicial.titulo + " " + peca_inicial.nome_arquivo) if peca_inicial else ""
    )
    if peca_inicial and (
        re.search(r"cda|certidao de divida ativa|execucao fiscal", init_titulo)
        or peca_inicial.tipo == "peticao_inicial"
        and re.search(r"execucao fiscal|execucao de titulo", init_titulo)
    ):
        return ("execucao", "RE-01", peca_inicial)

    # RE-01 — trânsito do mérito certificado → permite execução (cumprimento definitivo)
    cert = _find_certidao_transito(pieces)
    if cert:
        # Há atos satisfativos posteriores à certidão → execução
        atos_exec_posterior = False
        cert_ts = cert.sort_key
        for p in pieces:
            if p.is_noise or p is cert:
                continue
            if p.sort_key > cert_ts and p.tipo in (
                "inicio_cumprimento",
                "atos_constritivos",
                "conversao_renda",
                "destinacao_financeira",
            ):
                atos_exec_posterior = True
                break
        if atos_exec_posterior:
            return ("execucao", "RE-01", None)

    # Senão → conhecimento
    return ("conhecimento", "RE-01", None)


# ============================================================
# R3 — Domínio de Execução
# ============================================================

def classify_execution(
    pieces: List[DocumentPiece],
    classe_norm: Optional[str],
    perspectiva: str = "processual_arrecadatoria",
) -> Dict[str, Any]:
    """Aplica R3.1..R3.5 sobre a árvore (em ordem de precedência)."""
    determinantes: List[int] = []
    regras: List[str] = []
    flags: Dict[str, Any] = {}
    raciocinio: str = ""

    # Precedência: 14 > 15 (RE-03.1) — sob perspectiva padrão
    # R3.1 — arrecadação satisfativa ao ente credor → 14
    conv_docs = [p for p in pieces if p.tipo == "conversao_renda"]
    # sinal forte: "resgate mrj" / "dam conversao" / "comprovante de resgate mrj"
    polaridade_positiva = False
    for p in conv_docs:
        if _polaridade(p) == "positiva":
            polaridade_positiva = True
            determinantes.append(p.ordem)
            break
    if polaridade_positiva:
        # arrecadação parcial? se há atos constritivos posteriores OU execução em curso
        atos_posteriores = any(
            p.tipo in ("atos_constritivos", "inicio_cumprimento")
            and p.sort_key > max(conv_docs, key=lambda x: x.sort_key).sort_key
            for p in pieces
            if not p.is_noise
        )
        if atos_posteriores:
            flags["arrecadacao_parcial"] = True
            # arrecadação parcial com prosseguimento → 10
            fase, regra, rac = "10", "F-07", (
                "Arrecadação parcial ao ente credor identificada, com atos executivos "
                "posteriores: execução prossegue (10 + arrecadacao_parcial)."
            )
        else:
            # R3.1 + RE-06: satisfação integral → 14
            if perspectiva == "fase_processual_atual":
                # Sob perspectiva 'fase_processual_atual': se há arquivamento definitivo
                # posterior → 15, com marcador
                ext_docs = [p for p in pieces if p.tipo == "extincao_definitiva"]
                if ext_docs and max(ext_docs, key=lambda p: p.sort_key).sort_key > \
                        max(conv_docs, key=lambda x: x.sort_key).sort_key:
                    return _build_result(
                        "15", 0.85, [p.ordem for p in ext_docs],
                        flags={"houve_conversao_em_renda": True},
                        regra="R3.2 + RE-06 (fase_processual_atual)",
                        raciocinio="Conversão em renda seguida de extinção definitiva; sob "
                                   "perspectiva fase_processual_atual prevalece 15.",
                    )
            # padrão: 14 > 15
            fase, regra, rac = "14", "R3.1 / RE-06", (
                "Satisfação com arrecadação ao ente credor (polaridade positiva) "
                "comprovada por peça de conversão em renda."
            )
        flags.setdefault("houve_conversao_em_renda", True)
        return _build_result(fase, 0.88, determinantes, flags, regra, rac)

    # R3.2 — extinção definitiva sem arrecadação → 15
    ext_docs = [p for p in pieces if p.tipo == "extincao_definitiva"]
    if ext_docs:
        # F-13 — trava financeira: depósito judicial sem destinação posterior?
        if _tem_pendencia_financeira(pieces):
            return _build_result(
                "16", 0.45,
                [p.ordem for p in ext_docs],
                flags={"pendencia_financeira": True},
                regra="F-13 / RE-03.2",
                raciocinio="Extinção definitiva acompanhada de depósito judicial sem "
                           "destinação visível: trava financeira ativa (16).",
                motivo_abstencao="pendencia_financeira",
                fase_provavel="15",
            )
        # RE-03.2: arquivamento pós-conversão é vedado sob perspectiva padrão, mas
        # sem conversão (acima) pode arquivar
        ext = max(ext_docs, key=lambda p: p.sort_key)
        # polaridade negativa (precatório pago) → 15 (F-09)
        prec = [p for p in pieces if p.tipo == "precatorio_rpv"]
        if prec:
            return _build_result(
                "15", 0.85,
                [ext.ordem] + [p.ordem for p in prec],
                flags={},
                regra="R3.2 + F-09",
                raciocinio="Extinção definitiva após pagamento de precatório/RPV — "
                           "satisfação contra o ente, nunca 14.",
            )
        return _build_result(
            "15", 0.85, [ext.ordem], flags,
            regra="R3.2",
            raciocinio="Extinção definitiva (baixa/arquivamento definitivo) sem "
                       "arrecadação ao ente credor.",
        )

    # R3.3 — suspensão total (art. 921 CPC / 40 LEF / parcelamento) → 11
    susp_total = _latest_tipo(pieces, ["suspensao_execucao"])
    # Sair de 11 precisa de "retomada" posterior
    retomada = _latest_tipo(pieces, ["retomada"])
    if susp_total and (not retomada or retomada.sort_key < susp_total.sort_key):
        return _build_result(
            "11", 0.82, [susp_total.ordem], flags,
            regra="R3.3 / RE-03.2",
            raciocinio="Suspensão executiva (art. 921 CPC / 40 LEF / parcelamento) ativa; "
                       "arquivamento provisório jamais é 15.",
        )

    # R3.4 — suspensão parcial → 12
    susp_parc = _latest_tipo(pieces, ["suspensao_parcial"])
    if susp_parc and (not retomada or retomada.sort_key < susp_parc.sort_key):
        return _build_result(
            "12", 0.80, [susp_parc.ordem], flags,
            regra="R3.4",
            raciocinio="Suspensão executiva parcial (impugnação/embargos com efeito "
                       "suspensivo parcial).",
        )

    # R3.5 — atos executivos em curso → 10
    atos = [p for p in pieces if p.tipo in (
        "inicio_cumprimento", "atos_constritivos", "destinacao_financeira"
    ) and not p.is_noise]
    if atos:
        # polaridade indeterminada de algum Mandado/Pagamento sem destinação → trava (F-13)?
        # Para fase 10 não há trava: 10 é execução em curso.
        latest = max(atos, key=lambda p: p.sort_key)
        # F-09 — precatório expedição = 10, mas polo passivo fazendário (não 14)
        if any(p.tipo == "precatorio_rpv" for p in pieces):
            prec = max((p for p in pieces if p.tipo == "precatorio_rpv"), key=lambda p: p.sort_key)
            return _build_result(
                "10", 0.85,
                [prec.ordem] + [latest.ordem],
                flags={},
                regra="R3.5 + F-09",
                raciocinio="Expedição de precatório/RPV: execução em curso contra o ente.",
            )
        return _build_result(
            "10", 0.80, [latest.ordem], flags,
            regra="R3.5",
            raciocinio="Atos executivos/constritivos em curso ou petição inicial de "
                       "execução/cumprimento.",
        )

    # Classe executiva com árvore pobre → 16 (RE-11 conflito)
    if classe_e_executiva(classe_norm):
        return _build_result(
            "16", 0.40, [],
            flags={"arvore_opaca": True},
            regra="RE-11",
            raciocinio="Classe executiva com árvore sem peça executiva nominada: "
                       "trava RE-11 impede 01-09; sem peça sustaining → 16.",
            motivo_abstencao="contradicao_documental",
            fase_provavel="10",
        )

    # Sem peça executiva → 16
    return _build_result(
        "16", 0.35, [],
        flags={"arvore_opaca": True},
        regra="RE-07",
        raciocinio="Domínio execução sem peça executiva determinante.",
        motivo_abstencao="opacidade",
        fase_provavel="10",
    )


# ============================================================
# R4 — Domínio de Conhecimento
# ============================================================

def classify_knowledge(
    pieces: List[DocumentPiece],
    classe_norm: Optional[str],
    perspectiva: str = "processual_arrecadatoria",
    threshold_abstencao: float = 0.75,
) -> Dict[str, Any]:
    """Aplica R4.1..R4.6. Sempre respeita RE-05 (trânsito exige certidão)."""
    determinantes: List[int] = []
    flags: Dict[str, Any] = {}
    regras: List[str] = []
    raciocinio: str = ""

    # R4.1 — sobrestamento ativo → 13 + fase_subjacente
    sobre = _latest_tipo(pieces, ["sobrestamento"])
    retomada = _latest_tipo(pieces, ["retomada"])
    if sobre and (not retomada or retomada.sort_key < sobre.sort_key):
        # fase subjacente: derivar do último julgado/recurso anterior ao sobrestamento
        fase_subj = _fase_subjacente_sobrestamento(pieces, sobre)
        tema = _extrair_tema(sobre)
        flags["fase_subjacente"] = fase_subj
        if tema:
            flags["tema_vinculado"] = tema
        determinantes.append(sobre.ordem)
        return _build_result(
            "13", 0.85, determinantes, flags,
            regra="R4.1 / F-06",
            raciocinio=(
                f"Sobrestamento ativo ({sobre.titulo or sobre.nome_arquivo}); "
                f"fase subjacente {fase_subj}. Sem peça de retomada, permanece 13 (RE-08)."
            ),
        )

    # R4.2 — grau efetivo: maior grau com julgamento pendente/não transitado
    grau_efetivo = _grau_efetivo_conhecimento(pieces)
    # Detectar peças-chave por grau
    cert_transito = _find_certidao_transito(pieces)
    if cert_transito:
        grau_cert = _resolve_grau_certidao(cert_transito, pieces)
        # R4.3 / R4.4 / R4.5 — certidão de trânsito → 09/06/03 conforme grau
        # Mas se houver apelação/recurso POSTERIOR à certidão → F-11 (contradição)
        rec_after_cert = any(
            p.tipo in ("apelacao", "resp_re", "embargos_declaracao")
            and not p.is_noise and p.sort_key > cert_transito.sort_key
            for p in pieces
        )
        if rec_after_cert:
            # Sem peça desconstitutiva explícita → 16 (RE-07, F-11)
            return _build_result(
                "16", 0.45,
                [cert_transito.ordem],
                flags={"arvore_opaca": False},
                regra="F-11 / RE-07",
                raciocinio=("Certidão de trânsito seguida de peça recursal posterior sem "
                            "peça desconstitutiva: contradição documental (16)."),
                motivo_abstencao="contradicao_documental",
                fase_provavel=({"G1": "03", "G2": "06", "SUP": "09"}.get(grau_cert, "03")),
            )
        # Determinar fase pelo grau
        if grau_cert == "SUP":
            return _build_result(
                "09", 0.95,
                [cert_transito.ordem],
                flags={},
                regra="R4.3",
                raciocinio="Certidão de trânsito em julgado pós-acórdão STJ/STF.",
            )
        if grau_cert == "G2":
            return _build_result(
                "06", 0.95,
                [cert_transito.ordem],
                flags={},
                regra="R4.4",
                raciocinio="Certidão de trânsito em julgado pós-acórdão G2.",
            )
        return _build_result(
            "03", 0.93,
            [cert_transito.ordem],
            flags={},
            regra="R4.5",
            raciocinio="Certidão de trânsito em julgado pós-sentença G1.",
        )

    # Acórdão sem trânsito (08/05/02 conforme grau)
    acordao_sup = _latest_tipo(pieces, ["acordao_sup"])
    acordao_g2 = _latest_tipo(pieces, ["acordao_g2"])
    if acordao_sup:
        # Pode haver recurso posterior? se sim, ainda SUP (07) — mas STJ/STF é terminal
        # Mantemos 08 com confiança alta
        return _build_result(
            "08", 0.88, [acordao_sup.ordem],
            flags={},
            regra="R4.3",
            raciocinio="Acórdão/decisão STJ/STF sem certidão de trânsito posterior.",
        )
    if acordao_g2:
        # Se sentença contra Fazenda e há remessa, F-03 já aplicado (em pendente_julgamento)
        # Verifica se há recurso para superior pendente após acórdão
        rec_sup_after = any(
            p.tipo == "resp_re" and not p.is_noise
            and p.sort_key > acordao_g2.sort_key
            for p in pieces
        )
        if rec_sup_after:
            return _build_result(
                "07", 0.85, [acordao_g2.ordem],
                flags={},
                regra="R4.6 + R4.3",
                raciocinio="Acórdão G2 seguido de interposição de REsp/RE pendente.",
            )
        return _build_result(
            "05", 0.85, [acordao_g2.ordem],
            flags={},
            regra="R4.4",
            raciocinio="Acórdão G2 sem certidão de trânsito posterior.",
        )

    # Apelação/remessa pendente → 04
    apelacao = _latest_tipo(pieces, ["apelacao", "contrarrazoes"])
    remessa = _latest_tipo(pieces, ["remessa_necessaria"])
    if apelacao or remessa:
        determinante = (apelacao or remessa)
        determinantes.append(determinante.ordem)
        flags_select = {}
        regra_select = "R4.4"
        if remessa and (not apelacao or apelacao.sort_key < remessa.sort_key):
            flags_select["remessa_necessaria"] = True
            regra_select = "R4.4 + F-03"
            rac = "Remessa necessária pendente de julgamento em 2ª instância (F-03)."
        else:
            rac = "Apelação/contrarrazões pendente de julgamento em 2ª instância."
        # Se cumprimento provisório (F-01) — atos constritivos após sentença mas recurso pendente
        atos_after = any(
            p.tipo in ("atos_constritivos", "inicio_cumprimento")
            and not p.is_noise and p.sort_key > determinante.sort_key
            for p in pieces
        )
        if atos_after:
            flags_select["execucao_provisoria"] = True
            regra_select = "F-01 + " + regra_select
            rac = (
                "Recurso pendente no mérito (posição recursal domina) + atos "
                "constritivos/cumprimento provisório ≠ 10 (execucao_provisoria)."
            )
        # Acórdão antes da apelação = recurso já julgado?
        # Se há sentença + apelação + acórdão (já capturado acima), segue 04 sem acórdão
        return _build_result(
            "04", 0.82, determinantes, flags_select,
            regra=regra_select, raciocinio=rac,
        )

    # REsp/RE pendente sem acórdão → 07
    resp = _latest_tipo(pieces, ["resp_re"])
    if resp and not acordao_g2:
        # há apelação/acordao subjacente? "juizo_admissibilidade" indica SUP pendente
        return _build_result(
            "07", 0.82, [resp.ordem],
            flags={},
            regra="R4.6",
            raciocinio="Recurso STJ/STF interposto, pendente de julgamento.",
        )

    # Sentença sem trânsito → 02 (verifica F-03 ausência de remessa)
    sentenca = _latest_tipo(pieces, ["sentenca"])
    if sentenca:
        # cumprimento provisório (F-01) = 04 já tratado acima se há recurso
        # sem recurso após sentença:
        rec_after_sent = any(
            p.tipo in ("apelacao", "remessa_necessaria", "resp_re")
            and not p.is_noise and p.sort_key > sentenca.sort_key
            for p in pieces
        )
        if rec_after_sent:
            # já capturado em 04 ou 07 acima
            pass
        else:
            # F-03: não presumir remessa se não há peça
            return _build_result(
                "02", 0.88, [sentenca.ordem],
                flags={},
                regra="R4.5 + F-03",
                raciocinio="Sentença sem trânsito em julgado e sem peça recursal posterior.",
            )

    # Sem peça decisória → 01 (com aviso se árvore opaca)
    if any(p.tipo == "peticao_inicial" for p in pieces):
        # Verifica opacidade: a maioria das peças é ruído?
        noise_count = sum(1 for p in pieces if p.is_noise)
        if noise_count > len(pieces) / 2:
            return _build_result(
                "16", 0.40, [],
                flags={"arvore_opaca": True},
                regra="RE-07",
                raciocinio="Árvore predominantemente opaca (dossiê de trabalho) sem peça "
                           "decisória nominada.",
                motivo_abstencao="opacidade",
                fase_provavel="01",
            )
        return _build_result(
            "01", 0.75,
            [p.ordem for p in pieces if p.tipo == "peticao_inicial"],
            flags={},
            regra="R4.5",
            raciocinio="Sem sentença/acórdão/certidão: processo em fase de conhecimento pré-sentença.",
        )

    # Árvore totalmente sem peça inicial identficada → 16
    return _build_result(
        "16", 0.30, [],
        flags={"arvore_opaca": True},
        regra="RE-07 / RE-10",
        raciocinio=("Sem petição inicial, sem peça decisória: sinais insuficientes para "
                    "qualquer fase substantiva."),
        motivo_abstencao="opacidade",
        fase_provavel="01",
    )


# ============================================================
# RE-12 — Fallback de teor (Etapa 1.6)
# ============================================================

# Gatilhos de linguagem dispositiva (Etapa 1.5)
_TEOR_TRIGGER_SENTENCA = [
    r"julgo procedente|julgo improcedente|resolvo o merito|extingo sem resolu.*merito|homologo o acordo|art\.?\s*487|art\.?\s*485",
]
_TEOR_TRIGGER_TRANSITO = [
    r"certifico o transito em julgado|certifico.*transito em julgado|transit?\s*o? em julgado da senten",
]
_TEOR_TRIGGER_SUSP_EXEC = [
    r"suspendo o curso da execu|art\.?\s*921|art\.?\s*40.*lef|arquivo provisorio",
]
_TEOR_TRIGGER_CONV_RENDA = [
    r"converto em renda|extingo pela satisfacao|art\.?\s*924.*ii",
]
_TEOR_TRIGGER_CONSTRI = [
    r"bloqueio de ativos via sisbajud|restricao via renajud|inscricao via serasajud|penhoro|expeca.*mandado de penhora",
]


def aplicar_fallback_teor(
    pieces: List[DocumentPiece],
    preliminar_16: Dict[str, Any],
    threshold: float = 0.75,
) -> Optional[Dict[str, Any]]:
    """
    Etapa 1.6 + R5 — fallback de teor das até 5 peças mais recentes.

    Acionado apenas se a classificação preliminar resultou em 16. Se o teor
    trouxer ato decisório/certificatório/satisfativo inequívoco e a confiança
    alcançar threshold, retorna nova classificação; senão None (manter 16).
    """
    # Ordenar mais recentes primeiro; incluir peças opacas e despachos
    sorted_desc = sorted(pieces, key=lambda p: p.sort_key, reverse=True)
    cand = [p for p in sorted_desc if p.teor][:5]
    if not cand:
        return None

    lidos: List[int] = []
    for p in cand:
        lidos.append(p.ordem)
        teor = _normalize_text(p.teor)

        # Sentença
        if any(re.search(r, teor) for r in _TEOR_TRIGGER_SENTENCA):
            return _build_result(
                "02", 0.85, [p.ordem],
                flags={
                    "fallback_teor_acionado": True,
                    "documentos_lidos_fallback": lidos,
                    "arvore_opaca": True,
                },
                regra="RE-12 + R5",
                raciocinio=(f"Teor do doc {p.ordem} revela dispositivo de "
                            f"julgamento de mérito (sentença) — fallback acionado."),
                modo_evidencia="metadados_e_teor",
            )
        # Trânsito
        if any(re.search(r, teor) for r in _TEOR_TRIGGER_TRANSITO):
            # Detectar grau pelo contexto
            grau = _grau_do_ultimo_julgado(pieces)
            fase = {"G1": "03", "G2": "06", "SUP": "09"}.get(grau, "03")
            return _build_result(
                fase, 0.88, [p.ordem],
                flags={
                    "fallback_teor_acionado": True,
                    "documentos_lidos_fallback": lidos,
                    "arvore_opaca": True,
                },
                regra="RE-12 + RE-05",
                raciocinio=(f"Teor do doc {p.ordem} certifica expressamente trânsito em "
                            f"julgado (RE-05); grau {grau}."),
                modo_evidencia="metadados_e_teor",
            )
        # Suspensão executiva
        if any(re.search(r, teor) for r in _TEOR_TRIGGER_SUSP_EXEC):
            return _build_result(
                "11", 0.82, [p.ordem],
                flags={
                    "fallback_teor_acionado": True,
                    "documentos_lidos_fallback": lidos,
                    "arvore_opaca": True,
                },
                regra="RE-12 + RE-03.2",
                raciocinio=(f"Teor do doc {p.ordem} revela suspensão executiva "
                            f"(art. 921/40 LEF)."),
                modo_evidencia="metadados_e_teor",
            )
        # Conversão em renda
        if any(re.search(r, teor) for r in _TEOR_TRIGGER_CONV_RENDA):
            return _build_result(
                "14", 0.88, [p.ordem],
                flags={
                    "fallback_teor_acionado": True,
                    "documentos_lidos_fallback": lidos,
                    "houve_conversao_em_renda": True,
                    "arvore_opaca": True,
                },
                regra="RE-12 + RE-06",
                raciocinio=(f"Teor do doc {p.ordem} revela conversão em renda / "
                            f"extinção pela satisfação."),
                modo_evidencia="metadados_e_teor",
            )
        # Constrição
        if any(re.search(r, teor) for r in _TEOR_TRIGGER_CONSTRI):
            return _build_result(
                "10", 0.82, [p.ordem],
                flags={
                    "fallback_teor_acionado": True,
                    "documentos_lidos_fallback": lidos,
                    "arvore_opaca": True,
                },
                regra="RE-12 + RE-01",
                raciocinio=(f"Teor do doc {p.ordem} revela ato constritivo "
                            f"(Sisbajud/Renajud/penhora)."),
                modo_evidencia="metadados_e_teor",
            )

    return None


# ============================================================
# Helpers auxiliares
# ============================================================

def _latest_tipo(pieces: List[DocumentPiece], tipos_prefix: List[str]) -> Optional[DocumentPiece]:
    cands = [p for p in pieces if any(p.tipo.startswith(t) for t in tipos_prefix)]
    if not cands:
        return None
    return max(cands, key=lambda p: p.sort_key)


def _fase_subjacente_sobrestamento(pieces: List[DocumentPiece], sobre: DocumentPiece) -> str:
    """Deriva fase subjacente pelo estado anterior ao sobrestamento."""
    anteriores = [p for p in pieces if p.sort_key < sobre.sort_key and not p.is_noise]
    # Simplificado: se há apelação anterior, 04; sentença, 02; senão 01
    if any(p.tipo.startswith("apelacao") or p.tipo.startswith("resp_re") for p in anteriores):
        return "04"
    if any(p.tipo == "sentenca" for p in anteriores):
        return "02"
    return "01"


def _extrair_tema(p: DocumentPiece) -> Optional[str]:
    """Captura 'Tema XXXX' / 'IRDR nnnn' do título/nome/teor."""
    blob = f"{p.titulo} {p.nome_arquivo} {p.teor}"
    m = re.search(r"tema\s*(?:repetitivo\s*)?(\d{3,5})", _normalize_text(blob))
    if m:
        return f"Tema {m.group(1)}"
    m = re.search(r"irdr\s*(\d{3,5})", _normalize_text(blob))
    if m:
        return f"IRDR {m.group(1)}"
    return None


def _tem_pendencia_financeira(pieces: List[DocumentPiece]) -> bool:
    """F-13 — depósito judicial sem destinação posterior + arquivamento/baixa."""
    tem_deposito = any(p.tipo == "deposito_judicial" for p in pieces)
    tem_destinacao = any(
        p.tipo in ("conversao_renda", "destinacao_financeira", "certidao_saldo")
        and _polaridade(p) != "indeterminada"
        for p in pieces
    )
    tem_extincao = any(p.tipo == "extincao_definitiva" for p in pieces)
    return tem_deposito and not tem_destinacao and tem_extincao


def _grau_efetivo_conhecimento(pieces: List[DocumentPiece]) -> str:
    """Maior grau com julgamento pendente/não transitado (não usado diretamente aqui)."""
    return _grau_do_ultimo_julgado(pieces)


# ============================================================
# Builder de resultado parcial
# ============================================================

def _build_result(
    fase_codigo: str,
    confianca: float,
    documentos_determinantes: List[int],
    flags: Dict[str, Any],
    regra: str,
    raciocinio: str,
    modo_evidencia: str = "metadados_apenas",
    fase_provavel: Optional[str] = None,
    motivo_abstencao: Optional[str] = None,
) -> Dict[str, Any]:
    """Resultado parcial que o classifier.py consolida em output completo."""
    return {
        "fase_codigo": fase_codigo,
        "confianca": confianca,
        "documentos_determinantes": documentos_determinantes,
        "flags": flags,
        "regra_determinante": regra,
        "raciocinio": raciocinio,
        "modo_evidencia": modo_evidencia,
        "fase_provavel": fase_provavel,
        "motivo_abstencao": motivo_abstencao,
    }
