import pytest

from ..services.datajud import DataJudClient


def test_select_latest_instance_by_movement():
    client = DataJudClient()
    hits = [
        {
            "_source": {
                "grau": "G1",
                "movimentos": [
                    {"dataHora": "2020-01-01T00:00:00Z"}
                ],
            }
        },
        {
            "_source": {
                "grau": "G2",
                "movimentos": [
                    {"dataHora": "2021-05-10T12:30:00Z"}
                ],
            }
        },
    ]

    selected, meta = client._select_latest_instance(hits)

    assert selected.get("grau") == "G2"
    assert meta is not None
    assert meta.get("instances_count") == 2


def test_select_latest_instance_by_timestamp_fallback():
    client = DataJudClient()
    hits = [
        {
            "_source": {
                "grau": "G1",
                "dataHoraUltimaAtualizacao": "2020-01-01T00:00:00Z",
                "movimentos": [],
            }
        },
        {
            "_source": {
                "grau": "G2",
                "dataHoraUltimaAtualizacao": "2022-02-02T10:00:00Z",
                "movimentos": [],
            }
        },
    ]

    selected, meta = client._select_latest_instance(hits)

    assert selected.get("grau") == "G2"
    assert meta is not None
    assert meta.get("instances_count") == 2
