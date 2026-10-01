import logging
from fastapi import FastAPI

from .routes.webhook_routes import router as webhook_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="Chatbot WhatsApp")
app.include_router(webhook_router)


@app.get("/health")
async def health():
    return {"status": "ok"}