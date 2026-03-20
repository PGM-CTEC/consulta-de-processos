"""
Comprehensive Tests for DataJud Client - Phase 7 Coverage Push (75%+ Target)
Story: REM-017 - Backend Unit Tests (Target: 75%+ Coverage)

Test Categories:
- Tribunal alias determination (all judicial segments)
- Date/time parsing and sorting
- Instance selection and summarization
- HTTP error handling (401, 404, 429, 500+)
- Retry logic with network failures
- Multiple tribunal queries and merging
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest

from backend.services.datajud import DataJudClient
from backend.exceptions import DataJudAPIException, InvalidProcessNumberException


class TestTribunalAliasMapping:
    """Tests for _get_tribunal_alias method (15 tests)."""

    def setup_method(self):
        """Create client instance for each test."""
        self.client = DataJudClient()

    def test_alias_state_court_tjrj(self):
        """TC-1: J=8 (State Court) TR=19 maps to tjrj."""
        # Format: NNNNNNN DD AAAA J TR OOOO
        # Using:  0001745 64 1989 8 19 0002
        alias = self.client._get_tribunal_alias("00017456419898190002")
        assert alias == "api_publica_tjrj"

    def test_alias_state_court_tjsp(self):
        """TC-2: J=8 TR=25 maps to tjsp."""
        number = "00017456419898250002"  # J=8, TR=25
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_tjsp"

    def test_alias_state_court_tjmg(self):
        """TC-3: J=8 TR=13 maps to tjmg."""
        number = "00017456419898130002"  # J=8, TR=13
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_tjmg"

    def test_alias_unknown_state_court_fallback(self):
        """TC-4: J=8 with unknown TR falls back to CNJ."""
        number = "00017456419898990002"  # J=8, TR=99 (invalid)
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_cnj"

    def test_alias_trf_valid(self):
        """TC-5: J=4 (TRF) TR=01 maps to trf1."""
        number = "00017456419894010002"  # J=4, TR=01
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_trf1"

    def test_alias_trf5(self):
        """TC-6: J=4 TR=05 maps to trf5."""
        number = "00017456419894050002"  # J=4, TR=05
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_trf5"

    def test_alias_trf_invalid_raises(self):
        """TC-7: J=4 TR=06 (out of range) raises exception."""
        number = "00017456419894060002"  # J=4, TR=06 (invalid, TRF only 1-5)
        with pytest.raises(DataJudAPIException) as exc_info:
            self.client._get_tribunal_alias(number)
        assert "TRF inválido" in str(exc_info.value)

    def test_alias_trt_valid(self):
        """TC-8: J=5 (TRT) TR=01 maps to trt1."""
        number = "00017456419895010002"  # J=5, TR=01
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_trt1"

    def test_alias_trt24(self):
        """TC-9: J=5 TR=24 maps to trt24."""
        number = "00017456419895240002"  # J=5, TR=24
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_trt24"

    def test_alias_trt_invalid_raises(self):
        """TC-10: J=5 TR=25 (out of range) raises exception."""
        number = "00017456419895250002"  # J=5, TR=25 (invalid, TRT only 1-24)
        with pytest.raises(DataJudAPIException) as exc_info:
            self.client._get_tribunal_alias(number)
        assert "TRT inválido" in str(exc_info.value)

    def test_alias_tre_valid(self):
        """TC-11: J=3 (TRE) TR=19 maps to tre19."""
        number = "00017456419893190002"  # J=3, TR=19
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_tre19"

    def test_alias_tre_unknown_fallback(self):
        """TC-12: J=3 with unknown TR falls back to CNJ."""
        number = "00017456419893990002"  # J=3, TR=99 (invalid)
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_cnj"

    def test_alias_stm_valid(self):
        """TC-13: J=6 TR=00 maps to STM."""
        number = "00017456419896000002"  # J=6, TR=00
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_stm"

    def test_alias_tjm_valid(self):
        """TC-14: J=6 TR=01 maps to tjm01."""
        number = "00017456419896010002"  # J=6, TR=01
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_tjm01"

    def test_alias_unknown_segment_fallback(self):
        """TC-15: Unknown J segment falls back to CNJ."""
        number = "00017456419899190002"  # J=9 (unknown)
        alias = self.client._get_tribunal_alias(number)
        assert alias == "api_publica_cnj"

    def test_alias_invalid_length_raises(self):
        """TC-16: Process number with wrong length raises exception."""
        with pytest.raises(InvalidProcessNumberException):
            self.client._get_tribunal_alias("123456789")  # Only 9 digits


class TestDateTimeUtilities:
    """Tests for datetime parsing and sorting (8 tests)."""

    def setup_method(self):
        """Create client instance for each test."""
        self.client = DataJudClient()

    def test_parse_iso_datetime_valid(self):
        """TC-17: Parse valid ISO datetime."""
        result = self.client._parse_iso_datetime("2024-01-15T10:30:00.000Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_iso_datetime_none(self):
        """TC-18: Parse None returns None."""
        result = self.client._parse_iso_datetime(None)
        assert result is None

    def test_parse_iso_datetime_empty_string(self):
        """TC-19: Parse empty string returns None."""
        result = self.client._parse_iso_datetime("")
        assert result is None

    def test_parse_iso_datetime_non_string(self):
        """TC-20: Parse non-string returns None."""
        result = self.client._parse_iso_datetime(12345)
        assert result is None

    def test_parse_iso_datetime_invalid_format(self):
        """TC-21: Parse invalid format returns None."""
        result = self.client._parse_iso_datetime("invalid-date")
        assert result is None

    def test_latest_movement_datetime_with_movements(self):
        """TC-22: Find latest movement from list."""
        movements = [
            {"dataHora": "2024-01-15T10:00:00.000Z"},
            {"dataHora": "2024-02-20T15:30:00.000Z"},  # Latest
            {"dataHora": "2024-01-10T08:00:00.000Z"},
        ]
        result = self.client._latest_movement_datetime(movements)
        assert result is not None
        assert result.month == 2
        assert result.day == 20

    def test_latest_movement_datetime_empty_list(self):
        """TC-23: Empty movements returns None."""
        result = self.client._latest_movement_datetime([])
        assert result is None

    def test_latest_movement_datetime_no_valid_dates(self):
        """TC-24: Movements without valid dates returns None."""
        movements = [
            {"dataHora": None},
            {"dataHora": "invalid"},
            {"other_field": "value"},
        ]
        result = self.client._latest_movement_datetime(movements)
        assert result is None


class TestInstanceSelection:
    """Tests for instance selection and summarization (10 tests)."""

    def setup_method(self):
        """Create client instance for each test."""
        self.client = DataJudClient()

    def test_instance_sort_key_latest_movement(self):
        """TC-25: Sort key uses latest movement when available."""
        source = {
            "movimentos": [{"dataHora": "2024-02-15T10:00:00.000Z"}],
            "dataHoraUltimaAtualizacao": "2024-01-01T00:00:00.000Z",
        }
        result = self.client._instance_sort_key(source)
        assert result.month == 2
        assert result.day == 15

    def test_instance_sort_key_fallback_to_updated_at(self):
        """TC-26: Sort key falls back to updated_at when no movements."""
        source = {
            "movimentos": [],
            "dataHoraUltimaAtualizacao": "2024-01-20T10:00:00.000Z",
        }
        result = self.client._instance_sort_key(source)
        assert result.month == 1
        assert result.day == 20

    def test_instance_sort_key_fallback_to_timestamp(self):
        """TC-27: Sort key falls back to @timestamp."""
        source = {
            "@timestamp": "2024-03-10T10:00:00.000Z",
        }
        result = self.client._instance_sort_key(source)
        assert result.month == 3

    def test_instance_sort_key_no_dates_returns_min(self):
        """TC-28: Sort key returns datetime.min when no dates."""
        source = {}
        result = self.client._instance_sort_key(source)
        assert result == datetime.min

    def test_summarize_instance_complete(self):
        """TC-29: Summarize instance with all fields."""
        source = {
            "grau": "G2",
            "tribunal": "TJRJ",
            "orgaoJulgador": {"nome": "1ª Câmara Cível", "codigo": "001"},
            "movimentos": [{"dataHora": "2024-01-15T10:00:00.000Z"}],
            "dataHoraUltimaAtualizacao": "2024-01-16T00:00:00.000Z",
        }
        result = self.client._summarize_instance(source)
        assert result["grau"] == "G2"
        assert result["tribunal"] == "TJRJ"
        assert result["orgao_julgador"] == "1ª Câmara Cível"
        assert result["latest_movement_at"] is not None
        assert result["updated_at"] is not None

    def test_summarize_instance_minimal(self):
        """TC-30: Summarize instance with minimal fields."""
        source = {"grau": "G1"}
        result = self.client._summarize_instance(source)
        assert result["grau"] == "G1"
        assert result["latest_movement_at"] is None

    def test_instance_key_generation(self):
        """TC-31: Generate unique instance key."""
        source = {
            "grau": "G2",
            "tribunal": "TJRJ",
            "orgaoJulgador": {"codigo": "001"},
        }
        result = self.client._instance_key(source)
        assert result == "G2|TJRJ|001"

    def test_instance_key_with_orgao_nome(self):
        """TC-32: Instance key uses orgao nome when codigo missing."""
        source = {
            "grau": "G1",
            "tribunal": "TJSP",
            "orgaoJulgador": {"nome": "1ª Vara Cível"},
        }
        result = self.client._instance_key(source)
        assert "1ª Vara Cível" in result

    def test_select_latest_instance_single_hit(self):
        """TC-33: Select single hit returns it."""
        hits = [
            {
                "_source": {
                    "grau": "G1",
                    "tribunal": "TJRJ",
                    "movimentos": [{"dataHora": "2024-01-15T10:00:00.000Z"}],
                }
            }
        ]
        selected, meta = self.client._select_latest_instance(hits)
        assert selected["grau"] == "G1"
        assert meta["instances_count"] == 1
        assert meta["selected_by"] == "single_hit"

    def test_select_latest_instance_multiple_hits(self):
        """TC-34: Select latest from multiple hits."""
        hits = [
            {
                "_source": {
                    "grau": "G1",
                    "movimentos": [{"dataHora": "2024-01-15T10:00:00.000Z"}],
                }
            },
            {
                "_source": {
                    "grau": "G2",
                    "movimentos": [{"dataHora": "2024-02-20T15:00:00.000Z"}],  # Latest
                }
            },
        ]
        selected, meta = self.client._select_latest_instance(hits)
        assert selected["grau"] == "G2"
        assert meta["instances_count"] == 2
        assert meta["selected_by"] == "latest_movement_or_timestamp"
        assert meta["selected_index"] == 1


class TestHTTPErrorHandling:
    """Tests for HTTP error handling (8 tests)."""

    def setup_method(self):
        """Create client instance for each test."""
        self.client = DataJudClient()

    @patch("httpx.AsyncClient.post")
    def test_search_index_404_returns_empty(self, mock_post):
        """TC-35: 404 response returns empty list."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        result = asyncio.run(
            self.client._search_index("api_publica_tjrj", "00017456419898190002")
        )
        assert result == []

    @patch("httpx.AsyncClient.post")
    def test_search_index_401_raises_auth_error(self, mock_post):
        """TC-36: 401 response raises authentication error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with pytest.raises(DataJudAPIException) as exc_info:
            asyncio.run(
                self.client._search_index("api_publica_tjrj", "00017456419898190002")
            )
        assert "autenticação" in str(exc_info.value)

    @patch("httpx.AsyncClient.post")
    def test_search_index_429_raises_rate_limit(self, mock_post):
        """TC-37: 429 response raises rate limit error."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        with pytest.raises(DataJudAPIException) as exc_info:
            asyncio.run(
                self.client._search_index("api_publica_tjrj", "00017456419898190002")
            )
        assert "Limite de requisições" in str(exc_info.value)

    @patch("httpx.AsyncClient.post")
    def test_search_index_500_raises_server_error(self, mock_post):
        """TC-38: 500+ response raises server error."""
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_post.return_value = mock_response

        with pytest.raises(DataJudAPIException) as exc_info:
            asyncio.run(
                self.client._search_index("api_publica_tjrj", "00017456419898190002")
            )
        assert "temporariamente indisponível" in str(exc_info.value)

    @patch("httpx.AsyncClient.post")
    def test_search_index_200_success(self, mock_post):
        """TC-39: 200 response with valid JSON returns hits."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "numeroProcesso": "00017456419898190002",
                            "grau": "G1",
                        }
                    }
                ]
            }
        }
        mock_post.return_value = mock_response

        result = asyncio.run(
            self.client._search_index("api_publica_tjrj", "00017456419898190002")
        )
        assert len(result) == 1
        assert result[0]["numeroProcesso"] == "00017456419898190002"

    @patch("httpx.AsyncClient.post")
    def test_search_index_invalid_json_raises(self, mock_post):
        """TC-40: Invalid JSON response raises exception."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        with pytest.raises(DataJudAPIException) as exc_info:
            asyncio.run(
                self.client._search_index("api_publica_tjrj", "00017456419898190002")
            )
        assert "Resposta inválida" in str(exc_info.value)

    @patch("httpx.AsyncClient.post")
    def test_search_index_unexpected_status_raises(self, mock_post):
        """TC-41: Unexpected status code raises exception."""
        mock_response = MagicMock()
        mock_response.status_code = 418  # I'm a teapot
        mock_response.text = "Teapot error"
        mock_post.return_value = mock_response

        with pytest.raises(DataJudAPIException) as exc_info:
            asyncio.run(
                self.client._search_index("api_publica_tjrj", "00017456419898190002")
            )
        assert "código 418" in str(exc_info.value)

    @patch("httpx.AsyncClient.post")
    def test_search_index_network_error_raises(self, mock_post):
        """TC-42: Network error raises exception."""
        mock_post.side_effect = httpx.ConnectError("Connection failed")

        with pytest.raises(httpx.ConnectError):
            asyncio.run(
                self.client._search_index("api_publica_tjrj", "00017456419898190002")
            )


class TestGetProcessMethods:
    """Tests for public get_process methods (5 tests)."""

    def setup_method(self):
        """Create client instance for each test."""
        self.client = DataJudClient()

    @patch.object(DataJudClient, "get_process_instances")
    def test_get_process_with_result(self, mock_instances):
        """TC-43: get_process returns process with metadata."""
        selected = {"numeroProcesso": "00017456419898190002", "grau": "G1"}
        meta = {"instances_count": 1}
        mock_instances.return_value = (selected, meta)

        result = asyncio.run(self.client.get_process("00017456419898190002"))
        assert result is not None
        assert result["numeroProcesso"] == "00017456419898190002"
        assert "__meta__" in result
        assert result["__meta__"]["instances_count"] == 1

    @patch.object(DataJudClient, "get_process_instances")
    def test_get_process_not_found(self, mock_instances):
        """TC-44: get_process returns None when not found."""
        mock_instances.return_value = (None, None)

        result = asyncio.run(self.client.get_process("99999999999999999999"))
        assert result is None

    @patch.object(DataJudClient, "_search_aliases")
    @patch.object(DataJudClient, "_get_tribunal_alias")
    @patch.object(DataJudClient, "_expand_aliases_for_instances")
    def test_get_process_instances_success(
        self, mock_expand, mock_alias, mock_search
    ):
        """TC-45: get_process_instances returns selected instance."""
        mock_alias.return_value = "api_publica_tjrj"
        mock_expand.return_value = ["api_publica_tjrj"]
        mock_search.return_value = [
            {
                "_source": {
                    "numeroProcesso": "00017456419898190002",
                    "grau": "G1",
                    "movimentos": [{"dataHora": "2024-01-15T10:00:00.000Z"}],
                }
            }
        ]

        selected, meta = asyncio.run(
            self.client.get_process_instances("00017456419898190002")
        )
        assert selected is not None
        assert selected["numeroProcesso"] == "00017456419898190002"
        assert meta is not None
        assert "aliases_queried" in meta

    @patch.object(DataJudClient, "_get_tribunal_alias")
    def test_get_process_instances_invalid_number_raises(self, mock_alias):
        """TC-46: get_process_instances raises on invalid number."""
        mock_alias.side_effect = InvalidProcessNumberException("Invalid format")

        with pytest.raises(InvalidProcessNumberException):
            asyncio.run(self.client.get_process_instances("invalid"))

    @patch.object(DataJudClient, "_search_aliases")
    @patch.object(DataJudClient, "_get_tribunal_alias")
    @patch.object(DataJudClient, "_expand_aliases_for_instances")
    def test_get_process_instances_not_found_returns_none(
        self, mock_expand, mock_alias, mock_search
    ):
        """TC-47: get_process_instances returns None when not found."""
        mock_alias.return_value = "api_publica_tjrj"
        mock_expand.return_value = ["api_publica_tjrj"]
        mock_search.return_value = []  # No hits

        selected, meta = asyncio.run(
            self.client.get_process_instances("00017456419898190002")
        )
        assert selected is None
        assert meta is None
