# 📱 WhatsApp Integration Setup Guide

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
cd backend/whatsapp-service
npm install
```

### Step 2: Start the Monitor

```bash
npm start
```

### Step 3: Scan QR Code

1. A QR code will appear in your terminal
2. Open WhatsApp on your phone
3. Go to **Settings** → **Linked Devices** → **Link a Device**
4. Scan the QR code displayed in the terminal

### Step 4: Test It!

Send yourself a WhatsApp message:
```
"Meeting with professor tomorrow at 3 PM"
```

Within seconds, you should see:
- ✅ Console log showing deadline detected
- ✅ Task created in database
- ✅ Task appears in your Flutter app (refresh if needed)

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                  AUTOMATIC FLOW                          │
└─────────────────────────────────────────────────────────┘

1. You receive WhatsApp message:
   "Submit assignment by Jan 20"
        ↓
2. WhatsApp monitor detects keywords:
   ✅ "submit", "by" → Potential deadline
        ↓
3. AI extracts deadline:
   Task: "Submit assignment"
   Date: "2026-01-20"
        ↓
4. Task created in database
        ↓
5. Appears in Flutter app automatically
   (within 30 seconds due to auto-refresh)
```

---

## Features

### ✅ What's Detected

The monitor automatically detects deadlines from:

- **Personal chats**: "Call mom tomorrow"
- **Group chats**: "Project submission Friday 5 PM"
- **Natural language**: "Don't forget the meeting next Monday"
- **Specific dates**: "Exam on Jan 25 at 10 AM"
- **Relative dates**: "Assignment due in 3 days"

### 🎯 Keyword Triggers

Messages containing these words trigger deadline detection:
- deadline, due, submit, assignment
- exam, test, quiz, project
- meeting, appointment, call
- tomorrow, today, tonight
- Days: monday, tuesday, etc.
- Months: jan, feb, mar, etc.

---

## Configuration

### Customize Monitoring

Edit `backend/whatsapp-service/whatsapp-config.js`:

#### Monitor Specific Chats Only
```javascript
chatFilter: {
  monitorAll: false,
  whitelist: ['Important Group', 'Work Chat'],
  monitorGroups: true,
  monitorPersonal: true
}
```

#### Ignore Specific Chats
```javascript
chatFilter: {
  monitorAll: true,
  blacklist: ['Spam Group', 'Memes'],
}
```

#### Add Custom Keywords
```javascript
deadlineKeywords: [
  'deadline', 'due', 'submit',
  'your-custom-keyword'
]
```

---

## Running 24/7

### Option 1: Keep Terminal Open (Simplest)
```bash
npm start
```
- Keep terminal window open
- Computer must stay on

### Option 2: Background Process
```bash
nohup npm start > whatsapp-monitor.log 2>&1 &
```
- Runs in background
- Logs to `whatsapp-monitor.log`

### Option 3: PM2 (Recommended)
```bash
# Install PM2
npm install -g pm2

# Start monitor
pm2 start whatsapp-monitor.js --name whatsapp-deadline

# Save configuration
pm2 save

# Auto-start on system boot
pm2 startup
```

**PM2 Commands:**
```bash
pm2 status              # Check status
pm2 logs whatsapp-deadline  # View logs
pm2 restart whatsapp-deadline  # Restart
pm2 stop whatsapp-deadline     # Stop
```

---

## Troubleshooting

### ❌ QR Code Not Appearing

**Problem**: Terminal doesn't show QR code

**Solutions**:
1. Use a different terminal app (iTerm2, Terminal.app)
2. Make sure terminal supports Unicode characters
3. Try running in full-screen mode

### ❌ Authentication Failed

**Problem**: "Authentication failed" error

**Solutions**:
```bash
# Delete auth folder and try again
cd backend/whatsapp-service
rm -rf .wwebjs_auth
npm start
```

### ❌ No Deadlines Detected

**Problem**: Messages not creating tasks

**Solutions**:
1. Check if message contains deadline keywords
2. Enable logging to see all messages:
   ```javascript
   // In whatsapp-config.js
   logging: {
     logAllMessages: true
   }
   ```
3. Verify backend is running:
   ```bash
   curl http://localhost:8000/tasks
   ```

### ❌ Connection Lost

**Problem**: "WhatsApp disconnected"

**Solutions**:
- Monitor will auto-reconnect
- If it doesn't, restart: `npm start`
- Check your internet connection

### ❌ Tasks Not Appearing in App

**Problem**: Deadlines detected but not in app

**Solutions**:
1. Check backend is running
2. Refresh the app (pull down)
3. Check backend logs for errors
4. Verify task was created:
   ```bash
   curl http://localhost:8000/tasks
   ```

---

## Privacy & Security

### ⚠️ Important Notes

- This service has access to **ALL** your WhatsApp messages
- Only deadline-related data is sent to the backend
- Messages are **NOT** stored or logged (unless you enable logging)
- For **personal use only** (against WhatsApp ToS for commercial use)

### What Gets Stored

Only this information is saved:
- Task summary (e.g., "Submit assignment")
- Deadline date
- Source (e.g., "WhatsApp - John Doe")

### What's NOT Stored

- Full message content
- Media files
- Other chat participants
- Message history

---

## Advanced Usage

### Custom AI Prompts

The monitor uses your existing `/extract_deadline` endpoint. To customize AI extraction, edit `backend/llm_deadline_extractor.py`.

### Webhook Integration

Want to get notified when a deadline is detected? Add this to `whatsapp-monitor.js`:

```javascript
// After task creation
await fetch('YOUR_WEBHOOK_URL', {
  method: 'POST',
  body: JSON.stringify({
    task: deadline.task,
    deadline: deadline.date,
    source: chatName
  })
});
```

### Multi-User Support

Currently designed for single-user. For multi-user:
1. Add user authentication
2. Map WhatsApp numbers to user accounts
3. Store tasks per user

---

## Monitoring & Logs

### View Real-Time Logs
```bash
# If running with npm start
# Logs appear in terminal

# If running with PM2
pm2 logs whatsapp-deadline

# If running with nohup
tail -f whatsapp-monitor.log
```

### Log Format
```
🔍 Potential deadline detected!
   From: John Doe
   Chat: Work Group (Group)
   Message: "Submit report by Friday 5 PM"

   🤖 Sending to AI for extraction...
   ✅ Deadline extracted:
      Task: Submit report
      Due: 2026-01-19T17:00:00
      Source: WhatsApp - Work Group (Group)
   💾 Task created with ID: 42
   📱 Task will appear in app automatically!
```

---

## Stopping the Monitor

### If running in terminal:
```bash
Ctrl+C
```

### If running with PM2:
```bash
pm2 stop whatsapp-deadline
```

### If running with nohup:
```bash
# Find process ID
ps aux | grep whatsapp-monitor

# Kill process
kill <PID>
```

---

## Next Steps

1. ✅ Setup complete? Test with a message!
2. 📱 Check your Flutter app for the new task
3. ⚙️ Customize keywords and filters in `whatsapp-config.js`
4. 🚀 Set up PM2 for 24/7 monitoring

---

## Need Help?

- Check the [main README](../../README.md)
- Review [WHATSAPP_INTEGRATION_GUIDE.md](../../WHATSAPP_INTEGRATION_GUIDE.md)
- Enable debug logging in `whatsapp-config.js`
