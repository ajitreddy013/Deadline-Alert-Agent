# 🚀 Quick Start: WhatsApp Deadline Integration

## ⚡ Get Started in 5 Minutes

### Step 1: Install WhatsApp Monitor Dependencies

```bash
cd backend/whatsapp-service
npm install
```

**Expected output:**
```
added 150 packages in 30s
```

---

### Step 2: Start Your Backend (if not running)

```bash
cd backend
python run_server.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Keep this terminal open!

---

### Step 3: Start WhatsApp Monitor

Open a **new terminal** and run:

```bash
cd backend/whatsapp-service
npm start
```

**You'll see:**
```
🚀 Starting WhatsApp Deadline Monitor...
📡 Backend URL: http://localhost:8000
🔄 Initializing WhatsApp client...

📱 Scan this QR code with WhatsApp:

█████████████████████████████
█████████████████████████████
████ ▄▄▄▄▄ █▀█ █▄▄▀▄ ▄▄▄▄▄ ████
████ █   █ █▀▀▀█ ▀ █ █   █ ████
...

👆 Open WhatsApp on your phone → Settings → Linked Devices → Link a Device
```

---

### Step 4: Scan QR Code

1. Open WhatsApp on your phone
2. Tap the **⋮** (three dots) menu
3. Go to **Linked Devices**
4. Tap **Link a Device**
5. Scan the QR code in your terminal

**You'll see:**
```
🔐 Authentication successful!
✅ WhatsApp monitoring is now ACTIVE!
📨 Listening for deadline-related messages...
```

---

### Step 5: Test It!

Send yourself a WhatsApp message:

```
"Meeting with professor tomorrow at 3 PM"
```

**In the terminal, you'll see:**
```
🔍 Potential deadline detected!
   From: You
   Chat: You (Personal)
   Message: "Meeting with professor tomorrow at 3 PM"

   🤖 Sending to AI for extraction...
   ✅ Deadline extracted:
      Task: Meeting with professor
      Due: 2026-01-18T15:00:00
      Source: WhatsApp - You (Personal)
   💾 Task created with ID: 1
   📱 Task will appear in app automatically!
```

---

### Step 6: Check Your App

Open your Flutter app and you'll see:

```
🟡 Meeting with professor
   Due in 1 day
   WhatsApp - You (Personal)
```

---

## ✅ Success! What Now?

### Keep It Running 24/7

**Option 1: Simple (Keep Terminal Open)**
- Just leave the terminal running
- Computer must stay on

**Option 2: Background Process**
```bash
cd backend/whatsapp-service
nohup npm start > whatsapp.log 2>&1 &
```

**Option 3: PM2 (Recommended)**
```bash
npm install -g pm2
cd backend/whatsapp-service
pm2 start whatsapp-monitor.js --name whatsapp-deadline
pm2 save
pm2 startup
```

---

## 🎯 What Gets Detected?

The monitor automatically detects deadlines from messages like:

### ✅ Examples That Work

- "Meeting tomorrow at 3 PM"
- "Assignment due Friday"
- "Submit project by Jan 25"
- "Exam on Monday at 10 AM"
- "Don't forget to call mom this Sunday"
- "Presentation next week"
- "Deadline: Submit report before 5 PM today"

### ❌ Examples That Don't Work

- "Hello" (no deadline keywords)
- "How are you?" (no time reference)
- "Nice!" (too short)

---

## 🔧 Customization

### Monitor Specific Chats Only

Edit `backend/whatsapp-service/whatsapp-config.js`:

```javascript
chatFilter: {
  monitorAll: false,
  whitelist: ['Work Group', 'College Friends'],
}
```

### Add Custom Keywords

```javascript
deadlineKeywords: [
  'deadline', 'due', 'submit',
  'your-custom-word'  // Add your own!
]
```

### Ignore Certain Chats

```javascript
chatFilter: {
  monitorAll: true,
  blacklist: ['Spam Group', 'Memes'],
}
```

---

## 🐛 Troubleshooting

### QR Code Not Showing?
- Use iTerm2 or Terminal.app
- Make terminal full-screen
- Try a different terminal emulator

### Authentication Failed?
```bash
cd backend/whatsapp-service
rm -rf .wwebjs_auth
npm start
```

### No Deadlines Detected?
- Check message contains deadline keywords
- Enable debug logging in `whatsapp-config.js`
- Verify backend is running

### Tasks Not in App?
- Pull down to refresh
- Check backend is running
- Wait 30 seconds for auto-refresh

---

## 📱 Enhanced App Features

Your app now has:

### 🎨 Color-Coded Urgency
- 🔴 **Red**: Overdue or < 1 hour
- 🟠 **Orange**: < 1 day
- 🟡 **Yellow**: < 3 days
- 🟢 **Green**: > 3 days

### ⏱️ Relative Time
- "Due in 30 mins"
- "Due in 2 hours"
- "Due in 3 days"
- "Overdue by 2 hours"

### 🔍 Source Filtering
Tap the filter icon to show:
- 📋 All Sources
- 📧 Gmail only
- 💬 WhatsApp only
- ✍️ Manual only

### 🔄 Auto-Refresh
App refreshes every 30 seconds to show new WhatsApp deadlines

---

## 🎉 You're All Set!

Your app now automatically:
- ✅ Monitors all WhatsApp messages
- ✅ Detects deadline keywords
- ✅ Extracts deadlines using AI
- ✅ Creates tasks automatically
- ✅ Shows them in your app

**No manual work required!** 🚀

---

## 📚 More Info

- Full setup guide: [WHATSAPP_SETUP.md](../WHATSAPP_SETUP.md)
- Configuration: `backend/whatsapp-service/whatsapp-config.js`
- Logs: Check terminal or `whatsapp.log`

---

## 🛑 Stopping the Monitor

**If running in terminal:**
```bash
Ctrl+C
```

**If running with PM2:**
```bash
pm2 stop whatsapp-deadline
```

**If running with nohup:**
```bash
ps aux | grep whatsapp
kill <PID>
```
