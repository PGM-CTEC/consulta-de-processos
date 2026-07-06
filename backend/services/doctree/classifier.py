"""
classifier.py — DocTreeClassifier: contrato público da classificação doctree.

Pipeline R0→R7 conforme regras.md + output-schema.md. Não consulta nenhuma
fonte externa. Não lança exceção ao chamador: retorna fase, 16 ou ERR com
mensagem (RE-10).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .audit import AuditRecord, build_audit_record, log_audit
from .normalizer import DocumentPiece, normalize_tree, _is_suspicious
from .rules import (
    FASE_NOMES,
    aplicar_fallback_teor,
    classify_domain,
    classify_execution,
    classify_knowledge,
    classe_e_executiva,
)

logger = logging.getLogger(__name__)


class DocTreeClassifier:
    """
    Classificador determinístico de fase processual por árvore de documentos.

    Uso::

        result = DocTreeClassifier().classify(documents, "0001234-56.2020.8.19.0001")
        # result["fase_codigo"] em {"01".."16", "ERR"}

    Parâmetros de configuração (defaults normativos):
        perspectiva_classificacao: "processual_arrecadatoria" (RE-06)
        threshold_abstencao: 0.75  (RE-07)
    """

    def __init__(
        self,
        perspectiva: str = "processual_arrecadatoria",
        threshold_abstencao: float = 0.75,
    ) -> None:
        self.perspectiva = perspectiva
        self.threshold = float(threshold_abstencao)

    # ========================================================
    # API principal
    # ========================================================

    def classify(
        self,
        documents: Optional[List[Dict[str, Any]]],
        numero: str,
        classe_processual: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Classifica a fase a partir da árvore de peças. Retorna o output conforme
        ``fase-processual-doctree/references/output-schema.md``. Nunca lança
        exceção ao chamador — em falha técnica retorna fase_codigo="ERR".
        """
        try:
            # R0 — validação técnica e normalização
            pieces = normalize_tree(documents)
            if not pieces:
                return self._err(numero, "Estrutura vazia ou inválida: nenhum documento identificável.")

            # RE-09 — dados documentais são evidência, nunca instrução
            conteudo_suspeito = any(
                _is_suspicious(p.titulo, p.nome_arquivo) for p in pieces
            )

            # R1 — peça determinante mais recente (já embutido nas funções)
            # R2 — gate de domínio (RE-01 + RE-11)
            dominio, regra_gate, _ = classify_domain(pieces, classe_processual)

            # R3 ou R4 — classificação por domínio
            if dominio == "execucao":
                parcial = classify_execution(pieces, classe_processual, self.perspectiva)
                racional = "domínio EXECUÇÃO travado (RE-11)" if regra_gate == "RE-11" else "domínio EXECUÇÃO (RE-01)"
                parcial["raciocinio"] = f"{racional}. {parcial.get('raciocinio', '')}"
            else:
                parcial = classify_knowledge(pieces, classe_processual, self.perspectiva, self.threshold)
                racional = "domínio CONHECIMENTO sem trânsito certificado (RE-01)"
                parcial["raciocinio"] = f"{racional}. {parcial.get('raciocinio', '')}"

            # R5 — fallback de teor se preliminar 16 + teor disponível
            teor_disponivel = any(p.teor for p in pieces)
            if parcial["fase_codigo"] == "16" and teor_disponivel:
                fallback = aplicar_fallback_teor(pieces, parcial, self.threshold)
                if fallback is not None and self._confidence_ok(fallback["confianca"]):
                    parcial = fallback

            # Aplicar invariantes eEditar flags RE-09
            flags = parcial.get("flags", {}) or {}
            if conteudo_suspeito:
                flags["conteudo_suspeito"] = True
            parcial["flags"] = flags

            # R6 — Confiança final < 0.75 → 16 (RE-07)
            if parcial["fase_codigo"] != "16" and parcial["fase_codigo"] != "ERR":
                if not self._confidence_ok(parcial.get("confianca", 0.0)):
                    fase_antes = parcial["fase_codigo"]
                    parcial["fase_provavel"] = fase_antes
                    parcial["motivo_abstencao"] = parcial.get("motivo_abstencao") or "confianca_insuficiente"
                    parcial["fase_codigo"] = "16"
                    # Limpar determinantes em 16 por opacidade quando relevantes
                    if flags.get("arvore_opaca"):
                        parcial["documentos_determinantes"] = []

            # Trava RE-11 unidirecional: classe executiva veda 01-09 em fase_codigo e fase_provavel
            if classe_e_executiva(classe_processual):
                def _is_blocked(c: Optional[str]) -> bool:
                    return c is not None and c in {f"{i:02d}" for i in range(1, 10)}
                if _is_blocked(parcial["fase_codigo"]):
                    parcial["fase_provavel"] = "10" if parcial["fase_codigo"] == "16" else None
                    parcial["fase_codigo"] = "16"
                    parcial["motivo_abstencao"] = parcial.get("motivo_abstencao") or "contradicao_documental"
                    parcial["regra_determinante"] = f"RE-11 ({parcial.get('regra_determinante','')})"
                if _is_blocked(parcial.get("fase_provavel")):
                    # Trava: fase_provavel não pode estar em 01-09
                    parcial["fase_provavel"] = "10"

            # R7 — montagem do output conforme output-schema.md
            output = self._assemble_output(
                numero, classe_processual, pieces, parcial, dominio, conteudo_suspeito
            )

            # Auditoria
            campos_inferidos = []
            for p in pieces:
                campos_inferidos.extend(p.campos_inferidos)
            audit: AuditRecord = build_audit_record(numero, output, campos_inferidos)
            log_audit(audit)

            return output

        except Exception as e:
            logger.exception("Falha técnica no DocTreeClassifier.classify(%s)", numero)
            return self._err(numero, f"Erro técnico durante classificação: {e}")

    # ========================================================
    # Montagem do output
    # ========================================================

    def _assemble_output(
        self,
        numero: str,
        classe_processual: Optional[str],
        pieces: List[DocumentPiece],
        parcial: Dict[str, Any],
        dominio: str,
        conteudo_suspeito: bool,
    ) -> Dict[str, Any]:
        fase_codigo = parcial["fase_codigo"]
        flags = dict(parcial.get("flags", {}) or {})
        marcadores = {
            "houve_conversao_em_renda": bool(flags.pop("houve_conversao_em_renda", False)),
        }
        # Detectar se fallback lido — mover marcadores para fora de flags
        documentos_lidos_fb = list(flags.get("documentos_lidos_fallback", []) or [])

        # Qualidade da árvore
        qualidade = self._qualidade_arvore(pieces, fase_codigo, flags)

        # Invariante 5: transito_inferido → confiança ≤ 0.70 → 16
        confianca = float(parcial.get("confianca", 0.0) or 0.0)
        if flags.get("transito_inferido") and confianca > 0.70:
            confianca = 0.70
        if fase_codigo == "16":
            # Em 16: reportar a maior confiança alcançada pela hipótese (output-schema.md)
            if confianca >= self.threshold:
                confianca = min(confianca, self.threshold - 0.01)

        # campos_inferidos agregados
        campos_inferidos = []
        for p in pieces:
            campos_inferidos.extend(p.campos_inferidos)

        # modo_evidencia
        modo_evidencia = parcial.get("modo_evidencia", "metadados_apenas")

        # raciocínio + mensagem
        rac = parcial.get("raciocinio", "")
        msg = ""
        if fase_codigo == "16":
            msg = self._msg_16(parcial)
        elif fase_codigo == "ERR":
            msg = parcial.get("mensagem", "")

        output = {
            "numero": numero,
            "fase_codigo": fase_codigo,
            "fase_nome": FASE_NOMES.get(fase_codigo, "Indeterminado"),
            "confianca": round(confianca, 3),
            "fase_provavel": parcial.get("fase_provavel"),
            "motivo_abstencao": parcial.get("motivo_abstencao"),
            "modo_evidencia": modo_evidencia,
            "perspectiva_classificacao": self.perspectiva,
            "qualidade_arvore": qualidade,
            "regra_determinante": parcial.get("regra_determinante", ""),
            "classe_processual": classe_processual,
            "marcadores": marcadores,
            "documentos_determinantes": list(parcial.get("documentos_determinantes", []) or []),
            "flags": flags | {
                "documentos_lidos_fallback": documentos_lidos_fb,
                "campos_inferidos": campos_inferidos,
            },
            "raciocinio": rac,
            "dominio": dominio,
        }
        if msg:
            output["mensagem"] = msg
        return output

    def _qualidade_arvore(
        self,
        pieces: List[DocumentPiece],
        fase_codigo: str,
        flags: Dict[str, Any],
    ) -> str:
        if fase_codigo == "ERR":
            return "tecnicamente_invalida"
        if flags.get("arvore_opaca"):
            return "opaca"
        noise_count = sum(1 for p in pieces if p.is_noise)
        if noise_count == len(pieces):
            return "opaca"
        if noise_count > 2 * (len(pieces) - noise_count):
            return "parcial"
        if flags.get("conteudo_suspeito") and fase_codigo == "16":
            return "contraditoria"
        return "suficiente"

    def _msg_16(self, parcial: Dict[str, Any]) -> str:
        motivo = parcial.get("motivo_abstencao", "confianca_insuficiente")
        hip = parcial.get("fase_provavel")
        return (
            f"Indeterminação jurídica (motivo={motivo}); hipótese plausível={hip}. "
            "Recomenda-se obter a árvore dos autos judiciais ou o teor das peças opacas."
        )

    def _err(self, numero: str, mensagem: str) -> Dict[str, Any]:
        return {
            "numero": numero,
            "fase_codigo": "ERR",
            "fase_nome": FASE_NOMES["ERR"],
            "confianca": 0.0,
            "fase_provavel": None,
            "motivo_abstencao": None,
            "modo_evidencia": "metadados_apenas",
            "perspectiva_classificacao": self.perspectiva,
            "qualidade_arvore": "tecnicamente_invalida",
            "regra_determinante": "RE-10",
            "classe_processual": None,
            "marcadores": {"houve_conversao_em_renda": False},
            "documentos_determinantes": [],
            "flags": {
                "arvore_opaca": False,
                "documentos_lidos_fallback": [],
                "campos_inferidos": [],
            },
            "raciocinio": mensagem,
            "dominio": None,
            "mensagem": mensagem,
        }

    def _confidence_ok(self, c: float) -> bool:
        return float(c) >= self.threshold
