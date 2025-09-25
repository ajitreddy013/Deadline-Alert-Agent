# 📧💬 Gmail & WhatsApp Deadlines Manager

A focused Flutter application for managing deadlines extracted from Gmail and WhatsApp messages. This app provides a clean, dedicated interface for viewing and managing your important deadlines from these two primary communication sources.

## 🎯 Features

### 📧 **Gmail Integration**
- **Automatic Email Scanning**: Connects to your Gmail account and scans for deadline-related emails
- **Smart Deadline Extraction**: Uses AI-powered NLP to identify dates and deadlines in email content
- **Real-time Sync**: Automatically fetches new emails and updates your deadline list
- **Email Context**: View the original email subject and deadline information
- **Search & Filter**: Find specific deadlines quickly with search and status filtering

### 💬 **WhatsApp Integration**
- **Chat Message Scanning**: Scan specific WhatsApp chats for deadline mentions
- **Message Context**: View deadline information extracted from chat messages
- **Multiple Chat Support**: Scan different chat groups and conversations
- **QR Code Setup**: Easy one-time setup through WhatsApp Web

### 🔔 **Smart Notifications**
- **Multi-Channel Alerts**: Desktop notifications, WhatsApp messages, and email alerts
- **Customizable Preferences**: Configure notification settings for each platform
- **Instant Notifications**: Send immediate alerts for urgent deadlines
- **Status Tracking**: Track which notifications have been sent

### ⚙️ **Settings & Configuration**
- **Notification Preferences**: Enable/disable notifications for desktop, email, and WhatsApp
- **Contact Information**: Manage your email and WhatsApp number for notifications
- **App Information**: View connection status and data sources

## 🚀 Quick Start

### Prerequisites
- Flutter 3.8.1+ installed
- Backend server running (from parent directory)
- Gmail credentials configured
- WhatsApp Web access (for WhatsApp features)

### 1. Install Dependencies
```bash
flutter pub get
```

### 2. Start the Backend Server
```bash
cd ../backend
source venv/bin/activate
python run_server.py
```

### 3. Run the Flutter App
```bash
flutter run
```

### 4. Available Platforms
- **Chrome (Web)**: `flutter run -d chrome` - Recommended for testing
- **Android**: `flutter run -d android` - Requires Android Studio/device
- **iOS**: `flutter run -d ios` - Requires Xcode
- **Desktop**: `flutter run -d macos/windows/linux`

## 📱 App Screens

### 1. Gmail Deadlines Screen
- View all deadlines extracted from Gmail
- Search and filter by status (All, Pending, Sent)
- Refresh to sync with latest emails
- Ingest new emails with one tap
- Send notifications for specific deadlines

### 2. WhatsApp Deadlines Screen
- View all deadlines from WhatsApp messages
- Scan specific chats for new deadlines
- Search and filter capabilities
- WhatsApp-specific notification options
- Chat context preservation

### 3. Settings Screen
- Configure notification preferences
- Manage contact information
- View app information and connection status
- Toggle different notification channels

## 🔧 Configuration

### Backend Connection
The app connects to your local backend server at `http://localhost:8000`. Ensure the backend is running before starting the app.

### Notification Setup
1. **Desktop**: Automatically enabled
2. **WhatsApp**: Requires phone number configuration in settings
3. **Email**: Requires email address configuration in settings

---

This app provides a focused, clean interface for managing your Gmail and WhatsApp deadlines in one place. 🎉
