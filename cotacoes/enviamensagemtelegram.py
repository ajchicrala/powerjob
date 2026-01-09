import os
import requests
from dotenv import load_dotenv

# Carrega variáveis do .env apenas uma vez
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_mensagem_telegram(mensagem: str) -> bool:
    """
    Envia uma mensagem para um chat do Telegram.

    :param mensagem: Texto da mensagem a ser enviada
    :return: True se enviou com sucesso, False se falhou
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não configurados no .env")

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem para o Telegram: {e}")
        return False
