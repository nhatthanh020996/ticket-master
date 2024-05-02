import requests
import logging

logger = logging.getLogger(__name__)

def send_discord_message(webhook_url, message, bot_name):
    """
    Sends a message to a Discord channel via webhook.
    :param message: The message to send.
    """
    data = {
        "content": message,
        "username": bot_name
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        logger.error(f"Failed to send discord message: {response.status_code}, {response.text}")