import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from app.database.firebase import initialize_firebase
from app.routers.reviews import router as reviews_router

load_dotenv()

app = FastAPI(title="ReviewMind-API")
logger = logging.getLogger(__name__)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    try:
        initialize_firebase()
    except EnvironmentError:
        logger.warning("Firebase credentials are not available; continuing without Firebase initialization")


app.include_router(reviews_router)