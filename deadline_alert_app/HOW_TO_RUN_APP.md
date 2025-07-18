# 📱 How to Run the Deadline Reminder Flutter App

## 🚀 Quick Start

### 1. Make sure the backend is running:
```bash
cd ../backend
source venv/bin/activate
python run_server.py
```

### 2. Run the Flutter app:
```bash
cd deadline_alert_app
flutter run
```

## 📋 Available Platforms

Based on your system, you can run on:

### ✅ **Web (Chrome)** - Recommended for testing
```bash
flutter run -d chrome
```

### ✅ **Android** - If you have Android Studio/device
```bash
flutter run -d android
```

### ⚠️ **iOS/macOS** - Requires Xcode installation
```bash
flutter run -d ios     # Requires Xcode
flutter run -d macos   # Requires Xcode
```

## 🎯 What the App Does

### **Main Features:**
1. **View All Deadlines** - Shows tasks from Gmail, WhatsApp, and manual entries
2. **Real-time Updates** - Syncs with backend automatically
3. **Push Notifications** - Receives deadline alerts (if Firebase is configured)
4. **Refresh Data** - Pull to refresh or tap refresh button

### **App Screenshots/Flow:**
```
📱 App Launch
    ↓
📋 Task List Screen
    ├── 📧 Gmail Tasks (with deadlines)
    ├── 💬 WhatsApp Tasks (with deadlines)
    ├── ✍️ Manual Tasks
    └── 🔔 Notifications (if configured)
```

## 📊 What You'll See

### **Task Display:**
- **Title:** Email subject or WhatsApp message preview
- **Deadline:** Extracted deadline date/time
- **Source:** Gmail, WhatsApp, or Manual
- **Status:** Pending, Completed, etc.

### **Example Tasks:**
```
📧 Submit assignment by Dec 25th
   Due: December 25th at 11:59 PM
   Source: Gmail

💬 Meeting tomorrow at 3 PM
   Due: Tomorrow at 3:00 PM
   Source: WhatsApp

✍️ Project completion
   Due: 2024-12-31T23:59:59
   Source: Manual
```

## 🔧 Troubleshooting

### **If app doesn't connect to backend:**
1. Ensure backend is running on `http://localhost:8000`
2. Check if you can access `http://localhost:8000/tasks` in browser
3. Make sure no firewall is blocking port 8000

### **If no tasks appear:**
1. Try the refresh button in the app
2. Check if you have any tasks in the backend:
   ```bash
   curl http://localhost:8000/tasks
   ```
3. Import some tasks from Gmail:
   ```bash
   curl -X POST http://localhost:8000/ingest/gmail
   ```

### **If Firebase notifications don't work:**
1. Firebase setup is optional for basic functionality
2. App will work without Firebase, just no push notifications
3. Desktop notifications still work through the backend

## 🌐 Running on Web (Easiest)

The web version is perfect for testing:

```bash
flutter run -d chrome
```

This will:
- Open Chrome browser
- Show the app interface
- Connect to your local backend
- Display all your deadlines

## 📱 Running on Mobile

### **Android:**
1. Enable Developer Options on your phone
2. Enable USB Debugging
3. Connect phone to computer
4. Run: `flutter run -d android`

### **iOS (requires Xcode):**
1. Install Xcode from App Store
2. Connect iPhone to computer
3. Run: `flutter run -d ios`

## 🎉 What's Next

Once the app is running:
1. **View your current deadlines** from Gmail
2. **Add manual tasks** using the backend API
3. **Test WhatsApp integration** (scan QR code)
4. **Set up Firebase** for push notifications (optional)

The app is your mobile dashboard for all deadline management!
