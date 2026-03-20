"""Tests for ProcessService Fusion fallback integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.process_service import ProcessService


class TestProcessServiceFusionFallback:
    """Tests for Fusion fallback when DataJud returns not_found."""

    @pytest.mark.asyncio
    async def test_ativa_fusion_quando_datajud_not_found(self, test_db):
        """TC-1: FusionService é chamado quando DataJud retorna None."""
        from backend.services.fusion_api_client import FusionResult
        from backend.services.document_phase_classifier import FusionMovimento
        from datetime import datetime

        fusion_result = FusionResult(
            numero_cnj="0000001-01.2020.8.19.0001",
            neo_id=999,
            classe_processual="Ação Cível",
            sistema="TJRJ_DCP",
            movimentos=[
                FusionMovimento(
                    data=datetime(2024, 1, 1),
                    tipo_local="Sentença",
                    tipo_cnj="Sentença",
                )
            ],
            fonte="fusion_api",
        )

        mock_datajud = MagicMock()
        mock_datajud.get_process = AsyncMock(return_value=None)

        mock_fusion = MagicMock()
        mock_fusion.get_document_tree = AsyncMock(return_value=fusion_result)

        service = ProcessService(
            db=test_db,
            client=mock_datajud,
            fusion_service=mock_fusion,
        )

        result = await service.get_or_update_process("0000001-01.2020.8.19.0001")

        mock_fusion.get_document_tree.assert_called_once()
        assert result is not None
        assert result.phase_source == "fusion_api"

    @pytest.mark.asyncio
    async def test_nao_ativa_fusion_quando_datajud_retorna_dados(self, test_db):
        """TC-2: FusionService NÃO é chamado quando DataJud encontra o processo."""
        mock_datajud = MagicMock()
        mock_datajud.get_process = AsyncMock(return_value={"hits": {"hits": [{"_source": {
            "numeroJudicial": "0000001-01.2020.8.19.0001",
            "classeProcessual": "Ação Cível",
            "dataDistribuicao": "2020-01-01"
        }}]}})

        mock_fusion = MagicMock()
        mock_fusion.get_document_tree = AsyncMock()

        service = ProcessService(
            db=test_db,
            client=mock_datajud,
            fusion_service=mock_fusion,
        )

        result = await service.get_or_update_process("0000001-01.2020.8.19.0001")

        mock_fusion.get_document_tree.assert_not_called()
        assert result is not None
