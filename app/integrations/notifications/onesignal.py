import os
import json
import requests
from app.core.config import settings


ONESIGNAL_API_URL = "https://api.onesignal.com/notifications"


def send(title: str, message: str):
    if not (settings.onesignal_enabled and settings.onesignal_app_id and settings.onesignal_rest_api_key):
        print("[OneSignal] Not configured; skipping push")
        return
    # NOTE: In a real app, you'd supply include_player_ids or filters/external_id.
    # This is a placeholder that will no-op without device identifiers.
    headers = {
        "Authorization": f"Basic {settings.onesignal_rest_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "app_id": settings.onesignal_app_id,
        "included_segments": ["Subscribed Users"],  # placeholder
        "headings": {"en": title},
        "contents": {"en": message},
    }
    try:
        resp = requests.post(ONESIGNAL_API_URL, headers=headers, data=json.dumps(payload), timeout=10)
        if resp.status_code >= 400:
            print(f"[OneSignal] Error {resp.status_code}: {resp.text}")
        else:
            print("[OneSignal] Notification queued")
    except Exception as e:
        print(f"[OneSignal] Exception: {e}")
