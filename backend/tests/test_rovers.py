def test_create_and_list_rovers(client):
    created = client.post("/api/rovers", json={"name": "rover-01", "battery": 80})
    assert created.status_code == 201
    assert created.json()["online"] is False
    listing = client.get("/api/rovers").json()
    assert [r["name"] for r in listing] == ["rover-01"]


def test_duplicate_rover_name_rejected(client, rover):
    response = client.post("/api/rovers", json={"name": "rover-01"})
    assert response.status_code == 409


def test_update_and_delete_rover(client, rover):
    updated = client.put(f"/api/rovers/{rover['id']}", json={"status": "CHARGING"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "CHARGING"
    assert client.delete(f"/api/rovers/{rover['id']}").status_code == 204
    assert client.get(f"/api/rovers/{rover['id']}").status_code == 404


def test_battery_out_of_range_rejected(client):
    response = client.post("/api/rovers", json={"name": "bad", "battery": 150})
    assert response.status_code == 422


def test_telemetry_registers_and_marks_online(client):
    payload = {"rover": "rover-09", "x": 12.5, "y": 40, "heading": 90, "battery": 71, "status": "PATROLLING"}
    response = client.post("/api/telemetry", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["online"] is True
    assert body["x"] == 12.5
    assert len(client.get("/api/rovers").json()) == 1


def test_telemetry_requires_token_when_configured(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "ingest_token", "secret")
    payload = {"rover": "rover-01", "x": 0, "y": 0, "battery": 50}
    assert client.post("/api/telemetry", json=payload).status_code == 401
    ok = client.post("/api/telemetry", json=payload, headers={"X-Rover-Token": "secret"})
    assert ok.status_code == 200
