import os
from pyfcm import FCMNotification

FCM_SERVER_KEY = os.environ.get("FCM_SERVER_KEY")

def send_push_notification(token, title, message):
    if not FCM_SERVER_KEY:
        return {"error": "FCM_SERVER_KEY not configured"}
    
    try:
        push_service = FCMNotification(service_account_key_path=None, 
                                     project_id=None, 
                                     api_key=FCM_SERVER_KEY)
        result = push_service.notify_single_device(
            registration_id=token,
            message_title=title,
            message_body=message
        )
        return result
    except Exception as e:
        return {"error": str(e)}
