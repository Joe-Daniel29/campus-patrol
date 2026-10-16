def test_event_ingest_and_filter(client, rover, zone):
    body = {"rover": "rover-01", "zone": "Library", "type": "door_left_open", "severity": "WARNING"}
    created = client.post("/api/events", json=body)
    assert created.status_code == 201
    assert created.json()["zone_name"] == "Library"
    client.post("/api/events", json={"rover": "rover-01", "type": "crowd_gathering"})
    warnings = client.get("/api/events", params={"severity": "WARNING"}).json()
    assert len(warnings) == 1
    assert len(client.get("/api/events").json()) == 2


def test_event_from_unknown_rover_rejected(client):
    response = client.post("/api/events", json={"rover": "ghost", "type": "x"})
    assert response.status_code == 404


def test_incident_lifecycle(client, zone):
    created = client.post(
        "/api/incidents", json={"title": "Door open", "severity": "WARNING", "zone_id": zone["id"]}
    )
    assert created.status_code == 201
    incident = created.json()
    assert incident["status"] == "OPEN"
    assert incident["zone_name"] == "Library"

    acked = client.put(f"/api/incidents/{incident['id']}", json={"status": "ACKNOWLEDGED", "assignee": "desk"})
    assert acked.json()["status"] == "ACKNOWLEDGED"
    assert acked.json()["assignee"] == "desk"

    open_only = client.get("/api/incidents", params={"status": "OPEN"}).json()
    assert open_only == []

    assert client.delete(f"/api/incidents/{incident['id']}").status_code == 204
    assert client.get(f"/api/incidents/{incident['id']}").status_code == 404


def test_invalid_incident_status_rejected(client, zone):
    created = client.post("/api/incidents", json={"title": "x"}).json()
    response = client.put(f"/api/incidents/{created['id']}", json={"status": "BOGUS"})
    assert response.status_code == 422


def test_stats_reflect_fleet_and_incidents(client):
    client.post("/api/telemetry", json={"rover": "rover-01", "x": 0, "y": 0, "battery": 90})
    client.post("/api/rovers", json={"name": "rover-02"})
    client.post("/api/events", json={"rover": "rover-01", "type": "sos_button", "severity": "CRITICAL"})
    client.post("/api/incidents", json={"title": "SOS"})
    stats = client.get("/api/stats").json()
    assert stats["rovers_total"] == 2
    assert stats["rovers_online"] == 1
    assert stats["incidents_open"] == 1
    assert stats["events_last_hour"] == 1
    assert stats["events_by_type"] == {"sos_button": 1}
