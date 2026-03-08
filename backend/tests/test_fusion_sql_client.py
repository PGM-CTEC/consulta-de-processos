"""Tests for FusionSQLClient — SQL Server direct access."""
import pytest
from unittest.mock import MagicMock, patch
from backend.services.fusion_sql_client import FusionSQLClient, FusionSQLException


class TestFusionSQLClientAvailability:
    """Tests for availability check."""

    def test_is_available_false_sem_host(self):
        """TC-1: is_available() retorna False sem host configurado."""
        client = FusionSQLClient(host="", port=1433, database="db", user="u", password="p")
        assert client.is_available() is False

    def test_is_available_false_sem_database(self):
        """TC-2: is_available() retorna False sem database configurado."""
        client = FusionSQLClient(host="server", port=1433, database="", user="u", password="p")
        assert client.is_available() is False

    def test_is_available_true_com_credenciais_completas(self):
        """TC-3: is_available() retorna True com todas as credenciais."""
        client = FusionSQLClient(host="server", port=1433, database="db", user="u", password="p")
        assert client.is_available() is True


class TestFusionSQLClientConnection:
    """Tests for connection string building."""

    def test_connection_string_correto(self):
        """TC-4: Connection string segue formato pyodbc SQL Server."""
        client = FusionSQLClient(host="10.0.0.1", port=1433, database="FusionDB", user="sa", password="pass")
        cs = client._build_connection_string()
        assert "10.0.0.1" in cs
        assert "FusionDB" in cs
        assert "1433" in cs
