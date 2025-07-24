import os
import requests
from dotenv import load_dotenv

load_dotenv()

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")

ONESIGNAL_API_URL = "https://onesignal.com/api/v1/notifications"

def send_onesignal_notification(player_id, title, message):
    if not ONESIGNAL_APP_ID or not ONESIGNAL_API_KEY:
        return {"error": "OneSignal credentials not configured"}
    headers = {
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "include_player_ids": [player_id],
        "headings": {"en": title},
        "contents": {"en": message}
    }
    try:
        response = requests.post(ONESIGNAL_API_URL, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)} 