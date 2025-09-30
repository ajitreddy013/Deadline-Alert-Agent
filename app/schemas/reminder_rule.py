from pydantic import BaseModel
from app.models.reminder_rule import ChannelEnum


class ReminderRuleCreate(BaseModel):
    offset_seconds: int
    channel: ChannelEnum
    enabled: bool = True
