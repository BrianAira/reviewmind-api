import os
import asyncio
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore

firebase_app: Optional[firebase_admin.App] = None
firebase_client: Optional[firestore.AsyncClient] = None


def initialize_firebase() -> None:
    global firebase_app, firebase_client

    if firebase_app is not None and firebase_client is not None:
        return

    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required for Firebase initialization.")

    cred = credentials.Certificate(credentials_path)
    firebase_app = firebase_admin.initialize_app(cred)
    firebase_client = firestore.AsyncClient()


def get_firestore_client() -> firestore.AsyncClient:
    if firebase_client is None:
        initialize_firebase()
    return firebase_client


async def save_review(review_data: dict) -> dict:
    client = get_firestore_client()
    collection = client.collection("reviews")
    document_ref = collection.document()
    await document_ref.set(review_data)
    saved_snapshot = await document_ref.get()
    return {"id": document_ref.id, **saved_snapshot.to_dict()}