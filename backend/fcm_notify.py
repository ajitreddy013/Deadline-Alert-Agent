import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")
FCM_API_URL = "https://fcm.googleapis.com/fcm/send"


def send_fcm_notification(device_token: str, title: str, message: str):
    if not FCM_SERVER_KEY:
        return {"error": "FCM server key not configured"}
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": device_token,
        "notification": {
            "title": title,
            "body": message,
        },
        "data": {
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
        },
    }
    try:
        resp = requests.post(FCM_API_URL, headers=headers, data=json.dumps(payload), timeout=10)
        try:
            out = resp.json()
        except Exception:
            out = {"status": resp.status_code, "text": resp.text}
        return out
    except Exception as e:
        return {"error": str(e)}