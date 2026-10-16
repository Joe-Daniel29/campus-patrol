from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Zone
from ..schemas import ZoneCreate, ZoneOut

router = APIRouter(tags=["zones"])


@router.get("/api/zones", response_model=list[ZoneOut])
def list_zones(db: Session = Depends(get_db)):
    return list(db.scalars(select(Zone).order_by(Zone.name)))


@router.post("/api/zones", response_model=ZoneOut, status_code=status.HTTP_201_CREATED)
def create_zone(payload: ZoneCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Zone).where(Zone.name == payload.name)):
        raise HTTPException(status_code=409, detail="Zone name already exists")
    zone = Zone(**payload.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.delete("/api/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(zone_id: int, db: Session = Depends(get_db)):
    zone = db.get(Zone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    db.delete(zone)
    db.commit()
