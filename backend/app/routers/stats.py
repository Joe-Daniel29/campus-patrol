from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Event, Incident, Rover, utcnow
from ..schemas import StatsOut

router = APIRouter(tags=["stats"])


@router.get("/api/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    rovers = list(db.scalars(select(Rover)))
    since = utcnow() - timedelta(hours=1)
    by_type = db.execute(
        select(Event.type, func.count(Event.id)).where(Event.created_at >= since).group_by(Event.type)
    ).all()
    open_incidents = db.scalar(select(func.count(Incident.id)).where(Incident.status != "RESOLVED"))
    return StatsOut(
        rovers_total=len(rovers),
        rovers_online=sum(1 for r in rovers if r.online),
        incidents_open=open_incidents or 0,
        events_last_hour=sum(count for _, count in by_type),
        events_by_type={name: count for name, count in by_type},
    )
