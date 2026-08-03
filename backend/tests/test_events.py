def test_create_event(client):
    payload = {
        "user_id": "user_test",
        "event_type": "signup",
        "event_time": "2026-08-01T10:00:00Z",
        "priority": "HIGH",
    }
    response = client.post("/api/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "user_test"
    assert data["priority"] == "HIGH"
    assert "id" in data


def test_list_events(client):
    payload = {
        "user_id": "user_list",
        "event_type": "cart_abandon",
        "event_time": "2026-08-01T10:00:00Z",
        "priority": "MEDIUM",
    }
    client.post("/api/events", json=payload)
    client.post("/api/events", json=payload)

    response = client.get("/api/events", params={"user_id": "user_list"})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_event_by_id(client):
    payload = {
        "user_id": "user_get",
        "event_type": "renewal_due",
        "event_time": "2026-08-01T10:00:00Z",
        "priority": "LOW",
    }
    created = client.post("/api/events", json=payload).json()

    response = client.get(f"/api/events/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_event_not_found(client):
    import uuid

    response = client.get(f"/api/events/{uuid.uuid4()}")
    assert response.status_code == 404
