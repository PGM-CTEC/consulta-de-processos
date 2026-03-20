"""Tests for FusionAPIClient — PAV REST API client."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from backend.services.fusion_api_client import FusionAPIClient
from backend.services.document_phase_classifier import FusionMovimento


MOCK_RESPONSE = {
    "dadosPAV": {"wfProcessNeoId": 950453990, "neoId": 950453990},
    "dadosGerais": {
        "numeroJudicial": "00754816320208190001",
        "classeProcessual": "Cumprimento de sentença",
        "descricaoSistema": "TJRJ_DCP",
    },
    "movimentos": [
        {
            "dataDoMovimento": "08/04/2020 15:59",
            "tipoMovimentoCNJ": "Distribuição",
            "tipoMovimentoLocal": "DISTRIBUIÇÃO Sorteio",
            "documentos": ["123"],
        },
        {
            "dataDoMovimento": "10/02/2024 15:14",
            "tipoMovimentoCNJ": "Sentença",
            "tipoMovimentoLocal": "Sentença",
            "documentos": ["456"],
        },
    ],
    "encontradoTribunal": True,
    "uuid": "abc-123",
}


class TestFusionAPIClientParse:
    """Tests for response parsing."""

    def test_parse_retorna_fusion_result_correto(self):
        """TC-1: Parse retorna FusionResult com campos corretos."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=test",
            timeout=30,
        )
        result = client._parse(MOCK_RESPONSE, "00754816320208190001")

        assert result.neo_id == 950453990
        assert result.classe_processual == "Cumprimento de sentença"
        assert result.sistema == "TJRJ_DCP"
        assert result.fonte == "fusion_api"
        assert len(result.movimentos) == 2

    def test_parse_ordena_movimentos_por_data(self):
        """TC-2: Movimentos são ordenados cronologicamente (ASC)."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=test",
            timeout=30,
        )
        result = client._parse(MOCK_RESPONSE, "00754816320208190001")

        datas = [m.data for m in result.movimentos]
        assert datas == sorted(datas)

    def test_parse_converte_tipo_local_corretamente(self):
        """TC-3: tipoMovimentoLocal é mapeado para FusionMovimento.tipo_local."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=test",
            timeout=30,
        )
        result = client._parse(MOCK_RESPONSE, "00754816320208190001")
        assert result.movimentos[0].tipo_local == "DISTRIBUIÇÃO Sorteio"


class TestFusionAPIClientHTTP:
    """Tests for HTTP request behavior."""

    @pytest.mark.asyncio
    async def test_get_document_tree_chama_endpoint_correto(self):
        """TC-4: URL do endpoint contém número CNJ sem formatação."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=abc",
            timeout=30,
        )
        mock_resp = MagicMock()
        mock_resp.content = json.dumps(MOCK_RESPONSE).encode("utf-8")
        mock_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "get", new_callable=AsyncMock, return_value=mock_resp) as mock_get:
            await client.get_document_tree("0075481-63.2020.8.19.0001")
            called_url = mock_get.call_args[0][0]
            assert "00754816320208190001" in called_url
            assert "dados-da-consulta" in called_url

    @pytest.mark.asyncio
    async def test_get_document_tree_retorna_none_se_nao_encontrado(self):
        """TC-5: Retorna None se encontradoTribunal for False."""
        client = FusionAPIClient(
            base_url="https://pav.procuradoria.rio",
            session_cookie="JSESSIONID=abc",
            timeout=30,
        )
        mock_resp = MagicMock()
        mock_resp.content = json.dumps({**MOCK_RESPONSE, "encontradoTribunal": False}).encode("iso-8859-1")
        mock_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "get", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.get_document_tree("0075481-63.2020.8.19.0001")
            assert result is None
