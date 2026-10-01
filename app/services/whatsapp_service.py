import logging
import httpx

from ..config import settings

logger = logging.getLogger(__name__)


async def send_message(phone_number: str, message: str) -> bool:
    url = (
        f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}"
        f"/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message},
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        logger.info("Resposta enviada para %s", phone_number)
        return True
    except httpx.HTTPStatusError as e:
        logger.error(
            "API do WhatsApp recusou a mensagem: %s | %s",
            e.response.status_code,
            e.response.text,
        )
    except httpx.RequestError as e:
        logger.error("Erro de rede ao enviar mensagem: %s", e)

    return False