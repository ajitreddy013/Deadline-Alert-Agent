from sqlalchemy.orm import Session
from models import Task, UserPreferences, EmailAccount
from gmail_ingest import fetch_recent_emails
from whatsapp_ingest import fetch_whatsapp_messages
from notify import send_desktop_notification
from whatsapp_notify import send_deadline_reminder_whatsapp
import dateparser
from datetime import datetime, timezone
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64

# Use LLM provider instead of spacy for deadline extraction
from llm_deadline_extractor import extract_deadlines_with_llm

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service(email_account: EmailAccount):
    """Get authenticated Gmail service using refresh token"""
    creds = Credentials(
        None,
        refresh_token=email_account.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )
    
    if not creds.valid:
        creds.refresh(Request())
        
    return build('gmail', 'v1', credentials=creds)

def fetch_gmail_deadlines_oauth(service, email_address: str, category: str = "general"):
    """Fetch and process emails using Google Gmail API with LLM extraction"""
    query = 'newer_than:3d (deadline OR assignment OR meeting OR submit OR register)'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    extracted_tasks = []
    
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        
        # Get snippet or body
        snippet = msg_data.get('snippet', "")
        
        # Use LLM for intelligent deadline extraction
        message_text = f"{subject}\n{snippet}"
        deadlines = extract_deadlines_with_llm(message_text)
        
        # Add each extracted deadline as a task
        for deadline_info in deadlines:
            extracted_tasks.append({
                "summary": deadline_info.get("task", subject),
                "deadline": f"{deadline_info.get('date', '')} {deadline_info.get('time', '')}".strip(),
                "account": email_address,
                "category": category
            })
            
    return extracted_tasks

def ingest_all_gmail_accounts(db: Session):
    """Iterate through all active OAuth accounts and fetch deadlines"""
    accounts = db.query(EmailAccount).filter(EmailAccount.is_active == True).all()
    total_ingested = []
    
    for account in accounts:
        try:
            print(f"Syncing Gmail for: {account.email}")
            service = get_gmail_service(account)
            deadlines = fetch_gmail_deadlines_oauth(service, account.email, account.category)
            
            for d in deadlines:
                # Deduplication
                existing = db.query(Task).filter(
                    Task.summary == d['summary'], 
                    Task.source == "gmail"
                ).first()
                
                if not existing:
                    db_task = Task(
                        summary=d['summary'],
                        deadline=d['deadline'],
                        source="gmail",
                        alert_status="pending"
                    )
                    db.add(db_task)
                    total_ingested.append(d)
            
            account.last_sync = datetime.now()
            db.commit()
            
        except Exception as e:
            print(f"Failed to sync {account.email}: {e}")
            
    return total_ingested

def ingest_gmail_tasks(db: Session):
    """Legacy support for single account in .env, combined with multi-account logic"""
    # 1. First run the new multi-account logic
    results = ingest_all_gmail_accounts(db)
    
    # 2. Add fallback for the legacy .env account if it's still configured and not already in EmailAccount
    # (Optional: we could force migration instead)
    # Keeping it simple for now and just returning the new results.
    return results

def ingest_whatsapp_tasks(db: Session, chat_name: str):
    messages = fetch_whatsapp_messages(chat_name)
    results = []
    for msg_obj in messages:
        message = msg_obj["text"]
        
        # Use LLM for deadline extraction
        deadlines = extract_deadlines_with_llm(message)
        
        for deadline_info in deadlines:
            # Check if task already exists
            task_summary = deadline_info.get("task", message[:100])
            existing = db.query(Task).filter(Task.summary == task_summary, Task.source == "whatsapp").first()
            if existing:
                continue
                
            db_task = Task(
                summary=task_summary,
                deadline=f"{deadline_info.get('date', '')} {deadline_info.get('time', '')}".strip(),
                source="whatsapp",
                alert_status="pending"
            )
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            results.append({
                "message": message,
                "deadline": db_task.deadline,
                "task_id": db_task.id
            })
    return results

def check_and_notify_due_soon(db: Session, threshold_minutes: int = 60):
    now = datetime.now(timezone.utc)
    sent = []
    
    tasks = db.query(Task).filter(Task.alert_status == "pending").all()
    for task in tasks:
        if not task.deadline:
            continue
        try:
            parsed = dateparser.parse(
                task.deadline,
                settings={
                    "RETURN_AS_TIMEZONE_AWARE": True,
                    "PREFER_DATES_FROM": "future",
                },
            )
            if not parsed:
                continue
                
            due_at = parsed.astimezone(timezone.utc)
            delta = (due_at - now).total_seconds() / 60.0
            
            if 0 <= delta <= float(threshold_minutes):
                # Send Desktop notification
                send_desktop_notification(
                    title=f"Deadline soon: {task.summary}",
                    message=f"Due: {task.deadline}\nSource: {task.source}"
                )
                
                # Optionally send WhatsApp notification if preference is set
                prefs = db.query(UserPreferences).first()
                if prefs and prefs.whatsapp_notifications and prefs.whatsapp_number:
                    send_deadline_reminder_whatsapp(
                        to_number=prefs.whatsapp_number,
                        task_summary=task.summary,
                        deadline=task.deadline,
                        source=task.source
                    )
                
                task.alert_status = "sent"
                db.commit()
                sent.append(task.id)
        except Exception:
            continue
            
    return sent
