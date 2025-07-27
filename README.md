# 📅 Deadline Alert App

A comprehensive Flutter application that helps you manage deadlines by automatically fetching them from your emails and WhatsApp messages.

## ✨ Features

### 🎯 Core Deadline Management

- **Add, Edit, Delete** deadlines with detailed information
- **Priority-based color coding** (red for overdue, orange for today, etc.)
- **Completion tracking** with visual indicators
- **Time remaining** display for each deadline
- **Filtering options** (All, Pending, Completed, Overdue, Today)

### 📧 Email Integration

- **IMAP-based email fetching** (Gmail, Outlook, Yahoo support)
- **Automatic deadline extraction** from email content
- **Email settings persistence** and status checking
- **Mock email data** for demonstration purposes
- **Auto-fetch every 6 hours** when enabled

### 📱 WhatsApp Integration

- **Manual WhatsApp message input** for deadline extraction
- **Natural language processing** to extract dates and times
- **Mock WhatsApp data** for demonstration
- **Deadline parsing** from conversation context

### 📊 Analytics & Statistics

- **Comprehensive dashboard** with deadline statistics
- **Visual progress indicators** for completion rates
- **Overdue deadline tracking**
- **Today's deadline overview**

### 💾 Data Management

- **Local storage** using SharedPreferences
- **Settings persistence** (email credentials, preferences)
- **Export/Import functionality** for deadlines
- **Cross-platform support** (Web, Android, iOS)

## 🚀 Getting Started

### Prerequisites

- Flutter SDK (latest stable version)
- Dart SDK
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/deadline_alert_app.git
   cd deadline_alert_app
   ```

2. **Install dependencies**

   ```bash
   flutter pub get
   ```

3. **Run the app**
   ```bash
   flutter run -d chrome  # For web
   flutter run -d android # For Android
   flutter run -d ios     # For iOS
   ```

## 📧 Email Setup

### Gmail Configuration

1. Open the app and go to **Settings** → **Email Integration**
2. Enter your Gmail address and password
3. **Option 1**: Enable "Less secure app access" in your Google Account
4. **Option 2** (Recommended): Use an App Password
   - Enable 2-Step Verification
   - Generate an App Password
   - Use the App Password instead of your regular password

### Other Email Providers

- **Outlook**: `outlook.office365.com:993`
- **Yahoo**: `imap.mail.yahoo.com:993`

## 📱 WhatsApp Integration

1. Go to **Settings** → **WhatsApp Integration**
2. Paste a WhatsApp message containing a deadline
3. Example: "Team meeting tomorrow at 2 PM"
4. The app will automatically extract and create the deadline

## 🎨 Usage

### Adding Deadlines

- Tap the **"Add Deadline"** button
- Fill in title, description, date, and time
- Tap **"Save"** to create the deadline

### Managing Deadlines

- **Tap a deadline** to mark it as complete/incomplete
- **Long press** to edit or delete
- **Use filters** to view specific deadline types
- **Check statistics** for overview

### Auto-Fetch

- Enable auto-fetch in settings
- App automatically fetches new deadlines every 6 hours
- Manual fetch available through settings

## 🛠️ Technical Details

### Architecture

- **Flutter/Dart** for cross-platform development
- **Material Design 3** for modern UI
- **SharedPreferences** for local data storage
- **Modular service architecture** for maintainability

### Key Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  intl: ^0.19.0 # Date formatting
  http: ^1.1.0 # HTTP requests
  url_launcher: ^6.2.1 # External app launching
  permission_handler: ^11.0.1 # Permissions
  shared_preferences: ^2.2.2 # Local storage
```

### File Structure

```
lib/
├── main.dart                    # Main app entry point
├── models/
│   └── deadline.dart           # Deadline data model
└── services/
    ├── personal_deadline_service.dart    # Local data management
    ├── simple_email_fetcher.dart         # Email integration
    └── simple_whatsapp_fetcher.dart      # WhatsApp integration
```

## 🔧 Configuration

### Email Settings

- Configure email credentials in app settings
- Enable/disable auto-fetch functionality
- Check integration status

### WhatsApp Settings

- Add manual messages for deadline extraction
- Configure auto-fetch preferences

## 📱 Screenshots

[Add screenshots here when available]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flutter team for the amazing framework
- Material Design team for the design system
- All contributors and testers

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/deadline_alert_app/issues) page
2. Create a new issue with detailed information
3. Include device/OS information and steps to reproduce

---

**Made with ❤️ using Flutter**
