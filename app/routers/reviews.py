from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.database.firebase import get_reviews_by_user, initialize_firebase, save_review
from app.services.review_analysis import analyze_review_text

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


class ReviewRequest(BaseModel):
    productId: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=1)


class ReviewResponse(BaseModel):
    id: str
    userId: str
    productId: str
    rating: int
    text: str
    sentiment: str
    urgency: str
    analysis: dict


@router.get("/", response_model=list[dict])
async def list_reviews(
    current_user=Depends(get_current_user),
    urgency: Optional[str] = Query(default=None, pattern="^(BAJA|MEDIA|ALTA)$"),
):
    initialize_firebase()
    reviews = await get_reviews_by_user(current_user["uid"])

    if urgency is not None:
        reviews = [review for review in reviews if review.get("urgency") == urgency]

    return reviews


@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(review: ReviewRequest, current_user=Depends(get_current_user)):
    initialize_firebase()

    try:
        analysis = await analyze_review_text(review.text)
    except EnvironmentError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=502, detail="Error analizando la reseña con Gemini.")

    review_data = {
        "userId": current_user["uid"],
        "productId": review.productId,
        "rating": review.rating,
        "text": review.text,
        "sentiment": analysis.sentiment,
        "urgency": analysis.urgency,
        "analysis": analysis.dict(),
    }

    saved_review = await save_review(review_data)
    return ReviewResponse(**saved_review)


@router.post("/test-notification")
async def test_notification():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://notification-service:8001/notify",
                json={"recipient": "reviewmind@example.com", "message": "Test notification from ReviewMind-API"},
                timeout=3.0,
            )
            response.raise_for_status()
            return {
                "status": "ok",
                "notification_service_response": response.json(),
            }
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=502, detail="Notification service timeout") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Notification service error: {exc.response.text}") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Unable to reach notification service") from exc
