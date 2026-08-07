from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Notification Service")


class NotificationRequest(BaseModel):
    recipient: str
    message: str


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/notify")
async def notify(payload: NotificationRequest) -> dict:
    return {
        "status": "queued",
        "recipient": payload.recipient,
    }
