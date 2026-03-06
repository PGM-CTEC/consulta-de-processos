import logging
import json
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

from .classification_rules import (
    ClassificadorFases, ProcessoJudicial, MovimentoProcessual,
    GrauJurisdicao, DocumentoProcessual
)

logger = logging.getLogger(__name__)

DCP_WARNING_MESSAGE = (
    "A classificação deste processo pode estar errada, considerando-se "
    "tratar de um processo do sistema DCP do TJRJ com mais de 5 anos"
)

CODIGOS_BAIXA = {22, 861, 865, 10965, 10966, 10967, 12618}
CODIGOS_REATIVACAO = {900, 12617, 849, 36}

# Prioridade de grau: maior valor = grau mais avançado
_GRAU_PRIORITY = {
    GrauJurisdicao.G1: 1,
    GrauJurisdicao.JE: 1,
    GrauJurisdicao.G2: 2,
    GrauJurisdicao.TR: 2,
    GrauJurisdicao.SUP: 3,
}


class PhaseAnalyzer:
    """
    Analyzes process phases using the strict deterministic rules from
    'classification_rules.py' (based on PGM-Rio Business Rules).
    """

    @staticmethod
    def analyze(class_code: int, movements: List[Dict], tribunal: str = "", grau: str = "G1", process_number: str = "", raw_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Main entry point for phase analysis. Adapts the input data to the
        ProcessoJudicial dataclass and runs the ClassificadorFases.
        
        Args:
            class_code: CNJ Class Code (int)
            movements: List of movement dicts (must contain 'codigo' and 'dataHora')
            tribunal: Tribunal identifier
            grau: 'G1', 'G2', 'STJ', etc.
            process_number: Process number (CNJ format)
            raw_data: Full raw data from DataJud (optional, but useful for extra fields)
        """
        try:
            grau_enum = PhaseAnalyzer._map_grau(grau)
            movimentos_adaptados = PhaseAnalyzer._adapt_movements(movements or [], grau_enum)

            class_desc = ""
            if raw_data:
                class_desc = raw_data.get('classe', {}).get('nome', '')

            # Determinar situação: BAIXADO se há baixa definitiva não revertida
            situacao = "MOVIMENTO"
            if PhaseAnalyzer._instance_has_baixa(movimentos_adaptados):
                situacao = "BAIXADO"
                logger.info(f"Processo {process_number} detectado como BAIXADO (instância única)")

            processo = ProcessoJudicial(
                numero=process_number or "0000000-00.0000.0.00.0000",
                classe_codigo=int(class_code or 0),
                classe_descricao=class_desc,
                grau_atual=grau_enum,
                situacao=situacao,
                movimentos=movimentos_adaptados,
                documentos=[],
                polo_fazenda="RE"
            )

            # 2. Run Classification
            classificador = ClassificadorFases()
            resultado = classificador.classificar(processo)
            
            # 3. Return Phase Code + Description (com sufixo DCP se aplicável)
            phase_str = f"{resultado.fase.value} {resultado.fase.descricao}"
            if PhaseAnalyzer._is_dcp_process(raw_data, tribunal):
                phase_str += " *"
            return phase_str

        except Exception as e:
            logger.error(f"Error in PhaseAnalyzer: {e}")
            return "Erro na Análise"

    @staticmethod
    def _is_dcp_process(raw_data: Optional[Dict[str, Any]], tribunal: str) -> bool:
        """
        Verifica se o processo é do sistema DCP do TJRJ com mais de 5 anos.

        Critérios (todos obrigatórios):
        1. tribunal == "TJRJ"
        2. raw_data.sistema.codigo == -1  (sistema legado DCP)
        3. dataAjuizamento há mais de 5 anos
        """
        if not raw_data or tribunal != "TJRJ":
            return False

        sistema = raw_data.get("sistema", {})
        if not isinstance(sistema, dict) or sistema.get("codigo") != -1:
            return False

        data_str = raw_data.get("dataAjuizamento", "")
        if not data_str:
            return False

        try:
            if len(data_str) >= 8 and data_str[:8].isdigit():
                data_ajuiz = datetime.strptime(data_str[:8], "%Y%m%d")
            else:
                data_ajuiz = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
            return (datetime.now() - data_ajuiz).days > 5 * 365
        except (ValueError, TypeError):
            return False

    # ==================== Análise Unificada ====================

    @staticmethod
    def _map_grau(grau: str) -> GrauJurisdicao:
        """Mapeia string de grau para enum GrauJurisdicao."""
        if grau in ("G2", "TR"):
            return GrauJurisdicao.G2
        if grau in ("STJ", "STF", "TST", "SUP"):
            return GrauJurisdicao.SUP
        if grau == "JE":
            return GrauJurisdicao.JE
        return GrauJurisdicao.G1

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse ISO date string com fallback seguro. Sempre retorna UTC-aware."""
        try:
            dt = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            return dt
        except (ValueError, TypeError, AttributeError):
            # Retornar datetime UTC-aware para não quebrar comparações
            return datetime.fromtimestamp(0)  # Epoch UTC

    @staticmethod
    def _adapt_movements(movements: List[Dict], grau_enum: GrauJurisdicao) -> List[MovimentoProcessual]:
        """Converte lista de dicts de movimentos para MovimentoProcessual."""
        result = []
        if not movements:
            return result
        for m in movements:
            try:
                cod = int(m.get('codigo', 0))
                result.append(MovimentoProcessual(
                    codigo=cod,
                    descricao=m.get('nome') or m.get('descricao', ''),
                    data=PhaseAnalyzer._parse_date(m.get('dataHora', '')),
                    grau=grau_enum,
                    complementos=m.get('complementos', {})
                ))
            except (ValueError, TypeError):
                continue
        return result

    @staticmethod
    def _instance_has_baixa(movimentos: List[MovimentoProcessual]) -> bool:
        """Verifica se uma instância tem baixa definitiva não revertida."""
        movs_baixa = [m for m in movimentos if m.codigo in CODIGOS_BAIXA]
        if not movs_baixa:
            return False
        ultima_baixa = max(movs_baixa, key=lambda m: m.data)
        movs_reativ = [m for m in movimentos
                       if m.codigo in CODIGOS_REATIVACAO and m.data > ultima_baixa.data]
        return len(movs_reativ) == 0

    @staticmethod
    def _merge_instance_movements(
        all_instances: List[Dict[str, Any]]
    ) -> Tuple[List[MovimentoProcessual], GrauJurisdicao, str, int, str]:
        """
        Mescla movimentos de todas as instâncias e determina grau/situação efetivos.

        IMPORTANTE: Movimentos de instâncias com Baixa Definitiva não revertida
        são EXCLUÍDOS do merge, pois essas instâncias estão inativas.

        Returns:
            (merged_movements, effective_grau, effective_situacao, class_code, class_desc)
        """
        all_movements: List[MovimentoProcessual] = []
        instance_info = []  # (grau_enum, has_baixa, sort_key, class_code, class_desc)

        for inst in all_instances:
            if not isinstance(inst, dict):
                continue
            grau_str = inst.get("grau", "G1") or "G1"
            grau_enum = PhaseAnalyzer._map_grau(grau_str)
            movs_raw = inst.get("movimentos", []) or []
            movs = PhaseAnalyzer._adapt_movements(movs_raw, grau_enum)

            has_baixa = PhaseAnalyzer._instance_has_baixa(movs)

            # CRÍTICO: Instâncias com Baixa não revertida são inativas
            # Seus movimentos NÃO devem influenciar a classificação final
            if not has_baixa:
                all_movements.extend(movs)

            has_baixa = PhaseAnalyzer._instance_has_baixa(movs)

            # Sort key: último movimento ou timestamp (ambos UTC-aware)
            latest_mov = None
            try:
                if movs:
                    # Filtrar movimentos com data válida (timezone-aware)
                    valid_dates = [m.data for m in movs if m.data and m.data.tzinfo]
                    if valid_dates:
                        latest_mov = max(valid_dates)
            except (TypeError, ValueError):
                pass

            updated_at = PhaseAnalyzer._parse_date(inst.get("dataHoraUltimaAtualizacao", "") or "")

            # Usar o timestamp mais recente
            candidates = [d for d in [latest_mov, updated_at] if d and d.tzinfo]
            if candidates:
                sort_key = max(candidates)
            else:
                sort_key = datetime.fromtimestamp(0)  # Epoch

            class_node = inst.get("classe", {}) or {}
            class_code = int(class_node.get("codigo", 0) or 0)
            class_desc = class_node.get("nome", "") or ""

            instance_info.append((grau_enum, has_baixa, sort_key, class_code, class_desc))

        if not instance_info:
            return [], GrauJurisdicao.G1, "MOVIMENTO", 0, ""

        # Deduplicar movimentos por (codigo, data, grau)
        seen = set()
        deduped = []
        for m in all_movements:
            key = (m.codigo, m.data, m.grau)
            if key not in seen:
                seen.add(key)
                deduped.append(m)
        all_movements = deduped

        # Se há reativação, remover movimentos de baixa precedentes
        # Isso garante que o classificador não vê "baixa" quando há reativação posterior
        reativ_movs = [m for m in all_movements if m.codigo in CODIGOS_REATIVACAO]
        if reativ_movs:
            latest_reativ = max(reativ_movs, key=lambda m: m.data)
            # Remover baixas que vêm ANTES da última reativação
            all_movements = [m for m in all_movements if not (
                m.codigo in CODIGOS_BAIXA and m.data < latest_reativ.data
            )]

        # Separar instâncias ativas (sem baixa) e baixadas
        active = [(g, bx, sk, cc, cd) for g, bx, sk, cc, cd in instance_info if not bx]
        baixada = [(g, bx, sk, cc, cd) for g, bx, sk, cc, cd in instance_info if bx]

        if active:
            # Grau efetivo: maior grau ativo
            effective_grau = max(
                (g for g, _, _, _, _ in active),
                key=lambda g: _GRAU_PRIORITY.get(g, 0)
            )
            situacao = "MOVIMENTO"
        else:
            # Todas baixadas: grau efetivo = maior grau com baixa mais recente
            effective_grau = max(
                ((g, sk) for g, _, sk, _, _ in baixada),
                key=lambda t: (_GRAU_PRIORITY.get(t[0], 0), t[1])
            )[0]
            situacao = "BAIXADO"

        # Classe processual: menor grau (G1/JE) = tipo real do processo
        # Ordena por prioridade ascendente, pega o primeiro
        def sort_key_for_class(t):
            grau, _, sort_key, _, _ = t
            ts = sort_key.timestamp() if sort_key and sort_key != datetime.min and sort_key.tzinfo else 0
            return (_GRAU_PRIORITY.get(grau, 0), -ts)

        lowest = min(instance_info, key=sort_key_for_class)
        class_code = lowest[3]
        class_desc = lowest[4]

        return all_movements, effective_grau, situacao, class_code, class_desc

    @staticmethod
    def analyze_unified(
        all_instances: List[Dict[str, Any]],
        process_number: str = "",
        tribunal: str = ""
    ) -> str:
        """
        Analisa a fase processual de forma unificada, considerando TODAS as instâncias.

        Mescla movimentos de todas as instâncias, determina o grau efetivo
        (maior grau ativo) e a situação efetiva (BAIXADO só se TODAS baixadas),
        e roda o ClassificadorFases sobre o conjunto completo.

        Args:
            all_instances: Lista de dicts (cada um é um _source completo do DataJud)
            process_number: Número do processo CNJ
            tribunal: Identificador do tribunal
        Returns:
            String da fase no formato "XX Descrição" (ex: "04 Conhecimento - Recurso 2ª Instância...")
        """
        try:
            movements, effective_grau, situacao, class_code, class_desc = \
                PhaseAnalyzer._merge_instance_movements(all_instances)

            processo = ProcessoJudicial(
                numero=process_number or "0000000-00.0000.0.00.0000",
                classe_codigo=class_code,
                classe_descricao=class_desc,
                grau_atual=effective_grau,
                situacao=situacao,
                movimentos=movements,
                documentos=[],
                polo_fazenda="RE"
            )

            classificador = ClassificadorFases()
            resultado = classificador.classificar(processo)

            phase_str = f"{resultado.fase.value} {resultado.fase.descricao}"

            # Verificar DCP em cada instância (basta uma ser DCP)
            for inst in all_instances:
                if PhaseAnalyzer._is_dcp_process(inst, tribunal):
                    phase_str += " *"
                    break

            logger.info(
                f"Unified phase for {process_number}: {phase_str} "
                f"(effective_grau={effective_grau.value}, situacao={situacao}, "
                f"instances={len(all_instances)}, movements={len(movements)})"
            )
            return phase_str

        except Exception as e:
            logger.error(f"Error in analyze_unified: {e}", exc_info=True)
            return "Erro na Análise"
