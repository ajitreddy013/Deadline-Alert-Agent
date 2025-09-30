from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.db import get_db
from app.models.deadline import Deadline
from app.models.reminder_rule import ReminderRule, ChannelEnum
from app.schemas.deadline import DeadlineCreate, DeadlineRead, DeadlineUpdate
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[DeadlineRead])
def list_deadlines(db: Session = Depends(get_db)):
    items = db.query(Deadline).order_by(Deadline.due_at.asc()).all()
    return items


@router.get("/{deadline_id}", response_model=DeadlineRead)
def get_deadline(deadline_id: str, db: Session = Depends(get_db)):
    item = db.get(Deadline, deadline_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.post("/", response_model=DeadlineRead, status_code=201)
def create_deadline(payload: DeadlineCreate, db: Session = Depends(get_db)):
    item = Deadline(
        title=payload.title,
        description=payload.description,
        due_at=payload.due_at,
        status=payload.status,
        priority=payload.priority,
        project=payload.project,
        tags=payload.tags,
        source=payload.source,
        source_ref=payload.source_ref,
        source_url=payload.source_url,
        confidence=payload.confidence,
    )
    db.add(item)
    db.flush()

    # Default reminder rules if none provided
    rules = payload.reminder_rules
    if not rules:
        for offs in settings.default_reminder_offsets:
            # Default to desktop and mobile channels
            db.add(ReminderRule(deadline_id=item.id, offset_seconds=offs, channel=ChannelEnum.desktop, enabled=True))
            db.add(ReminderRule(deadline_id=item.id, offset_seconds=offs, channel=ChannelEnum.mobile, enabled=True))
    else:
        for r in rules:
            db.add(ReminderRule(deadline_id=item.id, offset_seconds=r.offset_seconds, channel=r.channel, enabled=r.enabled))

    db.commit()
    db.refresh(item)
    return item


@router.put("/{deadline_id}", response_model=DeadlineRead)
def update_deadline(deadline_id: str, payload: DeadlineUpdate, db: Session = Depends(get_db)):
    item = db.get(Deadline, deadline_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{deadline_id}", status_code=204)
def delete_deadline(deadline_id: str, db: Session = Depends(get_db)):
    item = db.get(Deadline, deadline_id)
    if not item:
        return
    db.delete(item)
    db.commit()
