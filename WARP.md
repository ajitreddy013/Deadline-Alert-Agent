# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is an AI-powered deadline management system that automatically extracts deadlines from Gmail and WhatsApp messages, sends intelligent notifications, and helps users stay on top of important tasks. The system consists of a FastAPI backend with spaCy NLP processing, a Flutter cross-platform mobile app, and multiple notification channels.

## Architecture

The project follows a microservices architecture with clear separation between components:

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

### Key Components

- **Backend (`backend/`)**: Python FastAPI server with spaCy NLP, SQLAlchemy ORM, SQLite database
- **Frontend (`deadline_alert_app/`)**: Flutter cross-platform application for iOS, Android, Web, Desktop
- **Alternative Frontend (`gmail_whatsapp_deadlines/`)**: Second Flutter app implementation
- **Integration Services**: Gmail IMAP, WhatsApp Web scraping, push notifications

## Development Commands

### Backend Development

```bash
# Setup backend environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Environment setup
cp .env.template .env
# Edit .env with your credentials

# Start development server
python run_server.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs

# Run backend tests
python test_api.py
python test_gmail.py
python test_whatsapp.py
```

### Flutter Development

```bash
# Main Flutter app
cd deadline_alert_app
flutter pub get
flutter run

# Alternative implementation
cd gmail_whatsapp_deadlines
flutter pub get
flutter run -d chrome  # For web
flutter run -d macos   # For desktop

# Flutter platform-specific commands
flutter run -d chrome    # Web version
flutter run -d macos     # Desktop version
flutter devices          # List available devices
flutter analyze          # Code analysis
flutter build web        # Build for web
```

### Full Project Commands

```bash
# Quick project startup
./start_project.sh

# Run demo app
./run_app_demo.sh

# Comprehensive testing
python test_full_project.py
```

## Testing

### Backend Testing
- `python test_full_project.py` - Complete system test
- `python test_api.py` - API endpoints testing
- `python test_gmail.py` - Gmail integration testing
- `python test_whatsapp.py` - WhatsApp integration testing

### Flutter Testing
```bash
cd deadline_alert_app
flutter test
flutter analyze
```

## Environment Configuration

### Required Environment Variables (.env)
```bash
# Gmail Configuration
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-app-password  # Use Gmail App Password, not regular password

# Firebase Cloud Messaging
FCM_SERVER_KEY=your-fcm-server-key

# Database
DATABASE_URL=sqlite:///./tasks.db

# WhatsApp Notifications (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# OneSignal
ONESIGNAL_APP_ID=your-onesignal-app-id
```

### Gmail Setup Requirements
1. Enable 2-factor authentication on Gmail account
2. Generate app-specific password (not regular password)
3. Add credentials to `backend/.env`

## API Endpoints

### Core Endpoints
- `GET /tasks` - List all tasks
- `POST /tasks` - Create new task
- `POST /ingest/gmail` - Import deadlines from Gmail
- `POST /ingest/whatsapp` - Import deadlines from WhatsApp
- `POST /extract_deadline` - Extract deadlines from text using NLP
- `POST /notify/desktop/{id}` - Send desktop notification
- `POST /notify/mobile` - Send mobile notification
- `POST /user/preferences` - Manage user notification preferences

### API Documentation
- Interactive API docs available at `http://localhost:8000/docs` when server is running
- OpenAPI schema available at `http://localhost:8000/openapi.json`

## Database

### Models
- **Task**: Core deadline/task entity with summary, deadline, source, alert_status
- **UserPreferences**: User notification preferences (email, WhatsApp, desktop)
- **DeviceToken**: Mobile device tokens for push notifications

### Database Management
```bash
# Database file location
backend/tasks.db

# Access database directly (if needed)
sqlite3 backend/tasks.db
```

## Security Considerations

### Credential Protection
- Never commit `.env` files to version control
- Use Gmail App Passwords, not regular passwords
- Store all secrets in environment variables
- Refer to `SECURITY_GUIDE.md` for detailed security practices

### File Permissions
```bash
chmod 600 backend/.env
```

## NLP Processing

The system uses spaCy's `en_core_web_sm` model for:
- Date and time entity extraction
- Task keyword recognition
- Deadline pattern detection
- Smart content classification for emails and messages

## Notification Systems

### Supported Channels
- **Desktop**: Native macOS notifications via `notify.py`
- **Mobile**: Firebase Cloud Messaging (FCM) and OneSignal
- **WhatsApp**: Twilio API integration for WhatsApp notifications
- **Email**: SMTP notifications (configurable)

## Project Structure

```
├── backend/                    # FastAPI backend
│   ├── app.py                 # Main FastAPI application
│   ├── models.py              # SQLAlchemy database models
│   ├── gmail_ingest.py        # Gmail integration
│   ├── whatsapp_ingest.py     # WhatsApp integration
│   ├── notify.py              # Desktop notifications
│   └── run_server.py          # Server startup script
├── deadline_alert_app/         # Primary Flutter application
├── gmail_whatsapp_deadlines/   # Alternative Flutter implementation
├── data/                      # Data files and configurations
├── src/                       # Additional source files
├── start_project.sh           # Project startup script
├── test_full_project.py       # Comprehensive test suite
└── run_app_demo.sh           # Demo application runner
```

## Common Development Workflows

### Adding New API Endpoints
1. Define endpoint in `backend/app.py`
2. Add corresponding database models if needed in `backend/models.py`
3. Test with `python test_api.py`
4. Update API documentation

### Integrating New Message Sources
1. Create new ingestion module (similar to `gmail_ingest.py`)
2. Add API endpoint in `app.py`
3. Implement NLP processing for the new source
4. Add tests for the new integration

### Mobile App Development
1. Work in `deadline_alert_app/` for the main implementation
2. Use `flutter run -d chrome` for rapid web testing
3. Test on multiple platforms: `flutter devices`
4. Build for production: `flutter build [platform]`

## Dependencies

### Backend
- FastAPI 0.116+ (web framework)
- spaCy 3.8+ (NLP processing)
- SQLAlchemy 2.0+ (database ORM)
- python-dotenv (environment management)
- Twilio (WhatsApp notifications)

### Frontend
- Flutter 3.32+ (cross-platform framework)
- HTTP package (API communication)
- OneSignal Flutter (push notifications)

## Troubleshooting

### Common Issues
1. **Gmail authentication fails**: Ensure using App Password, not regular password
2. **spaCy model missing**: Run `python -m spacy download en_core_web_sm`
3. **Flutter build errors**: Run `flutter clean && flutter pub get`
4. **API not accessible**: Check if backend server is running on port 8000

### Debug Commands
```bash
# Check backend server health
curl http://localhost:8000/tasks

# Test Gmail connection
cd backend && python test_gmail.py

# Analyze Flutter app
cd deadline_alert_app && flutter analyze

# Check Flutter devices
flutter devices
```
