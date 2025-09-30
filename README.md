# 📅 Deadline Reminder - AI-Powered Task Management System

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![Flutter](https://img.shields.io/badge/Flutter-3.32+-blue.svg)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A smart, AI-powered deadline management system that automatically extracts deadlines from your Gmail and WhatsApp messages, sends intelligent notifications, and helps you stay on top of all your important tasks.

## 🚀 Features

### 🧠 **Smart Deadline Extraction**
- **Gmail Integration**: Automatically scans your emails for deadline-related content
- **AI-Powered NLP**: Uses spaCy for intelligent date and task recognition
- **Pattern Recognition**: Detects hackathons, assignments, meetings, and project deadlines
- **WhatsApp Integration**: Extracts deadlines from chat messages

### 📱 **Multi-Platform Notifications**
- **Desktop Notifications**: Native macOS notifications for upcoming deadlines
- **Mobile Push Notifications**: Firebase Cloud Messaging for mobile alerts
- **Smart Timing**: Contextual reminder scheduling

### 🔧 **Powerful API**
- **RESTful API**: Built with FastAPI for high performance
- **Real-time Processing**: Instant deadline extraction and storage
- **Interactive Documentation**: Auto-generated API docs at `/docs`
- **Database Integration**: SQLite for reliable data persistence

### 📲 **Flutter Mobile App**
- **Cross-Platform**: iOS, Android, Web, and Desktop support
- **Real-time Sync**: Seamless integration with backend API
- **Modern UI**: Clean, intuitive interface for task management
- **Push Notifications**: Stay updated on all your deadlines

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Gmail/WhatsApp │    │   FastAPI       │    │   Flutter App   │
│   Integration   │ ── │   Backend       │ ── │   Mobile/Web    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   spaCy NLP     │    │   SQLite DB     │    │   Firebase      │
│   Processing    │    │   Storage       │    │   Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Python 3.13+** - Core language
- **FastAPI** - High-performance web framework
- **spaCy** - Advanced NLP for deadline extraction
- **SQLAlchemy** - Database ORM
- **SQLite** - Lightweight database
- **python-dotenv** - Environment variable management

### Frontend
- **Flutter 3.32+** - Cross-platform mobile framework
- **Dart** - Programming language for Flutter
- **HTTP** - API communication
- **Firebase Cloud Messaging** - Push notifications

### Integrations
- **Gmail IMAP** - Email scanning and processing
- **WhatsApp Web** - Message extraction via Selenium
- **Firebase** - Mobile push notifications
- **macOS Notifications** - Desktop alerts

## 📋 Quick Start

### Prerequisites
- Python 3.13+
- Flutter 3.32+
- Gmail account with app password
- (Optional) Firebase project for mobile notifications

### 1. Clone Repository
```bash
git clone https://github.com/ajitreddy013/Deadline-Alert-Agent.git
cd "Deadline Reminder"
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.template .env
# Edit .env with your Gmail credentials
```

### 3. Configure Gmail
1. Enable 2-factor authentication on your Gmail account
2. Generate an app-specific password
3. Add credentials to `backend/.env`:
   ```
   GMAIL_EMAIL=your-email@gmail.com
   GMAIL_PASSWORD=your-app-password
   ```

### 4. Start Backend Server
```bash
cd backend
python run_server.py
```
Server will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 5. Flutter App Setup
```bash
cd deadline_alert_app
flutter pub get
flutter run
```

### 6. Quick Start Script
```bash
./start_project.sh
```

## 💬 WhatsApp Ingestion (via WhatsApp Web)

- First run will open Chrome to https://web.whatsapp.com and may prompt a QR login.
- The WhatsApp Web session is persisted at: `~/.deadline_reminder/whatsapp_profile` (so you usually won't need to re-scan).
- Trigger ingestion for a chat by name (make sure the backend is running):

```bash
# Using curl
curl -X POST "http://localhost:8000/ingest/whatsapp?chat_name=Family"

# Or via the helper script
backend/scripts/ingest_whatsapp.sh "Family"
```

Tip: Keep the WhatsApp Web session alive by staying logged in. Re-scan if necessary.

## 🔧 Configuration

### Environment Variables
Create `backend/.env` from `backend/.env.template`:

```env
# Gmail Configuration
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-app-password

# Firebase Cloud Messaging (Optional)
FCM_SERVER_KEY=your-fcm-server-key

# Database
DATABASE_URL=sqlite:///./tasks.db
```

### Gmail Setup
1. Go to [Google Account Settings](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Generate App Password:
   - Select "Mail" as the app
   - Copy the 16-character password
   - Use this in your `.env` file

## 📚 API Documentation

### Core Endpoints
- `GET /tasks` - List all tasks
- `POST /tasks` - Create new task
- `POST /ingest/gmail` - Import deadlines from Gmail
- `POST /ingest/whatsapp` - Import deadlines from WhatsApp
- `POST /extract_deadline` - Extract deadlines from text
- `POST /notify/desktop/{id}` - Send desktop notification
- `POST /notify/mobile` - Send mobile notification

### Example Usage
```python
import requests

# Extract deadlines from Gmail
response = requests.post("http://localhost:8000/ingest/gmail")
print(response.json())

# Get all tasks
tasks = requests.get("http://localhost:8000/tasks")
print(tasks.json())
```

## 🧪 Testing

### Run Tests
```bash
# Test full project
python test_full_project.py

# Test specific components
cd backend
python test_api.py
python test_gmail.py
python test_whatsapp.py
```

### Expected Output
```
✅ API Endpoints: Working
✅ Gmail Integration: Working (10 emails found, 2 with deadlines)
✅ WhatsApp Integration: Ready (requires manual QR scan)
✅ Desktop Notifications: Working
✅ Flutter App: Ready to run
```

## 🎯 Use Cases

- **Students**: Track assignment deadlines, exam schedules, project submissions
- **Professionals**: Monitor project milestones, meeting deadlines, deliverables
- **Developers**: Keep track of hackathon deadlines, code review deadlines
- **Freelancers**: Manage client deadlines, invoice due dates, project timelines
- **Event Organizers**: Track submission deadlines, registration cutoffs

## 🔒 Security

This project follows security best practices:
- Environment variables for sensitive data
- No hardcoded credentials in source code
- Local-only storage of personal information
- Secure API key management

See [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for detailed security information.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **spaCy** for powerful NLP capabilities
- **FastAPI** for the excellent web framework
- **Flutter** for cross-platform mobile development
- **Firebase** for push notification infrastructure

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/ajitreddy013/Deadline-Alert-Agent/issues) page
2. Review the [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for setup help
3. Create a new issue with detailed information

---

**Made with ❤️ for better deadline management**
