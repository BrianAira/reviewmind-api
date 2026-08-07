import pytest


@pytest.mark.asyncio
async def test_create_review_returns_201_and_mocked_analysis(
    client,
    mock_firebase,
    mock_gemini_analysis,
    authenticated_user,
):
    payload = {
        "productId": "product-123",
        "rating": 4,
        "text": "Muy mala experiencia con el servicio",
    }

    response = await client.post("/api/v1/reviews/", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["userId"] == "test-user-123"
    assert body["sentiment"] == "NEGATIVO"
    assert body["urgency"] == "ALTA"


@pytest.mark.asyncio
async def test_create_review_rejects_invalid_payload(client, authenticated_user):
    payload = {
        "productId": "product-123",
        "rating": 10,
        "text": "Reseña inválida",
    }

    response = await client.post("/api/v1/reviews/", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_test_notification_success(client, monkeypatch):
    class DummyResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, json=None, timeout=3.0):
            return DummyResponse({"status": "queued", "recipient": "reviewmind@example.com"})

    import app.routers.reviews as reviews_module

    monkeypatch.setattr(reviews_module.httpx, "AsyncClient", lambda: DummyClient())

    response = await client.post("/api/v1/reviews/test-notification")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_get_reviews_filtered_by_urgency_alta(
    client,
    mock_firebase,
    authenticated_user,
    mock_firestore_reviews,
):
    response = await client.get("/api/v1/reviews/?urgency=ALTA")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert all(review["urgency"] == "ALTA" for review in body)


@pytest.mark.asyncio
async def test_get_reviews_invalid_urgency_value(client, authenticated_user):
    response = await client.get("/api/v1/reviews/?urgency=CRITICA")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_reviews_without_urgency_filter(
    client,
    mock_firebase,
    authenticated_user,
    mock_firestore_reviews,
):
    response = await client.get("/api/v1/reviews/")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert {review["id"] for review in body} == {"1", "2", "3"}
