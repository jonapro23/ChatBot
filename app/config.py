import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Confira a versão atual na documentação da Meta
    GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v21.0")

    MAX_MESSAGE_LENGTH = 1000  # limite de tamanho (requisito de segurança)


settings = Settings()