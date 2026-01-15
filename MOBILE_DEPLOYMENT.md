# Mobile Deployment Guide

## Backend Deployment to Railway

### Prerequisites
- Railway account (sign up at railway.app)
- GitHub repository connected

### Steps

1. **Install Railway CLI** (optional)
```bash
npm install -g @railway/cli
railway login
```

2. **Deploy via Railway Dashboard**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub"
   - Select your `Deadline-Alert-Agent` repository
   - Set root directory: `backend`

3. **Environment Variables** (Add in Railway Dashboard)
```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=groq
DATABASE_URL=sqlite:///./tasks.db
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

4. **Your Backend URL**
After deployment, Railway provides: `https://your-app.railway.app`

---

## Flutter App Update

### Update API Endpoint

Edit `deadline_alert_app/lib/main.dart`:

**Find:**
```dart
final response = await http.get(Uri.parse('http://localhost:8000/tasks'));
```

**Replace with:**
```dart
final response = await http.get(Uri.parse('https://your-app.railway.app/tasks'));
```

Do this for ALL API calls in the app.

---

## Build Android APK

```bash
cd deadline_alert_app
flutter build apk --release
```

APK location: `build/app/outputs/flutter-apk/app-release.apk`

---

## Install on Phone

### Option 1: USB
```bash
adb install build/app/outputs/flutter-apk/app-release.apk
```

### Option 2: File Transfer
1. Copy APK to phone
2. Open APK on phone
3. Allow "Install from unknown sources"
4. Install!

---

## Testing Checklist

- [ ] Backend accessible at Railway URL
- [ ] /llm/status endpoint working
- [ ] /chat endpoint working
- [ ] Gmail OAuth working
- [ ] Flutter app connects to cloud backend
- [ ] APK installed on phone
- [ ] Can view tasks on mobile
- [ ] Can chat with Groq AI on mobile
- [ ] Gmail sync works from mobile

---

## Troubleshooting

### Backend Issues
- Check Railway logs
- Verify environment variables set
- Test endpoints with curl/Postman

### Flutter Issues
- Ensure all localhost replaced with Railway URL
- Check internet permissions in AndroidManifest.xml
- Verify APK signed properly

### Mobile Issues
- Enable "Unknown sources" for APK install
- Check phone has internet connection
- Verify Google OAuth redirect URIs include Railway URL
