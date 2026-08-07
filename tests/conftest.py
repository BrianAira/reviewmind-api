from typing import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport

from main import app
from app.auth.dependencies import get_current_user


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def mock_firebase(monkeypatch: pytest.MonkeyPatch):
    """
    Mockea initialize_firebase y save_review en el punto donde se USAN
    (app.routers.reviews), no donde se definen (app.database.firebase),
    ya que reviews.py los importó con 'from ... import' y tiene su propia
    referencia local.
    """
    import app.routers.reviews as reviews_module

    async def fake_save_review(review_data: dict) -> dict:
        return {"id": "fake-review-id", **review_data}

    monkeypatch.setattr(reviews_module, "initialize_firebase", lambda: None)
    monkeypatch.setattr(reviews_module, "save_review", fake_save_review)

    yield


@pytest_asyncio.fixture
async def authenticated_user():
    """
    Sobreescribe la dependency de autenticación usando el mecanismo oficial
    de FastAPI (dependency_overrides), simulando un usuario ya autenticado
    sin necesidad de un token real de Firebase.
    """
    fake_user = {"uid": "test-user-123", "email": "alumno@prueba.com"}
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield fake_user
    app.dependency_overrides.pop(get_current_user, None)
    
@pytest_asyncio.fixture
async def mock_gemini_analysis(monkeypatch: pytest.MonkeyPatch):
    """
    Mockea analyze_review_text en el punto donde se usa (app.routers.reviews),
    para no depender de la API real de Gemini durante los tests.
    """
    import app.routers.reviews as reviews_module
    from app.services.review_analysis import ReviewAnalysisResult

    async def fake_analyze(text: str) -> ReviewAnalysisResult:
        return ReviewAnalysisResult(
            sentiment="NEGATIVO",
            urgency="ALTA",
            reasoning="Mock de prueba: análisis simulado sin llamar a Gemini.",
        )

    monkeypatch.setattr(reviews_module, "analyze_review_text", fake_analyze)
    yield


@pytest_asyncio.fixture
async def mock_firestore_reviews(monkeypatch: pytest.MonkeyPatch):
    import app.routers.reviews as reviews_module

    sample_reviews = [
        {"id": "1", "userId": "test-user-123", "urgency": "ALTA"},
        {"id": "2", "userId": "test-user-123", "urgency": "BAJA"},
        {"id": "3", "userId": "test-user-123", "urgency": "MEDIA"},
    ]

    async def fake_get_reviews_by_user(user_id: str):
        return [review for review in sample_reviews if review["userId"] == user_id]

    monkeypatch.setattr(
        reviews_module,
        "get_reviews_by_user",
        fake_get_reviews_by_user,
        raising=False,
    )
    yield