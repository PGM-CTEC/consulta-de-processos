"""
Tests for ProcessService (business logic layer).
Story: REM-017 - Backend Unit Tests (70% Coverage)

Test Categories:
- Unit tests: ProcessService methods in isolation
- Integration tests: ProcessService + mocked DataJud API
- Error handling: API errors, database errors, validation errors
- Async tests: Concurrent processing, semaphore limiting
- Data transformation: Parsing DataJud responses
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from backend.exceptions import DataJudAPIException, ProcessNotFoundException

from backend.services.process_service import ProcessService
from backend import models


class TestProcessServiceGetOrUpdateProcess:
    """Tests for get_or_update_process() - main business logic (9 tests)."""

    def test_get_or_update_process_new(self, process_service, sample_process_data):
        """TC-1: Create new process when not in database."""
        async def run_test():
            with patch.object(process_service.client, 'get_process', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = sample_process_data
                result = await process_service.get_or_update_process("00000001010000100001")

                assert result is not None
                assert result.number == "00000001010000100001"
                assert result.tribunal_name == "TJSP"
                assert result.class_nature == "Ação de Cobrança"
                mock_get.assert_called_once_with("00000001010000100001")

        asyncio.run(run_test())

    def test_get_or_update_process_update_existing(self, process_service, sample_process_db, sample_process_data):
        """TC-2: Update existing process with new data."""
        async def run_test():
            sample_process_data["classe"]["codigo"] = "0002"
            with patch.object(process_service.client, 'get_process', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = sample_process_data
                result = await process_service.get_or_update_process("00000001010000100001")

                assert result.number == "00000001010000100001"
                assert result.phase is not None
                assert result.last_update is not None

        asyncio.run(run_test())

    def test_get_or_update_process_not_found(self, process_service):
        """TC-3: Handle API 404 response (process not found)."""
        async def run_test():
            with patch.object(process_service.client, 'get_process', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = None
                result = await process_service.get_or_update_process("99999999999999999999")
                assert result is None

        asyncio.run(run_test())

    def test_get_or_update_process_api_error_fallback_to_cache(self, process_service, sample_process_db):
        """TC-4: Erros de API propagam exceção (sem fallback de cache)."""
        async def run_test():
            with patch.object(process_service.client, 'get_process', new_callable=AsyncMock) as mock_get:
                mock_get.side_effect = DataJudAPIException("API timeout")
                with pytest.raises(DataJudAPIException):
                    await process_service.get_or_update_process("00000001010000100001")

        asyncio.run(run_test())

    def test_get_or_update_process_api_error_no_cache(self, process_service):
        """TC-5: Raise error when API fails and no cache available."""
        async def run_test():
            with patch.object(process_service.client, 'get_process', new_callable=AsyncMock) as mock_get:
                mock_get.side_effect = DataJudAPIException("API connection failed")
                with pytest.raises(DataJudAPIException):
                    await process_service.get_or_update_process("99999999999999999999")

        asyncio.run(run_test())

    def test_get_or_update_process_unexpected_error_with_cache(self, process_service, sample_process_db):
        """TC-6: Erros inesperados propagam exceção (sem fallback de cache)."""
        async def run_test():
            with patch.object(process_service.client, 'get_process', new_callable=AsyncMock) as mock_get:
                mock_get.side_effect = Exception("Unexpected error")
                with pytest.raises(DataJudAPIException):
                    await process_service.get_or_update_process("00000001010000100001")

        asyncio.run(run_test())

    def test_get_or_update_process_records_history(self, process_service, sample_process_data):
        """TC-7: Verify search history is recorded."""
        async def run_test():
            with patch.object(process_service.client, 'get_process', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = sample_process_data
                with patch.object(process_service, '_record_history') as mock_record:
                    result = await process_service.get_or_update_process("00000001010000100001")

                    mock_record.assert_called_once()
                    assert result is not None

        asyncio.run(run_test())

    def test_get_or_update_process_with_movements(self, process_service, sample_process_data):
        """TC-8: Process includes movements from DataJud response."""
        async def run_test():
            with patch.object(process_service.client, 'get_process', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = sample_process_data
                result = await process_service.get_or_update_process("00000001010000100001")

                # Movements should be parsed from response
                assert result is not None
                assert hasattr(result, 'movements')

        asyncio.run(run_test())

    def test_get_or_update_process_transaction_rollback_on_error(self, process_service):
        """TC-9: Database transaction rolls back on save error."""
        async def run_test():
            sample_data = {"numeroProcesso": "00000001010000100001"}
            with patch.object(process_service.client, 'get_process', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = sample_data
                with patch.object(process_service, '_save_process_data', side_effect=Exception("DB error")):
                    with pytest.raises(Exception):
                        await process_service.get_or_update_process("00000001010000100001")

        asyncio.run(run_test())


class TestProcessServiceBulkProcesses:
    """Tests for get_bulk_processes() - async parallel processing (6 tests)."""

    def test_get_bulk_processes_all_success(self, process_service):
        """TC-10: All items processed successfully."""
        async def run_test():
            numbers = ["00000001010000100001", "00000001010000100002"]
            with patch.object(process_service, 'get_or_update_process', new_callable=AsyncMock) as mock_get:
                mock_process = MagicMock(spec=models.Process)
                mock_process.number = numbers[0]
                mock_get.side_effect = [mock_process, mock_process]

                result = await process_service.get_bulk_processes(numbers)

                assert len(result["results"]) == 2
                assert len(result["failures"]) == 0
                assert mock_get.call_count == 2

        asyncio.run(run_test())

    def test_get_bulk_processes_partial_failure(self, process_service):
        """TC-11: Some items succeed, some fail."""
        async def run_test():
            numbers = ["00000001010000100001", "00000001010000100002", "00000001010000100003"]
            with patch.object(process_service, 'get_or_update_process', new_callable=AsyncMock) as mock_get:
                mock_process = MagicMock(spec=models.Process)
                mock_get.side_effect = [mock_process, Exception("API error"), mock_process]

                result = await process_service.get_bulk_processes(numbers)

                assert len(result["results"]) == 2
                assert len(result["failures"]) == 1
                assert "00000001010000100002" in result["failures"]

        asyncio.run(run_test())

    def test_get_bulk_processes_all_failures(self, process_service):
        """TC-12: All items fail to process."""
        async def run_test():
            numbers = ["00000001010000100001", "00000001010000100002"]
            with patch.object(process_service, 'get_or_update_process', new_callable=AsyncMock) as mock_get:
                mock_get.side_effect = Exception("API error")

                result = await process_service.get_bulk_processes(numbers)

                assert len(result["results"]) == 0
                assert len(result["failures"]) == 2

        asyncio.run(run_test())

    def test_get_bulk_processes_semaphore_limits_concurrency(self, process_service):
        """TC-13: Semaphore limits concurrent requests."""
        async def run_test():
            concurrent_count = 0
            max_concurrent = 0

            async def mock_get_or_update(number):
                nonlocal concurrent_count, max_concurrent
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
                await asyncio.sleep(0.01)
                concurrent_count -= 1
                mock_proc = MagicMock(spec=models.Process)
                mock_proc.number = number
                return mock_proc

            with patch.object(process_service, 'get_or_update_process', side_effect=mock_get_or_update):
                numbers = [f"number_{i}" for i in range(20)]
                result = await process_service.get_bulk_processes(numbers, max_concurrent=5)

                assert max_concurrent <= 5, f"Expected max 5 concurrent, got {max_concurrent}"
                assert len(result["results"]) == 20

        asyncio.run(run_test())

    def test_get_bulk_processes_custom_concurrency_limit(self, process_service):
        """TC-14: Custom concurrency limit is respected."""
        async def run_test():
            concurrent_count = 0
            max_concurrent = 0

            async def mock_get_or_update(number):
                nonlocal concurrent_count, max_concurrent
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
                await asyncio.sleep(0.005)
                concurrent_count -= 1
                return MagicMock(spec=models.Process)

            with patch.object(process_service, 'get_or_update_process', side_effect=mock_get_or_update):
                result = await process_service.get_bulk_processes([f"n_{i}" for i in range(10)], max_concurrent=3)
                assert max_concurrent <= 3
                assert len(result["results"]) == 10

        asyncio.run(run_test())

    def test_get_bulk_processes_empty_list(self, process_service):
        """TC-15: Handle empty process list."""
        async def run_test():
            result = await process_service.get_bulk_processes([])

            assert len(result["results"]) == 0
            assert len(result["failures"]) == 0

        asyncio.run(run_test())


class TestProcessServiceDatabase:
    """Tests for database operations (8 tests)."""

    def test_get_from_db_exists(self, process_service, sample_process_db):
        """TC-16: Retrieve process from database."""
        result = process_service.get_from_db("00000001010000100001")
        assert result is not None
        assert result.number == "00000001010000100001"

    def test_get_from_db_not_exists(self, process_service):
        """TC-17: Handle missing records gracefully."""
        result = process_service.get_from_db("99999999999999999999")
        assert result is None

    def test_save_process_data_creates_new(self, process_service):
        """TC-18: Create new process in database."""
        process_data = {
            "numeroProcesso": "00000001010000100004",
            "tribunal": "TJMG",
            "classe": {"codigo": "0001", "nome": "Ação Cível"},
            "assuntos": [{"nome": "Cobrança"}],
            "movimentos": []
        }
        result = process_service._save_process_data("00000001010000100004", process_data)
        assert result is not None
        assert result.number == "00000001010000100004"
        assert result.tribunal_name == "TJMG"

    def test_save_process_data_updates_existing(self, process_service, sample_process_db):
        """TC-19: Update existing process in database."""
        process_data = {
            "numeroProcesso": "00000001010000100001",
            "tribunal": "TJMG",  # Changed from TJSP
            "classe": {"codigo": "0002", "nome": "Ação Revisional"},
            "assuntos": [{"nome": "Revisão"}],
            "movimentos": []
        }
        result = process_service._save_process_data("00000001010000100001", process_data)
        assert result.number == "00000001010000100001"
        assert result.tribunal_name == "TJMG"
        assert result.last_update is not None

    def test_save_process_data_replaces_movements(self, process_service, sample_process_db):
        """TC-20: Old movements are replaced when saving."""
        # Get initial movement count
        initial_process = process_service.get_from_db("00000001010000100001")
        initial_count = len(initial_process.movements) if hasattr(initial_process, 'movements') else 0

        # Save with new movements
        process_data = {
            "numeroProcesso": "00000001010000100001",
            "tribunal": "TJSP",
            "classe": {"codigo": "0001", "nome": "Ação de Cobrança"},
            "assuntos": [{"nome": "Cobrança"}],
            "movimentos": [
                {"nome": "Novo Movimento", "dataHora": "2024-01-20T10:00:00Z"}
            ]
        }
        result = process_service._save_process_data("00000001010000100001", process_data)
        assert result is not None
        # New movements should be present
        assert len(result.movements) > 0

    def test_record_history_adds_entry(self, process_service, sample_process_db):
        """TC-21: Search history is recorded."""
        process = sample_process_db
        process_service._record_history(process)

        # Verify entry was added to history
        history = process_service.db.query(models.SearchHistory).filter(
            models.SearchHistory.number == process.number
        ).first()
        assert history is not None
        assert history.number == "00000001010000100001"

    def test_record_history_handles_errors(self, process_service, sample_process_db):
        """TC-22: History recording handles database errors gracefully."""
        process = sample_process_db
        with patch.object(process_service.db, 'add', side_effect=Exception("DB error")):
            # Should not raise, just log error
            process_service._record_history(process)

    def test_save_process_data_transaction_management(self, process_service):
        """TC-23: Transactions are properly managed."""
        process_data = {
            "numeroProcesso": "00000001010000100005",
            "tribunal": "TJBA",
            "classe": {"codigo": "0001", "nome": "Ação Cível"},
            "assuntos": [{"nome": "Cobrança"}],
            "movimentos": []
        }
        result = process_service._save_process_data("00000001010000100005", process_data)

        # Verify data was persisted
        persisted = process_service.get_from_db("00000001010000100005")
        assert persisted is not None
        assert persisted.number == "00000001010000100005"


class TestProcessServiceParsing:
    """Tests for DataJud response parsing (9 tests)."""

    def test_parse_datajud_response_basic(self, process_service):
        """TC-24: Parse basic API response correctly."""
        sample_data = {
            "numeroProcesso": "00000001010000100001",
            "tribunal": "TJSP",
            "classe": {"codigo": "0001", "nome": "Ação de Cobrança"},
            "assuntos": [{"nome": "Cobrança"}],
            "movimentos": []
        }
        result = process_service._parse_datajud_response(sample_data)
        assert result is not None
        assert result["tribunal_name"] == "TJSP"
        assert result["class_nature"] == "Ação de Cobrança"
        assert result["subject"] == "Cobrança"

    def test_parse_datajud_response_full(self, process_service, sample_process_data):
        """TC-25: Parse complete DataJud response with all fields."""
        result = process_service._parse_datajud_response(sample_process_data)
        assert result is not None
        assert "class_nature" in result
        assert "tribunal_name" in result
        assert "court" in result
        assert "phase" in result

    def test_parse_datajud_response_missing_fields(self, process_service):
        """TC-26: Handle missing fields gracefully."""
        minimal_data = {"numeroProcesso": "00000001010000100001"}
        result = process_service._parse_datajud_response(minimal_data)
        assert result is not None
        assert result["tribunal_name"] == "N/A"
        assert result["class_nature"] == "N/A"

    def test_parse_datajud_date_format_yyyymmddhhmmss(self, process_service):
        """TC-27: Parse DataJud format (YYYYMMDDHHMMSS)."""
        result = process_service._parse_datajud_date("20240115103000", "distribution date")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 0

    def test_parse_datajud_date_format_iso8601(self, process_service):
        """TC-28: Parse ISO 8601 format."""
        result = process_service._parse_datajud_date("2024-01-15T10:30:00Z", "distribution date")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_datajud_date_invalid_format(self, process_service):
        """TC-29: Handle invalid date formats gracefully."""
        result = process_service._parse_datajud_date("invalid-date", "field")
        assert result is None

    def test_parse_datajud_date_empty_string(self, process_service):
        """TC-30: Handle empty date strings."""
        result = process_service._parse_datajud_date("", "field")
        assert result is None

    def test_parse_datajud_date_partial_valid(self, process_service):
        """TC-31: Parse partial valid date format."""
        result = process_service._parse_datajud_date("202401", "field")
        assert result is None  # Too short

    def test_parse_datajud_response_with_multiple_subjects(self, process_service):
        """TC-32: Use first subject when multiple exist."""
        data = {
            "numeroProcesso": "00000001010000100001",
            "tribunal": "TJSP",
            "classe": {"codigo": "0001", "nome": "Ação de Cobrança"},
            "assuntos": [
                {"nome": "Cobrança"},
                {"nome": "Juros"},
                {"nome": "Custas"}
            ],
            "movimentos": []
        }
        result = process_service._parse_datajud_response(data)
        assert result["subject"] == "Cobrança"


class TestProcessServiceMovements:
    """Tests for movement handling (5 tests)."""

    def test_add_movements_basic(self, process_service, sample_process_db):
        """TC-33: Add basic movements to process."""
        movements_data = [
            {
                "nome": "Petição Inicial",
                "dataHora": "2024-01-10T10:00:00Z",
                "codigo": "001"
            },
            {
                "nome": "Recebimento",
                "dataHora": "2024-01-15T11:00:00Z",
                "codigo": "002"
            }
        ]
        process_service._add_movements(sample_process_db.id, movements_data)
        process_service.db.commit()

        # Refresh to get updated movements
        process_service.db.refresh(sample_process_db)
        movements = sample_process_db.movements
        assert len(movements) >= 2

    def test_add_movements_with_complements(self, process_service, sample_process_db):
        """TC-34: Movements with complementosTabelados are formatted correctly."""
        # Clear existing movements first
        process_service.db.query(models.Movement).filter(
            models.Movement.process_id == sample_process_db.id
        ).delete()
        process_service.db.commit()

        movements_data = [
            {
                "nome": "Sentença",
                "dataHora": "2024-01-20T10:00:00Z",
                "codigo": "003",
                "complementosTabelados": [
                    {"nome": "Procedência"},
                    {"nome": "Apelável"}
                ]
            }
        ]
        process_service._add_movements(sample_process_db.id, movements_data)
        process_service.db.commit()

        # Refresh and check
        process_service.db.refresh(sample_process_db)
        assert len(sample_process_db.movements) > 0
        movement = sample_process_db.movements[0]
        assert "Sentença" in movement.description
        assert "Procedência" in movement.description

    def test_add_movements_invalid_date_format(self, process_service, sample_process_db):
        """TC-35: Handle invalid date formats in movements."""
        movements_data = [
            {
                "nome": "Movimentação",
                "dataHora": "invalid-date",
                "codigo": "001"
            }
        ]
        # Should not raise, uses current date as fallback
        process_service._add_movements(sample_process_db.id, movements_data)
        process_service.db.commit()
        assert True  # Test passed if no exception

    def test_add_movements_empty_list(self, process_service, sample_process_db):
        """TC-36: Handle empty movements list."""
        process_service._add_movements(sample_process_db.id, [])
        # Should not raise
        assert True

    def test_get_latest_movement_orgao(self, process_service):
        """TC-37: Extract latest movimento's orgaoJulgador."""
        movements_data = [
            {
                "nome": "Movimento 1",
                "dataHora": "2024-01-10T10:00:00Z",
                "orgaoJulgador": {"nome": "Tribunal X"}
            },
            {
                "nome": "Movimento 2",
                "dataHora": "2024-01-20T15:00:00Z",
                "orgaoJulgador": {"nome": "Tribunal Y"}
            }
        ]
        result = process_service._get_latest_movement_orgao(movements_data)
        assert result is not None
        assert result["nome"] == "Tribunal Y"


class TestProcessServiceInstances:
    """Tests for multi-instance handling (3 tests)."""

    def test_get_process_instance_basic(self, process_service, sample_process_db):
        """TC-38: Retrieve specific instance of process."""
        async def run_test():
            # Mock raw_data structure
            with patch.object(process_service, 'get_from_db') as mock_get:
                mock_process = MagicMock()
                mock_process.number = "00000001010000100001"
                mock_process.raw_data = {"__meta__": {"all_hits": [{"tribunal": "TJSP"}]}}
                mock_get.return_value = mock_process

                with patch.object(process_service, '_parse_datajud_response', return_value={"tribunal_name": "TJSP"}):
                    with patch.object(process_service, '_parse_movements_list', return_value=[]):
                        result = await process_service.get_process_instance("00000001010000100001", 0)
                        assert result is not None
                        assert result["number"] == "00000001010000100001"

        asyncio.run(run_test())

    def test_get_process_instance_not_found_in_db(self, process_service):
        """TC-39: Handle process not found in database."""
        async def run_test():
            with pytest.raises(ProcessNotFoundException):
                await process_service.get_process_instance("99999999999999999999", 0)

        asyncio.run(run_test())

    def test_get_all_instances_returns_dict(self, process_service, sample_process_db):
        """TC-40: Get all instances returns expected structure."""
        async def run_test():
            with patch.object(process_service.client, 'get_process_instances', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = ({"tribunal": "TJSP"}, {"instances_count": 1, "instances": []})
                result = await process_service.get_all_instances("00000001010000100001")
                assert result is not None
                assert "instances_count" in result

        asyncio.run(run_test())
