# 📱 WhatsApp Integration for Deadline Reminder

## 🎯 Overview

The WhatsApp integration allows your Deadline Reminder system to send notifications directly to your WhatsApp number, providing instant alerts for upcoming deadlines alongside email and desktop notifications.

## ✨ Features

- **📲 WhatsApp Notifications**: Send deadline reminders directly to WhatsApp
- **🔧 User Preferences**: Configure WhatsApp number and notification preferences
- **📊 Multi-Channel**: Combine WhatsApp with desktop and email notifications
- **✅ Validation**: Phone number validation and formatting
- **🎨 Rich Messages**: Formatted messages with emojis and structure

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Deadline      │    │    Twilio       │    │    WhatsApp     │
│   Reminder API  │───▶│    WhatsApp     │───▶│    Message      │
│                 │    │    API          │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Setup Instructions

### 1. Install Dependencies

The required dependencies are already included in `requirements.txt`:

```bash
cd backend
pip install twilio python-dotenv
```

### 2. Create Twilio Account

1. Go to [Twilio Console](https://console.twilio.com/)
2. Sign up for a free account
3. Get $15 free credit for testing
4. Navigate to **Console Dashboard** to find your credentials

### 3. Set Up WhatsApp Sandbox (Development)

For development and testing:

1. Go to **Console → Messaging → Try it out → Send a WhatsApp message**
2. Note your sandbox number: `+1 415 523 8886`
3. Note your sandbox code (e.g., `join happy-tiger`)
4. Send `join happy-tiger` to `+1 415 523 8886` from your WhatsApp
5. You should receive a confirmation message

### 4. Configure Environment Variables

Add to your `backend/.env` file:

```env
# WhatsApp Notifications (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 5. Test the Integration

```bash
cd backend
python test_whatsapp_integration.py
```

## 📋 API Endpoints

### User Preferences

#### Set WhatsApp Number and Preferences
```http
POST /user/preferences
Content-Type: application/json

{
  "email": "your@email.com",
  "whatsapp_number": "+1234567890",
  "email_notifications": true,
  "whatsapp_notifications": true,
  "desktop_notifications": true
}
```

#### Get Current Preferences
```http
GET /user/preferences
```

### WhatsApp Notifications

#### Send WhatsApp Notification for Task
```http
POST /notify/whatsapp/{task_id}
```

#### Send Custom WhatsApp Message
```http
POST /notify/whatsapp?to_number=+1234567890&title=Test&message=Hello
```

#### Send All Notifications (Desktop + WhatsApp)
```http
POST /notify/all/{task_id}
```

## 💬 Message Format

WhatsApp messages are formatted with emojis and structure:

```
🔔 Deadline Reminder

Task: Submit final project report

⏰ Due: December 25th at 11:59 PM
📧 Source: Gmail

Don't forget to complete this task on time! ⚡️
```

## 🧪 Testing

### Test with Curl

```bash
# Set preferences
curl -X POST "http://localhost:8000/user/preferences" \
  -H "Content-Type: application/json" \
  -d '{
    "whatsapp_number": "+1234567890",
    "whatsapp_notifications": true
  }'

# Create test task
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Test deadline",
    "deadline": "2024-12-31T23:59:59",
    "source": "test"
  }'

# Send WhatsApp notification (replace {task_id})
curl -X POST "http://localhost:8000/notify/whatsapp/1"
```

### Python Test Script

```python
import requests

# Configure preferences
preferences = {
    "whatsapp_number": "+1234567890",  # Your WhatsApp number
    "whatsapp_notifications": True
}
requests.post("http://localhost:8000/user/preferences", json=preferences)

# Create and notify
task = {
    "summary": "Important deadline",
    "deadline": "2024-12-31T23:59:59",
    "source": "test"
}
response = requests.post("http://localhost:8000/tasks", json=task)
task_id = response.json()["id"]

# Send notification
requests.post(f"http://localhost:8000/notify/all/{task_id}")
```

## 🔧 Production Setup

### WhatsApp Business API

For production use with unlimited messaging:

1. **Apply for WhatsApp Business API**
   - Go to [Facebook Business](https://business.facebook.com/)
   - Apply for WhatsApp Business API access
   - Approval process takes 1-2 weeks

2. **Use Business Solution Provider**
   - Twilio (easier setup)
   - MessageBird
   - Vonage
   - 360Dialog

3. **Update Configuration**
   ```env
   TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890  # Your approved number
   ```

## 🎮 Integration with Flutter App

The Flutter app can be updated to include WhatsApp preferences:

### Settings Screen Addition

```dart
// Add to settings screen
Card(
  child: ListTile(
    leading: Icon(Icons.message, color: Colors.green),
    title: Text('WhatsApp Notifications'),
    subtitle: Text('Send reminders to WhatsApp'),
    trailing: Switch(
      value: whatsappEnabled,
      onChanged: (value) => updateWhatsAppPreference(value),
    ),
  ),
),

TextField(
  decoration: InputDecoration(
    labelText: 'WhatsApp Number',
    hintText: '+1234567890',
    prefixIcon: Icon(Icons.phone),
  ),
  onChanged: (value) => updateWhatsAppNumber(value),
)
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Twilio credentials not configured"**
   - Check `.env` file has correct credentials
   - Verify `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`

2. **"Failed to send message"**
   - Ensure you've joined the WhatsApp sandbox
   - Verify phone number format (+1234567890)
   - Check Twilio console for error logs

3. **"Invalid phone number"**
   - Use international format: +[country code][number]
   - No spaces or special characters except +

4. **Messages not received**
   - Check WhatsApp sandbox is active
   - Verify recipient has joined sandbox
   - Check Twilio usage/billing limits

### Debug Mode

Enable debug logging in WhatsApp notify module:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring & Analytics

### Twilio Console

- Monitor message delivery status
- View usage statistics
- Check error logs
- Track costs

### API Response Handling

```python
# Check delivery status
result = send_whatsapp_notification(number, title, message)
if "error" in result:
    print(f"Failed: {result['error']}")
else:
    print(f"Message SID: {result['sid']}")
    print(f"Status: {result['status']}")
```

## 💰 Pricing

### Twilio Sandbox (Free)
- Free for development/testing
- Limited to pre-approved numbers
- Rate limits apply

### Twilio WhatsApp Business API
- ~$0.0025 - $0.012 per message (varies by country)
- Volume discounts available
- No setup fees

## 🔒 Security Best Practices

1. **Secure Credentials**
   ```bash
   # Store in environment variables
   export TWILIO_ACCOUNT_SID="your_sid"
   export TWILIO_AUTH_TOKEN="your_token"
   ```

2. **Rate Limiting**
   - Implement rate limiting in your API
   - Avoid spamming users with notifications

3. **User Consent**
   - Only send messages to consented users
   - Provide opt-out mechanism

4. **Data Privacy**
   - Don't log sensitive phone numbers
   - Follow GDPR/privacy regulations

## 🚀 Advanced Features

### Scheduled Notifications

```python
# Schedule WhatsApp reminder
from datetime import datetime, timedelta

def schedule_whatsapp_reminder(task, hours_before=24):
    reminder_time = datetime.fromisoformat(task.deadline) - timedelta(hours=hours_before)
    # Use celery or similar for scheduling
```

### Interactive Messages

```python
# Add quick reply buttons (requires approval)
def send_interactive_reminder(number, task):
    message = f"""
🔔 Deadline Reminder: {task.summary}

⏰ Due: {task.deadline}

Reply:
✅ DONE - Mark as complete
⏰ SNOOZE - Remind me in 1 hour
❌ CANCEL - Stop reminders for this task
    """
    return send_whatsapp_notification(number, "Deadline Alert", message)
```

### Rich Media

```python
# Send with image/document (requires approval)
def send_rich_notification(number, task, media_url=None):
    # Twilio supports images, documents, etc.
    pass
```

## 🎯 Next Steps

1. **Set up Twilio account and sandbox**
2. **Configure credentials in `.env`**
3. **Run test script to verify integration**
4. **Update Flutter app for user preferences**
5. **Test with your actual WhatsApp number**
6. **Apply for WhatsApp Business API for production**

## 📚 Resources

- [Twilio WhatsApp API Documentation](https://www.twilio.com/docs/whatsapp)
- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Twilio Console](https://console.twilio.com/)
- [WhatsApp Business Platform](https://business.whatsapp.com/)

---

🎉 **Your WhatsApp integration is now ready!** You can receive deadline reminders directly on WhatsApp alongside your existing email and desktop notifications.
