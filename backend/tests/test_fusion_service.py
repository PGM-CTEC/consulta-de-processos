"""Tests for FusionService orchestrator."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.services.fusion_service import FusionService
from backend.services.fusion_sql_client import FusionSQLException


def _make_result(fonte="fusion_api"):
    from backend.services.fusion_api_client import FusionResult
    from datetime import datetime
    return FusionResult(
        numero_cnj="0000001-01.2020.8.19.0001",
        neo_id=123,
        classe_processual="Ação Cível",
        sistema="TJRJ_DCP",
        movimentos=[],
        fonte=fonte,
    )


class TestFusionServiceOrchestration:
    """Tests for SQL → API fallback logic."""

    @pytest.mark.asyncio
    async def test_usa_sql_quando_disponivel(self):
        """TC-1: Usa SQL direto quando disponível."""
        sql = MagicMock()
        sql.is_available.return_value = True
        sql.get_document_tree = AsyncMock(return_value=_make_result("fusion_sql"))

        api = MagicMock()
        api.get_document_tree = AsyncMock()

        service = FusionService(sql_client=sql, api_client=api)
        result = await service.get_document_tree("0000001-01.2020.8.19.0001")

        assert result.fonte == "fusion_sql"
        api.get_document_tree.assert_not_called()

    @pytest.mark.asyncio
    async def test_fallback_para_api_quando_sql_falha(self):
        """TC-2: Cai para API REST quando SQL lança exceção."""
        sql = MagicMock()
        sql.is_available.return_value = True
        sql.get_document_tree = AsyncMock(side_effect=FusionSQLException("erro"))

        api = MagicMock()
        api.get_document_tree = AsyncMock(return_value=_make_result("fusion_api"))

        service = FusionService(sql_client=sql, api_client=api)
        result = await service.get_document_tree("0000001-01.2020.8.19.0001")

        assert result.fonte == "fusion_api"

    @pytest.mark.asyncio
    async def test_usa_api_quando_sql_nao_disponivel(self):
        """TC-3: Vai direto para API quando SQL não configurado."""
        sql = MagicMock()
        sql.is_available.return_value = False

        api = MagicMock()
        api.get_document_tree = AsyncMock(return_value=_make_result("fusion_api"))

        service = FusionService(sql_client=sql, api_client=api)
        result = await service.get_document_tree("0000001-01.2020.8.19.0001")

        assert result.fonte == "fusion_api"
        sql.get_document_tree.assert_not_called()

    @pytest.mark.asyncio
    async def test_retorna_none_quando_nao_encontrado(self):
        """TC-4: Retorna None quando API também não encontra o processo."""
        sql = MagicMock()
        sql.is_available.return_value = False

        api = MagicMock()
        api.get_document_tree = AsyncMock(return_value=None)

        service = FusionService(sql_client=sql, api_client=api)
        result = await service.get_document_tree("0000001-01.2020.8.19.0001")

        assert result is None
