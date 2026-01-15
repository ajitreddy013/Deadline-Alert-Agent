from fastapi import FastAPI, Depends, HTTPException, Body
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
from database import SessionLocal, engine
from models import Task, Base, UserPreferences, EmailAccount
from service import ingest_gmail_tasks, ingest_whatsapp_tasks, check_and_notify_due_soon, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SCOPES
from sqlalchemy import Column, Integer, String
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware
from notify import send_desktop_notification
from whatsapp_notify import send_whatsapp_notification, send_deadline_reminder_whatsapp, validate_whatsapp_number
from onesignal_notify import send_onesignal_notification
from fcm_notify import send_fcm_notification
from google_auth_oauthlib.flow import Flow
from fastapi.responses import RedirectResponse, HTMLResponse
from urllib.parse import urlencode
from chat_handler import chat_with_deadlines, get_llm_status
import requests
import os

Base.metadata.create_all(bind=engine)

def periodic_gmail_ingest():
    db = SessionLocal()
    try:
        print("Running scheduled Gmail ingestion...")
        ingest_gmail_tasks(db)
    except Exception as e:
        print(f"Error in scheduled Gmail ingestion: {e}")
    finally:
        db.close()

def periodic_whatsapp_ingest():
    db = SessionLocal()
    try:
        prefs = db.query(UserPreferences).first()
        if prefs and prefs.whatsapp_chat_name:
            print(f"Running scheduled WhatsApp ingestion for chat: {prefs.whatsapp_chat_name}")
            ingest_whatsapp_tasks(db, prefs.whatsapp_chat_name)
    except Exception as e:
        print(f"Error in scheduled WhatsApp ingestion: {e}")
    finally:
        db.close()

def periodic_due_soon_check():
    db = SessionLocal()
    try:
        print("Running scheduled due-soon check...")
        check_and_notify_due_soon(db)
    except Exception as e:
        print(f"Error in scheduled due-soon check: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler
    scheduler = BackgroundScheduler()
    
    # Ingest Gmail every 15 minutes
    scheduler.add_job(periodic_gmail_ingest, 'interval', minutes=15)
    
    # Check for due tasks every 5 minutes
    scheduler.add_job(periodic_due_soon_check, 'interval', minutes=5)
    
    # Ingest WhatsApp every 30 minutes (if configured)
    scheduler.add_job(periodic_whatsapp_ingest, 'interval', minutes=30)
    
    scheduler.start()
    print("Background scheduler started.")
    
    yield
    
    # Shutdown scheduler
    scheduler.shutdown()
    print("Background scheduler shut down.")

app = FastAPI(lifespan=lifespan)

# Enable CORS for local development (Flutter web in Chrome)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:7357",
        "http://127.0.0.1:7357",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DeviceToken(Base):
    __tablename__ = "device_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)

class EmailAccountRead(BaseModel):
    id: int
    email: str
    account_name: Optional[str]
    category: str
    is_active: bool
    last_sync: Optional[datetime]

    class Config:
        from_attributes = True

class EmailAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class TokenExchangeRequest(BaseModel):
    code: str
    email: str
    account_name: Optional[str] = "Personal"

class TaskCreate(BaseModel):
    summary: str
    deadline: str = None  # ISO format string or natural language
    source: str
    alert_status: str = "pending"

class TaskRead(BaseModel):
    id: int
    summary: str
    deadline: str = None
    source: str
    alert_status: str

    class Config:
        from_attributes = True

@app.get("/tasks", response_model=List[TaskRead])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.post("/tasks", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        summary=task.summary,
        deadline=task.deadline,
        source=task.source,
        alert_status=task.alert_status
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.post("/extract_deadline")
def extract_deadline(message: str = Body(..., embed=True)):
    """Extract deadlines using LLM provider"""
    from llm_deadline_extractor import extract_deadlines_with_llm
    
    deadlines = extract_deadlines_with_llm(message)
    
    # Format response to match legacy format
    dates = [d.get('date', '') for d in deadlines]
    tasks = [d.get('task', '') for d in deadlines]
    
    return {
        "deadlines": deadlines,  # Full structured data
        "dates": dates,  # Legacy format
        "tasks": tasks,  # Legacy format
    }

@app.post("/ingest/gmail")
def ingest_gmail(db: Session = Depends(get_db)):
    results = ingest_gmail_tasks(db)
    return {"ingested": results}

@app.post("/ingest/whatsapp")
def ingest_whatsapp(chat_name: str, db: Session = Depends(get_db)):
    results = ingest_whatsapp_tasks(db, chat_name)
    return {"ingested": results}

@app.post("/notify/desktop/{task_id}")
def notify_desktop(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return {"error": "Task not found"}
    send_desktop_notification(
        title=f"Deadline Alert: {task.summary}",
        message=f"Due: {task.deadline}\nSource: {task.source}"
    )
    return {"status": "notification sent"}

@app.post("/notify/mobile")
def notify_mobile(player_id: str, title: str, message: str):
    result = send_onesignal_notification(player_id, title, message)
    return {"result": result}

@app.post("/notify/mobile/fcm")
def notify_mobile_fcm(device_token: str, title: str, message: str):
    """Send a mobile push using FCM legacy HTTP with a device registration token."""
    result = send_fcm_notification(device_token, title, message)
    return {"result": result}

@app.post("/notify/due-soon")
def notify_due_soon(threshold_minutes: int = 60, db: Session = Depends(get_db)):
    sent = check_and_notify_due_soon(db, threshold_minutes)
    return {"sent": sent, "threshold_minutes": threshold_minutes}

# --- Google OAuth Endpoints ---

@app.get("/auth/google/login")
async def google_login():
    """Initial OAuth step: Redirect user to Google's consent screen."""
    backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
    redirect_uri = f"{backend_url.rstrip('/')}/auth/google/callback"
    
    print(f"DEBUG: Starting login. Backend URL: {backend_url}")
    print(f"DEBUG: Client ID: {GOOGLE_CLIENT_ID[:10] if GOOGLE_CLIENT_ID else 'MISSING'}...")
    
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID not configured in environment variables")
    
    # We use offline access to get a refresh token
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

@app.get("/auth/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Second OAuth step: Google redirects here with a code."""
    backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
    redirect_uri = f"{backend_url.rstrip('/')}/auth/google/callback"
    
    try:
        # 1. Prepare the flow to exchange the code
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            # Match the scopes used in /login exactly
            scopes=["openid", "email", "profile", "https://www.googleapis.com/auth/gmail.readonly"],
            redirect_uri=redirect_uri
        )
        
        # 2. Exchange code for token
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # 3. Get user info
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {creds.token}"}
        user_info_resp = requests.get(user_info_url, headers=headers)
        user_info = user_info_resp.json()
        
        email = user_info.get("email")
        name = user_info.get("name", "Personal")

        # 4. Store in database
        account = db.query(EmailAccount).filter(EmailAccount.email == email).first()
        if account:
            account.refresh_token = creds.refresh_token or account.refresh_token
            account.is_active = True
        else:
            account = EmailAccount(
                email=email,
                refresh_token=creds.refresh_token,
                account_name=name,
                category="gmail_oauth"
            )
            db.add(account)
        
        db.commit()
        
        # 5. Return success HTML
        return HTMLResponse(content=f"""
            <html>
                <body style="font-family: sans-serif; text-align: center; padding-top: 100px; background-color: #f4f4f9;">
                    <div style="display: inline-block; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <h1 style="color: #4CAF50;">Successfully Connected!</h1>
                        <p style="font-size: 1.2em; color: #555;">Account: <strong>{email}</strong></p>
                        <p>You can now close this window and refresh your app settings.</p>
                        <button onclick="window.close()" style="margin-top: 20px; padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 5px; cursor: pointer;">Close Window</button>
                    </div>
                </body>
            </html>
        """)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Connection Error</h1><p>{str(e)}</p>", status_code=500)

@app.post("/auth/google/exchange")
def exchange_google_code(req: TokenExchangeRequest, db: Session = Depends(get_db)):
    """Exchange auth code for refresh token and store it"""
    try:
        # Note: In a real production app, the redirect_uri must match what was registered
        # and what the Flutter app used. For Flutter Web/Mobile, 'postmessage' or a custom scheme is common.
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
            redirect_uri='postmessage' # Standard for server-side exchange from mobile/web
        )
        
        flow.fetch_token(code=req.code)
        creds = flow.credentials
        
        if not creds.refresh_token:
            # If no refresh token, we might need to prompt for 'offline' access again
            return {"error": "No refresh token received. Ensure access_type='offline' and prompt='consent'"}

        # Check if already exists
        account = db.query(EmailAccount).filter(EmailAccount.email == req.email).first()
        if account:
            account.refresh_token = creds.refresh_token
        else:
            account = EmailAccount(
                email=req.email,
                account_name=req.account_name,
                refresh_token=creds.refresh_token
            )
            db.add(account)
        
        db.commit()
        return {"status": "success", "email": req.email}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/accounts", response_model=List[EmailAccountRead])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(EmailAccount).all()

@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"status": "deleted"}

# WhatsApp Notification Endpoints
class UserPreferencesCreate(BaseModel):
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email_notifications: bool = True
    whatsapp_notifications: bool = False
    desktop_notifications: bool = True
    whatsapp_chat_name: Optional[str] = None

class UserPreferencesRead(BaseModel):
    id: int
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email_notifications: bool
    whatsapp_notifications: bool
    desktop_notifications: bool
    whatsapp_chat_name: Optional[str] = None

    class Config:
        from_attributes = True

@app.post("/user/preferences", response_model=UserPreferencesRead)
def create_or_update_user_preferences(preferences: UserPreferencesCreate, db: Session = Depends(get_db)):
    """Create or update user notification preferences"""
    
    # Validate WhatsApp number if provided
    if preferences.whatsapp_number:
        validated_number = validate_whatsapp_number(preferences.whatsapp_number)
        if not validated_number:
            raise HTTPException(status_code=400, detail="Invalid WhatsApp number format. Use international format like +1234567890")
        preferences.whatsapp_number = validated_number
    
    # Check if preferences already exist (assuming one user for now)
    existing = db.query(UserPreferences).first()
    
    if existing:
        # Update existing preferences
        for field, value in preferences.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new preferences
        db_preferences = UserPreferences(**preferences.model_dump())
        db.add(db_preferences)
        db.commit()
        db.refresh(db_preferences)
        return db_preferences

@app.get("/user/preferences", response_model=UserPreferencesRead)
def get_user_preferences(db: Session = Depends(get_db)):
    """Get user notification preferences"""
    preferences = db.query(UserPreferences).first()
    if not preferences:
        # Return default preferences
        return UserPreferencesRead(
            id=0,
            email=None,
            whatsapp_number=None,
            email_notifications=True,
            whatsapp_notifications=False,
            desktop_notifications=True,
            whatsapp_chat_name=None
        )
    return preferences

@app.post("/notify/whatsapp/{task_id}")
def notify_whatsapp_task(task_id: int, db: Session = Depends(get_db)):
    """Send WhatsApp notification for a specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get user preferences
    preferences = db.query(UserPreferences).first()
    if not preferences or not preferences.whatsapp_notifications or not preferences.whatsapp_number:
        raise HTTPException(status_code=400, detail="WhatsApp notifications not configured or disabled")
    
    result = send_deadline_reminder_whatsapp(
        to_number=preferences.whatsapp_number,
        task_summary=task.summary,
        deadline=task.deadline or "No deadline specified",
        source=task.source
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp notification: {result['error']}")
    
    return {"status": "WhatsApp notification sent", "result": result}

@app.post("/notify/whatsapp")
def notify_whatsapp_custom(to_number: str, title: str, message: str):
    """Send custom WhatsApp notification"""
    validated_number = validate_whatsapp_number(to_number)
    if not validated_number:
        raise HTTPException(status_code=400, detail="Invalid WhatsApp number format")
    
    result = send_whatsapp_notification(validated_number, title, message)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp notification: {result['error']}")
    
    return {"status": "WhatsApp notification sent", "result": result}

@app.post("/notify/all/{task_id}")
def notify_all_channels(task_id: int, db: Session = Depends(get_db)):
    """Send notifications through all enabled channels for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get user preferences
    preferences = db.query(UserPreferences).first()
    results = {}
    
    # Desktop notification
    if not preferences or preferences.desktop_notifications:
        try:
            send_desktop_notification(
                title=f"Deadline Alert: {task.summary}",
                message=f"Due: {task.deadline or 'No deadline specified'}\nSource: {task.source}"
            )
            results["desktop"] = "sent"
        except Exception as e:
            results["desktop"] = f"failed: {str(e)}"
    
    # WhatsApp notification
    if preferences and preferences.whatsapp_notifications and preferences.whatsapp_number:
        try:
            whatsapp_result = send_deadline_reminder_whatsapp(
                to_number=preferences.whatsapp_number,
                task_summary=task.summary,
                deadline=task.deadline or "No deadline specified",
                source=task.source
            )
            if "error" in whatsapp_result:
                results["whatsapp"] = f"failed: {whatsapp_result['error']}"
            else:
                results["whatsapp"] = "sent"
        except Exception as e:
            results["whatsapp"] = f"failed: {str(e)}"
    else:
        results["whatsapp"] = "disabled or not configured"
    
    # Update task alert status
    task.alert_status = "sent"
    db.commit()
    
    return {"status": "notifications processed", "results": results}

# LLM Endpoints
@app.get("/llm/status")
def llm_status():
    """Check which LLM providers are available and get suggested questions"""
    return get_llm_status()

@app.post("/chat")
def chat_endpoint(question: str, db: Session = Depends(get_db)):
    """Chat with your deadlines using LLM"""
    tasks = db.query(Task).all()
    response = chat_with_deadlines(question, tasks)
    return response

if __name__ == "__main__":
    import uvicorn
    # Bind to loopback for local-only access by default
    uvicorn.run(app, host="127.0.0.1", port=8000)
