from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.deadline import StatusEnum, PriorityEnum, SourceEnum
from app.models.reminder_rule import ChannelEnum


class ReminderRuleBase(BaseModel):
    offset_seconds: int
    channel: ChannelEnum
    enabled: bool = True


class ReminderRuleCreate(ReminderRuleBase):
    pass


class ReminderRuleRead(ReminderRuleBase):
    id: str


class DeadlineBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_at: datetime
    status: StatusEnum = StatusEnum.pending
    priority: PriorityEnum = PriorityEnum.normal
    project: Optional[str] = None
    tags: Optional[str] = None


class DeadlineCreate(DeadlineBase):
    source: SourceEnum = SourceEnum.manual
    source_ref: Optional[str] = None
    source_url: Optional[str] = None
    confidence: Optional[float] = None
    reminder_rules: Optional[List[ReminderRuleCreate]] = None


class DeadlineUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    project: Optional[str] = None
    tags: Optional[str] = None


class DeadlineRead(DeadlineBase):
    id: str
    source: SourceEnum
    source_ref: Optional[str] = None
    source_url: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    reminder_rules: List[ReminderRuleRead] = Field(default_factory=list)

    class Config:
        use_enum_values = True
