"""
PAV Data Transformer — Normaliza resposta completa do PAV para formato interno.

O endpoint /services/custom-consulta-rapida-de-procesos/dados-da-consulta/{numero}
retorna um JSON completo com:
- dadosPAV: informações administrativas (situação, localização, procurador)
- dadosGerais: informações processuais (número, tribunal, classe, data)
- partes: lista de atores (autor, réu, terceiros)
- movimentos: lista de movimentos (data, descrição, tipo)
- assuntos: tópicos relacionados
- recursos: recursos processuais
- outrasInformacoes: dados adicionais

Esta classe transforma esses dados para o formato esperado pelo modelo Process.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
from .document_phase_classifier import FusionMovimento

logger = logging.getLogger(__name__)


class PAVDataTransformer:
    """Transforma dados completos do PAV para formato interno da aplicação."""

    @staticmethod
    def transform(pav_response: dict) -> Dict:
        """
        Transforma resposta completa do PAV em dicionário normalizando.

        Args:
            pav_response: JSON completo do PAV.

        Returns:
            Dict com campos normalizados para o modelo Process.

        Raises:
            ValueError: Se resposta PAV está vazia ou mal formada.
        """
        if not pav_response:
            raise ValueError("Resposta PAV vazia")

        # Extrair seções principais
        dados_gerais = pav_response.get("dadosGerais", {})
        dados_pav = pav_response.get("dadosPAV", {})
        partes = pav_response.get("partes", [])
        movimentos_raw = pav_response.get("movimentos", [])

        # Extrair campo de número processual
        numero_judicial = dados_gerais.get("numeroJudicial", "")
        if not numero_judicial:
            raise ValueError("Número judicial não encontrado na resposta PAV")

        # Normalizar dados cadastrais
        tribunal_name = dados_gerais.get("orgaoJulgador", "")
        classe_processual = dados_gerais.get("classeProcessual", "")
        data_ajuizamento = dados_gerais.get("dataAjuizamento")

        # Extrair principais partes (autor e réu)
        autor = PAVDataTransformer._extract_actor(partes, "Autor")
        reu = PAVDataTransformer._extract_actor(partes, "Réu")

        # Normalizar movimentos para formato FusionMovimento
        movimentos = PAVDataTransformer._transform_movimentos(movimentos_raw)

        # Montar estrutura compatível com formato antigo do DataJud
        # para manter compatibilidade com código existente
        normalized_data = {
            "numero": numero_judicial,
            "tribunal_name": tribunal_name,
            "classe": {
                "nome": classe_processual,
                "codigo": dados_gerais.get("classeProcessual", "")
            },
            "data_ajuizamento": data_ajuizamento,
            "autor_principal": autor,
            "reu_principal": reu,
            "movimentos": movimentos,
            "raw_data": {
                "__meta__": {
                    "fonte_pav": "custom-consulta-rapida",
                    "dados_pav": dados_pav,
                    "situacao": dados_pav.get("situacao"),
                    "localizacao": dados_pav.get("localizacaoCorrente"),
                    "procurador": dados_pav.get("procuradorResponsavel"),
                },
                "dadosGerais": dados_gerais,
                "partes": partes,
                "assuntos": pav_response.get("assuntos", []),
                "recursos": pav_response.get("recursos", []),
            }
        }

        return normalized_data

    @staticmethod
    def _extract_actor(partes: List[Dict], polo: str) -> Optional[str]:
        """
        Extrai nome do primeiro ator de um polo específico (Autor, Réu, etc.).

        Args:
            partes: Lista de partes do processo.
            polo: Polo processual ('Autor', 'Réu', 'Terceiro', etc.).

        Returns:
            Nome do ator ou None.
        """
        for parte in partes:
            if parte.get("tipoPolo") == polo:
                nome = parte.get("nome", "")
                # Limpar nome
                nome = nome.strip()
                if nome and nome.upper() != "OS MESMOS":
                    return nome
        return None

    @staticmethod
    def _transform_movimentos(movimentos_raw: List[Dict]) -> List[FusionMovimento]:
        """
        Transforma lista de movimentos do PAV em FusionMovimento.

        Formato do PAV:
        {
            "dataDoMovimento": "16/07/2025 11:08",
            "descricao": "Identificador Processo: ...",
            "tipoMovimentoCNJ": "Recebimento",
            "tipoMovimentoLocal": "Indisponível",
            "documentos": [...]
        }

        Returns:
            Lista de FusionMovimento, ordenada por data ASC.
        """
        movimentos = []

        for mov_raw in movimentos_raw:
            try:
                data_str = mov_raw.get("dataDoMovimento", "")
                if not data_str:
                    continue

                # Parsear data no formato DD/MM/YYYY HH:MM ou DD/MM/YYYY HH:MM:SS
                try:
                    # Tentar com segundos primeiro
                    data = datetime.strptime(data_str.strip(), "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    try:
                        # Tentar sem segundos
                        data = datetime.strptime(data_str.strip(), "%d/%m/%Y %H:%M")
                    except ValueError:
                        logger.warning(f"Não foi possível parsear data: {data_str}")
                        continue

                # Extrair tipo de movimento (preferir CNJ, senão local)
                tipo_movimento = mov_raw.get("tipoMovimentoCNJ") or mov_raw.get("tipoMovimentoLocal")
                descricao = mov_raw.get("descricao", "")

                # Criar FusionMovimento
                movimento = FusionMovimento(
                    data=data,
                    tipo_local=descricao[:100] if descricao else tipo_movimento,  # primeiros 100 chars
                    tipo_cnj=tipo_movimento or "Unknown"
                )
                movimentos.append(movimento)

            except Exception as e:
                logger.warning(f"Erro ao parsear movimento {mov_raw}: {e}")
                continue

        # Ordenar por data (ASC)
        movimentos.sort(key=lambda m: m.data)

        return movimentos

    @staticmethod
    def extract_movimentos_for_classification(pav_response: dict) -> List[FusionMovimento]:
        """
        Extrai apenas movimentos do PAV para classification de fase.

        Retorna lista de FusionMovimento para passar ao DocumentPhaseClassifier.

        Args:
            pav_response: JSON completo do PAV.

        Returns:
            Lista de FusionMovimento.
        """
        movimentos_raw = pav_response.get("movimentos", [])
        return PAVDataTransformer._transform_movimentos(movimentos_raw)

    @staticmethod
    def extract_classe_processual(pav_response: dict) -> str:
        """
        Extrai classe processual da resposta PAV.

        Args:
            pav_response: JSON completo do PAV.

        Returns:
            String com classe processual normalizada.
        """
        return pav_response.get("dadosGerais", {}).get("classeProcessual", "")
