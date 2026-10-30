"""Тест маршрута /health."""


def test_health(client):
    """GET /health возвращает 200 и JSON {"status": "ok"}."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
