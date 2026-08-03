from datetime import datetime, timedelta, timezone


def _create_nudge(client, user_id, channel, status, hours_ago, hour_of_day):
    sent_time = (datetime.now(timezone.utc) - timedelta(days=hours_ago)).replace(
        hour=hour_of_day, minute=0, second=0, microsecond=0
    )
    payload = {
        "user_id": user_id,
        "channel": channel,
        "sent_time": sent_time.isoformat(),
        "status": status,
    }
    response = client.post("/api/nudges", json=payload)
    assert response.status_code == 201
    return response.json()


def test_recommendation_no_history_returns_404(client):
    response = client.get("/api/recommendation/nonexistent_user")
    assert response.status_code == 404


def test_recommendation_favors_high_engagement_bucket(client):
    user_id = "eng_user"

    # Strong evening WhatsApp engagement
    for day in range(4):
        _create_nudge(client, user_id, "WHATSAPP", "REPLIED", day, 19)

    # Weaker morning email engagement
    for day in range(4):
        _create_nudge(client, user_id, "EMAIL", "DELIVERED", day, 8)

    response = client.get(f"/api/recommendation/{user_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["channel"] == "WHATSAPP"
    assert 0.0 <= data["confidence"] <= 1.0
    assert "reason" in data
    assert data["user_id"] == user_id


def test_delivery_report_updates_nudge_status(client):
    nudge = _create_nudge(client, "report_user", "SMS", "DELIVERED", 1, 10)

    response = client.post(
        "/api/delivery-reports",
        json={"nudge_id": nudge["id"], "status": "CLICKED", "meta": "webhook"},
    )
    assert response.status_code == 201

    fetched = client.get(f"/api/nudges/{nudge['id']}")
    assert fetched.json()["status"] == "CLICKED"


def test_analytics_endpoint(client):
    user_id = "analytics_user"
    _create_nudge(client, user_id, "PUSH", "CLICKED", 2, 13)

    response = client.get(f"/api/users/{user_id}/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_nudges"] == 1
    assert "engagement_by_bucket" in data
    assert "engagement_by_channel" in data


def test_event_returns_a_schedule_without_history(client):
    created = client.post(
        "/api/events",
        json={
            "user_id": "new_user",
            "event_type": "subscription_renewal",
            "event_time": "2026-08-03T10:00:00Z",
            "priority": "HIGH",
        },
    ).json()

    response = client.get(f"/api/events/{created['id']}/recommendation")
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == created["id"]
    assert data["channel"] == "WHATSAPP"
    assert data["confidence"] == 0.0


def test_delivery_report_cannot_downgrade_engagement(client):
    nudge = _create_nudge(client, "ordered_reports", "SMS", "REPLIED", 1, 10)

    response = client.post(
        "/api/delivery-reports",
        json={"nudge_id": nudge["id"], "status": "DELIVERED"},
    )
    assert response.status_code == 201
    fetched = client.get(f"/api/nudges/{nudge['id']}")
    assert fetched.json()["status"] == "REPLIED"


def test_delivery_report_rejects_unknown_status(client):
    nudge = _create_nudge(client, "invalid_report", "EMAIL", "DELIVERED", 1, 10)

    response = client.post(
        "/api/delivery-reports",
        json={"nudge_id": nudge["id"], "status": "BOUNCED"},
    )
    assert response.status_code == 422
