from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from .database import SessionLocal
from .models import Task
import spacy

nlp = spacy.load("en_core_web_sm")

app = FastAPI()

# Dependency to get DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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