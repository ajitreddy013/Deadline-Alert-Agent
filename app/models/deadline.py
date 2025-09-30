from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from sqlalchemy.dialects.sqlite import BLOB


class StatusEnum(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    done = "done"


class PriorityEnum(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    critical = "critical"


class SourceEnum(str, enum.Enum):
    manual = "manual"
    whatsapp = "whatsapp"
    email = "email"


from app.core.db import Base


class Deadline(Base):
    __tablename__ = "deadlines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(SAEnum(StatusEnum), nullable=False, default=StatusEnum.pending)
    priority = Column(SAEnum(PriorityEnum), nullable=False, default=PriorityEnum.normal)
    project = Column(String, nullable=True)
    source = Column(SAEnum(SourceEnum), nullable=False, default=SourceEnum.manual)
    source_ref = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    tags = Column(String, nullable=True)  # comma-separated for now

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reminder_rules = relationship(
        "app.models.reminder_rule.ReminderRule",
        back_populates="deadline",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
