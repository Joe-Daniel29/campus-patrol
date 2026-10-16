from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import require_ingest_token
from ..metrics import EVENTS_TOTAL
from ..models import Event, Rover, Zone
from ..schemas import EventCreate, EventOut, Severity

router = APIRouter(tags=["events"])


@router.get("/api/events", response_model=list[EventOut])
def list_events(
    severity: Severity | None = None,
    rover_id: int | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = select(Event).order_by(Event.created_at.desc(), Event.id.desc()).limit(limit)
    if severity:
        query = query.where(Event.severity == severity)
    if rover_id:
        query = query.where(Event.rover_id == rover_id)
    return list(db.scalars(query).unique())


@router.post(
    "/api/events",
    response_model=EventOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_ingest_token)],
)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    rover = db.scalar(select(Rover).where(Rover.name == payload.rover))
    if not rover:
        raise HTTPException(status_code=404, detail="Unknown rover")
    zone = None
    if payload.zone:
        zone = db.scalar(select(Zone).where(Zone.name == payload.zone))
        if not zone:
            raise HTTPException(status_code=404, detail="Unknown zone")
    event = Event(
        rover_id=rover.id,
        zone_id=zone.id if zone else None,
        type=payload.type,
        severity=payload.severity,
        confidence=payload.confidence,
        message=payload.message,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    EVENTS_TOTAL.labels(type=event.type, severity=event.severity).inc()
    return event
