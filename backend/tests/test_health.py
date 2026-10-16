def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_metrics_exposes_fleet_gauges(client, rover):
    body = client.get("/metrics").text
    assert "patrol_rovers_total 1.0" in body
    assert "patrol_rovers_online" in body
    assert "http_requests_total" in body
