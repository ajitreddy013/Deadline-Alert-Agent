from sqlalchemy import Column, String, Integer, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum
import uuid

from app.core.db import Base


class ChannelEnum(str, enum.Enum):
    desktop = "desktop"
    mobile = "mobile"
    whatsapp = "whatsapp"


class ReminderRule(Base):
    __tablename__ = "reminder_rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    deadline_id = Column(String, ForeignKey("deadlines.id", ondelete="CASCADE"), nullable=False)
    offset_seconds = Column(Integer, nullable=False)
    channel = Column(SAEnum(ChannelEnum), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)

    deadline = relationship("app.models.deadline.Deadline", back_populates="reminder_rules")
