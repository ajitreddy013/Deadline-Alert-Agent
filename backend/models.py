from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String, nullable=False)
    deadline = Column(String, nullable=True)
    source = Column(String, nullable=False)  # e.g., 'gmail', 'whatsapp'
    alert_status = Column(String, default="pending")  # 'sent' or 'pending'
    
class UserPreferences(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=True)
    whatsapp_number = Column(String, nullable=True)  # Format: +1234567890
    email_notifications = Column(Boolean, default=True)
    whatsapp_notifications = Column(Boolean, default=False)
    desktop_notifications = Column(Boolean, default=True)
