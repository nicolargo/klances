def test_status_ready(client):
    resp = client.get("/api/1/status")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["api_version"] == "1"
    assert data["klances_version"] != ""


def test_docs_available(client):
    resp = client.get("/api/1/docs")
    assert resp.status_code == 200


def test_openapi_json_available(client):
    resp = client.get("/api/1/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert schema["info"]["title"] == "Klances API"
