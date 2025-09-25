import os
from typing import Optional
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")  # Twilio Sandbox number

def send_whatsapp_notification(to_number: str, title: str, message: str) -> dict:
    """
    Send WhatsApp notification using Twilio API
    
    Args:
        to_number: WhatsApp number in format +1234567890
        title: Notification title
        message: Notification message
        
    Returns:
        dict: Response from Twilio API
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("❌ Twilio credentials not configured")
        return {"error": "Twilio credentials not configured"}
    
    # Format the phone number for WhatsApp
    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"
    
    # Prepare the message
    full_message = f"🔔 *{title}*\n\n{message}"
    
    # Twilio API endpoint
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    # Prepare authentication
    auth = base64.b64encode(f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}".encode()).decode()
    
    # Prepare the payload
    payload = {
        'From': TWILIO_WHATSAPP_NUMBER,
        'To': to_number,
        'Body': full_message
    }
    
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ WhatsApp message sent successfully to {to_number}")
        return {
            "success": True,
            "sid": result.get("sid"),
            "status": result.get("status"),
            "to": result.get("to")
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send WhatsApp message: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"❌ Unexpected error sending WhatsApp message: {e}")
        return {"error": str(e)}

def send_deadline_reminder_whatsapp(to_number: str, task_summary: str, deadline: str, source: str) -> dict:
    """
    Send a formatted deadline reminder via WhatsApp
    
    Args:
        to_number: WhatsApp number in format +1234567890
        task_summary: Summary of the task
        deadline: Deadline date/time
        source: Source of the task (gmail, whatsapp, manual)
        
    Returns:
        dict: Response from sending the message
    """
    title = "📅 Deadline Reminder"
    
    # Format the message with emojis and formatting
    source_emoji = {
        "gmail": "📧",
        "whatsapp": "💬", 
        "manual": "✍️"
    }.get(source, "📋")
    
    message = f"""
*Task:* {task_summary}

⏰ *Due:* {deadline}
{source_emoji} *Source:* {source.title()}

Don't forget to complete this task on time! ⚡️
    """.strip()
    
    return send_whatsapp_notification(to_number, title, message)

def validate_whatsapp_number(phone_number: str) -> Optional[str]:
    """
    Validate and format WhatsApp phone number
    
    Args:
        phone_number: Phone number to validate
        
    Returns:
        Optional[str]: Formatted phone number or None if invalid
    """
    # Remove all non-digit characters except +
    import re
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Must start with + and have at least 10 digits
    if not cleaned.startswith('+') or len(cleaned) < 11:
        return None
        
    return cleaned

# Test function
def test_whatsapp_notification():
    """Test WhatsApp notification with a sample message"""
    test_number = "+1234567890"  # Replace with your WhatsApp number for testing
    result = send_deadline_reminder_whatsapp(
        to_number=test_number,
        task_summary="Complete project submission",
        deadline="December 25th at 11:59 PM",
        source="gmail"
    )
    print(f"Test result: {result}")

if __name__ == "__main__":
    test_whatsapp_notification()
