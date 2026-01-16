# WhatsApp Deadline Monitor

Automatically monitors your WhatsApp messages and extracts deadlines using AI.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Monitor
```bash
npm start
```

### 3. Scan QR Code
- A QR code will appear in the terminal
- Open WhatsApp on your phone
- Go to Settings → Linked Devices → Link a Device
- Scan the QR code

### 4. Done!
The monitor is now active and will automatically:
- Listen to all your WhatsApp messages
- Detect deadline-related keywords
- Extract deadlines using AI
- Create tasks in your app

## How It Works

```
WhatsApp Message
    ↓
"Submit assignment by Jan 20"
    ↓
Keyword Detection (deadline, submit, by)
    ↓
AI Extraction (Groq)
    ↓
Task Created in Database
    ↓
Appears in Flutter App
```

## Configuration

Edit `whatsapp-config.js` to customize:

- **Deadline Keywords**: Words that trigger deadline detection
- **Chat Filters**: Which chats to monitor (all/specific/groups only)
- **Message Filters**: Message length, ignore self, etc.
- **Logging**: Control what gets logged

## Examples

The monitor will detect deadlines from messages like:

- "Meeting tomorrow at 3 PM"
- "Assignment due Friday"
- "Don't forget to submit the project by Jan 25"
- "Exam on Monday at 10 AM"
- "Call the client before 5 PM today"

## Troubleshooting

### QR Code Not Appearing
- Make sure your terminal supports QR code display
- Try running in a different terminal app

### Authentication Failed
```bash
# Delete auth folder and try again
rm -rf .wwebjs_auth
npm start
```

### No Deadlines Detected
- Check if message contains deadline keywords
- Enable `logAllMessages` in config to see all messages
- Verify backend is running and accessible

### Connection Lost
- The monitor will auto-reconnect
- If it doesn't, restart with `npm start`

## Privacy & Security

- ⚠️ This service has access to ALL your WhatsApp messages
- Only deadline-related data is sent to the backend
- Messages are NOT stored or logged (unless you enable logging)
- For personal use only

## Stopping the Monitor

Press `Ctrl+C` to stop the monitor gracefully.

## Running 24/7

### Option 1: Keep Terminal Open
- Simple but requires computer to stay on

### Option 2: Use PM2 (Recommended)
```bash
npm install -g pm2
pm2 start whatsapp-monitor.js --name whatsapp-deadline
pm2 save
pm2 startup
```

### Option 3: Run as Background Service
```bash
nohup npm start > whatsapp-monitor.log 2>&1 &
```

## Logs

Check logs to see detected deadlines:
```bash
tail -f whatsapp-monitor.log
```
