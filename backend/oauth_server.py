#!/usr/bin/env python3
"""
OAuth Server for Deadline Reminder - Minimal server for Google OAuth
Runs on port 8000 for OAuth callbacks, while Flutter app runs on port 8080
"""

import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional
from google_auth_oauthlib.flow import Flow
import requests

# Import Gmail ingestion
try:
    from gmail_oauth_ingest import ingest_gmail_for_account
    GMAIL_INGEST_AVAILABLE = True
except ImportError:
    GMAIL_INGEST_AVAILABLE = False
    print("Warning: Gmail ingestion not available")

# Import LLM features
try:
    from chat_handler import chat_with_deadlines, suggest_questions
    from llm_deadline_extractor import check_ollama_availability
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM features not available")

# Load environment
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String, nullable=False)
    deadline = Column(String, nullable=True)
    source = Column(String, nullable=False)
    alert_status = Column(String, default="pending")

class EmailAccount(Base):
    __tablename__ = "email_accounts"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    account_name = Column(String, nullable=True)
    category = Column(String, default="general")
    refresh_token = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# App setup
app = FastAPI(title="Deadline Reminder OAuth Server")

# Enable CORS - Allow Flutter web app on port 8080
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google OAuth config
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

@app.get("/")
async def root():
    return {
        "message": "Deadline Reminder OAuth Server",
        "version": "1.0",
        "oauth_endpoint": "/auth/google/login",
        "flutter_app": "http://localhost:8080"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# --- Google OAuth Endpoints ---

@app.get("/auth/google/login")
async def google_login():
    """Initial OAuth step: Redirect user to Google's consent screen."""
    print(f"DEBUG: Starting login with Client ID: {GOOGLE_CLIENT_ID[:10] if GOOGLE_CLIENT_ID else 'None'}...")
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID not configured")
    
    # We use offline access to get a refresh token
    # Use full scope URIs to match what Google returns
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": "http://localhost:8000/auth/google/callback",
        "response_type": "code",
        "scope": "openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/gmail.readonly",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

@app.get("/auth/google/callback")
async def google_callback(code: str = None, error: str = None, db: Session = Depends(get_db)):
    """Second OAuth step: Google redirects here with a code."""
    if error:
        return HTMLResponse(content=f"""
            <html>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #f44336;">OAuth Error</h1>
                    <p>{error}</p>
                    <button onclick="window.close()">Close</button>
                </body>
            </html>
        """, status_code=400)
    
    if not code:
        return HTMLResponse(content="""
            <html>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1>Error</h1>
                    <p>No authorization code received</p>
                    <button onclick="window.close()">Close</button>
                </body>
            </html>
        """, status_code=400)
    
    try:
        # Exchange authorization code for tokens manually (avoid strict scope validation)
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": "http://localhost:8000/auth/google/callback",
            "grant_type": "authorization_code"
        }
        
        # Get tokens
        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code != 200:
            raise Exception(f"Token exchange failed: {token_response.text}")
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        if not access_token:
            raise Exception("No access token received")
        
        # 3. Get user info
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_resp = requests.get(user_info_url, headers=headers)
        
        if user_info_resp.status_code != 200:
            raise Exception(f"Failed to get user info: {user_info_resp.text}")
            
        user_info = user_info_resp.json()
        
        email = user_info.get("email")
        name = user_info.get("name", "Personal")

        # 4. Store in database
        account = db.query(EmailAccount).filter(EmailAccount.email == email).first()
        if account:
            # Update existing account
            if refresh_token:  # Only update if we got a new refresh token
                account.refresh_token = refresh_token
            account.is_active = True
            account.last_sync = datetime.now()
        else:
            # Create new account
            if not refresh_token:
                raise Exception("No refresh token received for new account. Please try again.")
            account = EmailAccount(
                email=email,
                refresh_token=refresh_token,
                account_name=name,
                category="gmail_oauth",
                last_sync=datetime.now()
            )
            db.add(account)
        
        db.commit()
        
        # 5. Return success HTML
        return HTMLResponse(content=f"""
            <html>
                <body style="font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 100px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin: 0;">
                    <div style="display: inline-block; padding: 40px; background: rgba(255,255,255,0.95); border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); color: #333;">
                        <div style="font-size: 4em; margin-bottom: 20px;">✅</div>
                        <h1 style="color: #4CAF50; margin: 10px 0;">Successfully Connected!</h1>
                        <p style="font-size: 1.2em; color: #555; margin: 20px 0;">
                            Account: <strong style="color: #667eea;">{email}</strong>
                        </p>
                        <p style="color: #666; margin: 20px 0;">
                            Your Gmail account is now connected to the Deadline Reminder app.<br>
                            You can now close this window and return to the app.
                        </p>
                        <button onclick="window.close()" style="margin-top: 30px; padding: 15px 40px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 50px; font-size: 1.1em; cursor: pointer; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); transition: all 0.3s;">
                            Close Window
                        </button>
                        <p style="margin-top: 30px; font-size: 0.9em; color: #999;">
                            <a href="http://localhost:8080" style="color: #667eea; text-decoration: none;">← Back to Deadline Reminder App</a>
                        </p>
                    </div>
                </body>
            </html>
        """)
    except Exception as e:
        print(f"ERROR in OAuth callback: {str(e)}")
        return HTMLResponse(content=f"""
            <html>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #f44336;">Connection Error</h1>
                    <p>Failed to connect your Gmail account.</p>
                    <pre style="text-align: left; background: #f5f5f5; padding: 20px; border-radius: 5px;">{str(e)}</pre>
                    <button onclick="window.close()" style="margin-top: 20px; padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        Close Window
                    </button>
                </body>
            </html>
        """, status_code=500)

@app.get("/accounts")
async def list_accounts(db: Session = Depends(get_db)):
    """List all connected email accounts"""
    accounts = db.query(EmailAccount).all()
    return [{
        "id": acc.id,
        "email": acc.email,
        "account_name": acc.account_name,
        "category": acc.category,
        "is_active": acc.is_active,
        "last_sync": acc.last_sync.isoformat() if acc.last_sync else None
    } for acc in accounts]

@app.delete("/accounts/{account_id}")
async def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Delete a connected account"""
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"status": "deleted", "email": account.email}

@app.get("/tasks")
async def list_tasks(db: Session = Depends(get_db)):
    """List all tasks"""
    tasks = db.query(Task).all()
    return tasks

@app.post("/ingest/gmail")
async def ingest_gmail(db: Session = Depends(get_db)):
    """Ingest emails from all connected Gmail accounts"""
    if not GMAIL_INGEST_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gmail ingestion not available. Check dependencies.")
    
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth credentials not configured")
    
    # Get all active accounts
    accounts = db.query(EmailAccount).filter(EmailAccount.is_active == True).all()
    
    if not accounts:
        return {
            "status": "no_accounts",
            "message": "No active Gmail accounts connected",
            "tasks_created": 0
        }
    
    results = []
    total_tasks = 0
    
    for account in accounts:
        try:
            tasks_created = ingest_gmail_for_account(
                account,
                GOOGLE_CLIENT_ID,
                GOOGLE_CLIENT_SECRET,
                db
            )
            results.append({
                "email": account.email,
                "status": "success",
                "tasks_created": len(tasks_created),
                "tasks": tasks_created
            })
            total_tasks += len(tasks_created)
        except Exception as e:
            results.append({
                "email": account.email,
                "status": "error",
                "error": str(e),
                "tasks_created": 0
            })
    
    return {
        "status": "completed",
        "accounts_processed": len(accounts),
        "total_tasks_created": total_tasks,
        "results": results
    }

@app.get("/llm/status")
async def llm_status():
    """Check LLM availability and status"""
    if not LLM_AVAILABLE:
        return {
            "available": False,
            "reason": "LLM modules not loaded",
            "install_instructions": "Install Ollama from https://ollama.ai and run: pip install ollama"
        }
    
    status = check_ollama_availability()
    status["suggested_questions"] = suggest_questions()
    return status

@app.post("/chat")
async def chat_endpoint(question: str, db: Session = Depends(get_db)):
    """Chat with your deadlines using LLM"""
    if not LLM_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chat feature requires Ollama. Install from https://ollama.ai"
        )
    
    # Get all tasks
    tasks = db.query(Task).all()
    
    # Generate response
    response = chat_with_deadlines(question, tasks)
    
    return response

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Deadline Reminder OAuth Server...")
    print("📍 Backend: http://localhost:8000")
    print("📱 Flutter App: http://localhost:8080")
    print("🔐 OAuth Callback: http://localhost:8000/auth/google/callback")
    print("📚 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
