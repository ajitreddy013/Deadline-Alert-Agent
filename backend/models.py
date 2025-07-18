from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String, nullable=False)
    deadline = Column(String, nullable=True)
    source = Column(String, nullable=False)  # e.g., 'gmail', 'whatsapp'
    alert_status = Column(String, default="pending")  # 'sent' or 'pending' 