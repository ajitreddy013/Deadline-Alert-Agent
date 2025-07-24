from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from .database import SessionLocal, engine
from .models import Task, Base
import spacy
import os
from .gmail_ingest import fetch_recent_emails
from .whatsapp_ingest import fetch_whatsapp_messages
from .notify import send_desktop_notification
from sqlalchemy import Column, Integer, String
from .onesignal_notify import send_onesignal_notification

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
        orm_mode = True

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