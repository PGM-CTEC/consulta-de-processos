import asyncio

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


def test_get_process_instances_expands_aliases_and_merges_classes(monkeypatch):
    client = DataJudClient()
    calls = []

    data_by_alias = {
        "api_publica_tjrj": [],
        "api_publica_tjrj_1g": [
            {
                "numeroProcesso": "04357568020128190001",
                "grau": "G1",
                "tribunal": "TJRJ",
                "classe": {"nome": "Procedimento Comum Cível"},
                "orgaoJulgador": {"codigo": 1001, "nome": "1ª Vara Cível"},
                "movimentos": [{"dataHora": "2019-03-01T10:00:00Z"}],
            }
        ],
        "api_publica_tjrj_2g": [
            {
                "numeroProcesso": "04357568020128190001",
                "grau": "G2",
                "tribunal": "TJRJ",
                "classe": {"nome": "Apelação / Remessa Necessária"},
                "orgaoJulgador": {"codigo": 16611, "nome": "13 CÂMARA CÍVEL"},
                "movimentos": [{"dataHora": "2021-10-19T13:44:00Z"}],
            }
        ],
        "api_publica_stj": [
            {
                "numeroProcesso": "04357568020128190001",
                "grau": "SUP",
                "tribunal": "STJ",
                "classe": {"nome": "Recurso Especial"},
                "orgaoJulgador": {"codigo": 1, "nome": "2ª Turma"},
                "movimentos": [{"dataHora": "2022-01-20T09:00:00Z"}],
            }
        ],
        "api_publica_stf": [],
        "api_publica_tst": [],
    }

    async def fake_search_index(alias, clean_number):
        calls.append(alias)
        return data_by_alias.get(alias, [])

    monkeypatch.setattr(client, "_search_index", fake_search_index)

    selected, meta = asyncio.run(client.get_process_instances("0435756-80.2012.8.19.0001"))

    assert selected is not None
    assert selected.get("tribunal") == "STJ"
    assert meta is not None
    assert meta.get("instances_count") == 3
    assert meta.get("source_limited") is False
    assert meta.get("missing_expected_instances") == []
    assert "api_publica_tjrj_1g" in calls
    assert "api_publica_tjrj_2g" in calls
    assert "api_publica_stj" in calls
    assert "api_publica_stf" in calls
    assert "api_publica_tst" in calls

    all_hits = meta.get("all_hits", [])
    tjrj_classes = {(h.get("classe") or {}).get("nome") for h in all_hits if h.get("tribunal") == "TJRJ"}
    assert "Procedimento Comum Cível" in tjrj_classes
    assert "Apelação / Remessa Necessária" in tjrj_classes


def test_get_process_instances_only_queries_superior_when_g2_exists(monkeypatch):
    client = DataJudClient()
    calls = []

    data_by_alias = {
        "api_publica_tjrj": [],
        "api_publica_tjrj_1g": [
            {
                "numeroProcesso": "04357568020128190001",
                "grau": "G1",
                "tribunal": "TJRJ",
                "classe": {"nome": "Procedimento Comum Cível"},
                "orgaoJulgador": {"codigo": 1001, "nome": "1ª Vara Cível"},
                "movimentos": [{"dataHora": "2019-03-01T10:00:00Z"}],
            }
        ],
        "api_publica_tjrj_2g": [],
        "api_publica_cnj": [],
    }

    async def fake_search_index(alias, clean_number):
        calls.append(alias)
        return data_by_alias.get(alias, [])

    monkeypatch.setattr(client, "_search_index", fake_search_index)

    selected, meta = asyncio.run(client.get_process_instances("0435756-80.2012.8.19.0001"))

    assert selected is not None
    assert selected.get("grau") == "G1"
    assert meta is not None
    assert meta.get("instances_count") == 1
    assert meta.get("source_limited") is False
    assert meta.get("missing_expected_instances") == []
    assert "api_publica_cnj" in calls
    assert "api_publica_stj" not in calls
    assert "api_publica_stf" not in calls
    assert "api_publica_tst" not in calls


def test_get_process_instances_flags_source_limited_when_only_g2(monkeypatch):
    client = DataJudClient()

    data_by_alias = {
        "api_publica_tjrj": [
            {
                "numeroProcesso": "04357568020128190001",
                "grau": "G2",
                "tribunal": "TJRJ",
                "classe": {"nome": "Apelação / Remessa Necessária"},
                "orgaoJulgador": {"codigo": 16611, "nome": "13 CÂMARA CÍVEL"},
                "movimentos": [{"dataHora": "2021-10-19T13:44:00Z"}],
            }
        ],
        "api_publica_tjrj_1g": [],
        "api_publica_tjrj_2g": [],
        "api_publica_cnj": [],
        "api_publica_tst": [],
        "api_publica_stj": [],
        "api_publica_stf": [],
    }

    async def fake_search_index(alias, clean_number):
        return data_by_alias.get(alias, [])

    monkeypatch.setattr(client, "_search_index", fake_search_index)

    selected, meta = asyncio.run(client.get_process_instances("0435756-80.2012.8.19.0001"))

    assert selected is not None
    assert selected.get("grau") == "G2"
    assert meta is not None
    assert meta.get("source_limited") is True
    assert meta.get("missing_expected_instances") == ["G1"]
    assert "não retornou" in (meta.get("diagnostic_note") or "")
