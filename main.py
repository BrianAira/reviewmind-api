from dotenv import load_dotenv
from fastapi import FastAPI

from app.database.firebase import initialize_firebase
from app.routers.reviews import router as reviews_router

load_dotenv()

app = FastAPI(title="ReviewMind-API")

@app.on_event("startup")
async def startup_event():
    initialize_firebase()

app.include_router(reviews_router)