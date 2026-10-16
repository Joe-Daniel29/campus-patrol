from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import require_ingest_token
from ..metrics import TELEMETRY_TOTAL
from ..models import Rover, utcnow
from ..schemas import RoverCreate, RoverOut, RoverUpdate, Telemetry

router = APIRouter(tags=["rovers"])


@router.get("/api/rovers", response_model=list[RoverOut])
def list_rovers(db: Session = Depends(get_db)):
    return list(db.scalars(select(Rover).order_by(Rover.name)))


@router.get("/api/rovers/{rover_id}", response_model=RoverOut)
def get_rover(rover_id: int, db: Session = Depends(get_db)):
    rover = db.get(Rover, rover_id)
    if not rover:
        raise HTTPException(status_code=404, detail="Rover not found")
    return rover


@router.post("/api/rovers", response_model=RoverOut, status_code=status.HTTP_201_CREATED)
def create_rover(payload: RoverCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Rover).where(Rover.name == payload.name)):
        raise HTTPException(status_code=409, detail="Rover name already exists")
    rover = Rover(**payload.model_dump())
    db.add(rover)
    db.commit()
    db.refresh(rover)
    return rover


@router.put("/api/rovers/{rover_id}", response_model=RoverOut)
def update_rover(rover_id: int, payload: RoverUpdate, db: Session = Depends(get_db)):
    rover = db.get(Rover, rover_id)
    if not rover:
        raise HTTPException(status_code=404, detail="Rover not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(rover, key, value)
    db.commit()
    db.refresh(rover)
    return rover


@router.delete("/api/rovers/{rover_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rover(rover_id: int, db: Session = Depends(get_db)):
    rover = db.get(Rover, rover_id)
    if not rover:
        raise HTTPException(status_code=404, detail="Rover not found")
    db.delete(rover)
    db.commit()


@router.post(
    "/api/telemetry",
    response_model=RoverOut,
    dependencies=[Depends(require_ingest_token)],
)
def ingest_telemetry(payload: Telemetry, db: Session = Depends(get_db)):
    """Heartbeat from a rover. Unknown rovers are registered on first contact."""
    rover = db.scalar(select(Rover).where(Rover.name == payload.rover))
    if not rover:
        rover = Rover(name=payload.rover)
        db.add(rover)
    rover.x, rover.y, rover.heading = payload.x, payload.y, payload.heading
    rover.battery, rover.status = payload.battery, payload.status
    rover.last_seen = utcnow()
    db.commit()
    db.refresh(rover)
    TELEMETRY_TOTAL.inc()
    return rover
