import asyncio

from ..services.process_service import ProcessService


def test_parse_datajud_response_adds_phase_source_to_meta():
    service = ProcessService(db=None)
    payload = {
        "classe": {"codigo": 1728, "nome": "Apelação / Remessa Necessária"},
        "tribunal": "TJRJ",
        "grau": "G2",
        "orgaoJulgador": {"nome": "13 CÂMARA CÍVEL"},
        "movimentos": [{"codigo": 22, "nome": "Baixa Definitiva", "dataHora": "2021-10-19T13:44:00Z"}],
        "__meta__": {
            "selected_index": 0,
            "instances": [{"grau": "G2"}],
        },
    }

    parsed = service._parse_datajud_response(payload)
    meta = (parsed.get("raw_data") or {}).get("__meta__", {})
    assert meta.get("phase_source_instance_index") == 0
    assert meta.get("phase_source_grau") == "G2"


def test_get_all_instances_single_instance_uses_raw_summary_fields(monkeypatch):
    service = ProcessService(db=None)
    raw_single_hit = {
        "grau": "G2",
        "tribunal": "TJRJ",
        "orgaoJulgador": {"nome": "13 CÂMARA CÍVEL"},
        "dataHoraUltimaAtualizacao": "2022-07-29T22:04:43.766Z",
        "movimentos": [{"dataHora": "2021-10-19T13:44:00Z"}],
    }

    async def fake_get_process_instances(_number):
        return raw_single_hit, {"instances_count": 1}

    monkeypatch.setattr(service.client, "get_process_instances", fake_get_process_instances)

    result = asyncio.run(service.get_all_instances("0435756-80.2012.8.19.0001"))
    assert result.get("instances_count") == 1
    first = result.get("instances", [])[0]
    assert first.get("grau") == "G2"
    assert first.get("tribunal") == "TJRJ"
    assert first.get("orgao_julgador") == "13 CÂMARA CÍVEL"
    assert first.get("latest_movement_at") is not None
    assert first.get("updated_at") is not None
