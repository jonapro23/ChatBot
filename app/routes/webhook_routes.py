import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from ..config import settings
from ..services import whatsapp_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------- GET /webhook: verificação inicial ----------
@router.get("/webhook")
async def verify_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
):
    if (
        hub_mode == "subscribe"
        and settings.WHATSAPP_VERIFY_TOKEN
        and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN
    ):
        logger.info("Webhook verificado com sucesso")
        return PlainTextResponse(hub_challenge, status_code=200)

    logger.warning("Falha na verificação do webhook")
    raise HTTPException(status_code=403, detail="Forbidden")


# ---------- Extração dos dados do payload ----------
def extract_message(payload: dict) -> dict | None:
    """Retorna os dados da mensagem ou None se o evento não for uma mensagem."""
    try:
        value = payload["entry"][0]["changes"][0]["value"]
    except (KeyError, IndexError, TypeError):
        return None

    messages = value.get("messages")
    if not messages:  # eventos de status (entregue, lida...) caem aqui
        return None

    msg = messages[0]
    contacts = value.get("contacts") or [{}]
    msg_type = msg.get("type")

    return {
        "message_id": msg.get("id"),
        "phone_number": msg.get("from"),
        "user_name": contacts[0].get("profile", {}).get("name"),
        "message_type": msg_type,
        "text": msg.get("text", {}).get("body") if msg_type == "text" else None,
        "timestamp": msg.get("timestamp"),
    }


# ---------- Regras do chatbot (depois entra a IA) ----------
def build_reply(data: dict) -> str:
    if data["message_type"] != "text":
        return "No momento consigo processar apenas mensagens de texto."

    text = (data["text"] or "").strip()
    if not text:
        return "Não consegui ler sua mensagem. Pode enviar novamente?"
    if len(text) > settings.MAX_MESSAGE_LENGTH:
        return "Sua mensagem é muito longa. Pode resumir, por favor?"

    if text.lower() in ("oi", "olá", "ola"):
        return "Olá! Como posso ajudar?"

    return f"Você disse: {text}"


async def process_message(data: dict) -> None:
    """Roda em segundo plano para responder rápido à Meta."""
    try:
        logger.info(
            "Mensagem recebida de %s (tipo: %s)", data["phone_number"], data["message_type"]
        )
        reply = build_reply(data)
        await whatsapp_service.send_message(data["phone_number"], reply)
    except Exception:
        logger.exception("Erro ao processar mensagem")


# ---------- POST /webhook: recebe os eventos ----------
@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Payload inválido")

    data = extract_message(payload)
    if data is None:
        return {"status": "ignored"}

    background_tasks.add_task(process_message, data)

    # Responde 200 na hora para a Meta não reenviar o evento
    return {"status": "ok"}