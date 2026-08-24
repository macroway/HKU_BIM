from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.models.store import clear_models

client = TestClient(app)


def setup_function():
    clear_models()


def test_list_samples():
    response = client.get("/api/models/samples")
    assert response.status_code == 200
    data = response.json()
    assert any(s["id"] == "collision_positive" for s in data)
    assert any(s["id"] == "building_l1" for s in data)
    assert any(s["id"] == "demo/demo-collision" for s in data)
    assert any(s["id"] == "demo/building-l1" for s in data)
    ids = {s["id"] for s in data}
    assert "attrs_missing" not in ids
    assert "attrs_ok" not in ids


def test_select_hidden_sample_still_works():
    sel = client.post("/api/models/select/attrs_missing")
    assert sel.status_code == 200


def test_select_sample_and_chat():
    sel = client.post("/api/models/select/collision_positive")
    assert sel.status_code == 200
    model_id = sel.json()["model_id"]

    chat = client.post("/api/chat", json={"model_id": model_id, "message": "帮我查碰撞"})
    assert chat.status_code == 200
    body = chat.json()
    assert body["did_run_tools"] is True
    assert "collision" in body["results"]
    assert len(body["tool_traces"]) >= 1


def test_select_demo_ifc_sample():
    sel = client.post("/api/models/select/demo/demo-collision")
    assert sel.status_code == 200
    assert sel.json()["format"] == "ifc"
    model_id = sel.json()["model_id"]

    chat = client.post("/api/chat", json={"model_id": model_id, "message": "帮我查碰撞"})
    assert chat.status_code == 200
    assert chat.json()["did_run_tools"] is True
    assert len(chat.json()["results"]["collision"]["pairs"]) >= 1


def test_chat_without_model_404():
    response = client.post("/api/chat", json={"model_id": "missing", "message": "查碰撞"})
    assert response.status_code == 404


def test_upload_json_sample():
    path = Path(__file__).resolve().parent.parent / "test_samples/collision_negative.json"
    with path.open("rb") as f:
        response = client.post(
            "/api/models/upload",
            files={"file": ("collision_negative.json", f, "application/json")},
        )
    assert response.status_code == 200
    model_id = response.json()["model_id"]

    chat = client.post("/api/chat", json={"model_id": model_id, "message": "查碰撞"})
    assert chat.status_code == 200
    assert chat.json()["results"]["collision"]["pairs"] == []


def test_index_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "CheckBIM Agent" in response.text
    assert "plan-canvas" in response.text


def test_model_preview():
    sel = client.post("/api/models/select/collision_positive")
    assert sel.status_code == 200
    model_id = sel.json()["model_id"]
    preview = client.get(f"/api/models/{model_id}/preview")
    assert preview.status_code == 200
    data = preview.json()
    assert data["element_count"] >= 1
    assert len(data["elements"]) >= 1
    assert "aabb" in data["elements"][0]


def test_llm_status_offline_by_default_in_tests():
    response = client.get("/api/llm/status")
    assert response.status_code == 200
    body = response.json()
    assert "provider" in body
    assert "planner_label" in body
