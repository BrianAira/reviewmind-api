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
