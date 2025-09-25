from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal, engine
from models import Task, Base, UserPreferences
import spacy
import os
from gmail_ingest import fetch_recent_emails
from whatsapp_ingest import fetch_whatsapp_messages
from notify import send_desktop_notification
from whatsapp_notify import send_whatsapp_notification, send_deadline_reminder_whatsapp, validate_whatsapp_number
from sqlalchemy import Column, Integer, String
from onesignal_notify import send_onesignal_notification

Base.metadata.create_all(bind=engine)

nlp = spacy.load("en_core_web_sm")

app = FastAPI()

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

class TaskCreate(BaseModel):
    summary: str
    deadline: str = None  # ISO format string
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
    doc = nlp(message)
    dates = []
    tasks = []
    hackathons = []
    # Extract date/time entities
    for ent in doc.ents:
        if ent.label_ in ["DATE", "TIME"]:
            dates.append(ent.text)
    # Simple keyword-based extraction for tasks/hackathons
    task_keywords = ["assignment", "meeting", "test", "task", "reminder"]
    hackathon_keywords = ["hackathon", "register", "submit", "deadline"]
    lower_msg = message.lower()
    for word in task_keywords:
        if word in lower_msg:
            tasks.append(word)
    for word in hackathon_keywords:
        if word in lower_msg:
            hackathons.append(word)
    return {
        "dates": dates,
        "tasks": tasks,
        "hackathons": hackathons
    }

@app.post("/ingest/gmail")
def ingest_gmail(db: Session = Depends(get_db)):
    emails = fetch_recent_emails()
    results = []
    for email_obj in emails:
        message = f"{email_obj['subject']}\n{email_obj['body']}"
        doc = nlp(message)
        dates = [ent.text for ent in doc.ents if ent.label_ in ["DATE", "TIME"]]
        if dates:
            db_task = Task(
                summary=email_obj['subject'],
                deadline=dates[0],
                source="gmail",
                alert_status="pending"
            )
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            results.append({
                "subject": email_obj['subject'],
                "deadline": dates[0],
                "task_id": db_task.id
            })
    return {"ingested": results}

@app.post("/ingest/whatsapp")
def ingest_whatsapp(chat_name: str, db: Session = Depends(get_db)):
    messages = fetch_whatsapp_messages(chat_name)
    results = []
    for msg_obj in messages:
        message = msg_obj["text"]
        doc = nlp(message)
        dates = [ent.text for ent in doc.ents if ent.label_ in ["DATE", "TIME"]]
        if dates:
            db_task = Task(
                summary=message[:100],
                deadline=dates[0],
                source="whatsapp",
                alert_status="pending"
            )
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            results.append({
                "message": message,
                "deadline": dates[0],
                "task_id": db_task.id
            })
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

@app.post("/register_token")
def register_token(token: str, db: Session = Depends(get_db)):
    if db.query(DeviceToken).filter(DeviceToken.token == token).first():
        return {"status": "already registered"}
    db_token = DeviceToken(token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return {"status": "registered", "id": db_token.id}

# WhatsApp Notification Endpoints
class UserPreferencesCreate(BaseModel):
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email_notifications: bool = True
    whatsapp_notifications: bool = False
    desktop_notifications: bool = True

class UserPreferencesRead(BaseModel):
    id: int
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email_notifications: bool
    whatsapp_notifications: bool
    desktop_notifications: bool

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
            desktop_notifications=True
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
