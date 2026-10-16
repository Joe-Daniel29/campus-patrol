from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RoverStatus = Literal["IDLE", "PATROLLING", "CHARGING", "RESPONDING", "OFFLINE"]
Severity = Literal["INFO", "WARNING", "CRITICAL"]
IncidentStatus = Literal["OPEN", "ACKNOWLEDGED", "RESOLVED"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- zones ---
class ZoneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = ""
    x: float = 0
    y: float = 0
    width: float = Field(default=50, gt=0)
    height: float = Field(default=50, gt=0)


class ZoneOut(ORM, ZoneCreate):
    id: int


# --- rovers ---
class RoverCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    status: RoverStatus = "IDLE"
    battery: float = Field(default=100, ge=0, le=100)
    x: float = 0
    y: float = 0


class RoverUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    status: RoverStatus | None = None
    battery: float | None = Field(default=None, ge=0, le=100)


class RoverOut(ORM):
    id: int
    name: str
    status: RoverStatus
    battery: float
    x: float
    y: float
    heading: float
    last_seen: datetime | None
    online: bool


class Telemetry(BaseModel):
    rover: str = Field(min_length=1, max_length=80)
    x: float
    y: float
    heading: float = 0
    battery: float = Field(ge=0, le=100)
    status: RoverStatus = "PATROLLING"


# --- events ---
class EventCreate(BaseModel):
    rover: str
    zone: str | None = None
    type: str = Field(min_length=1, max_length=40)
    severity: Severity = "INFO"
    confidence: float = Field(default=1.0, ge=0, le=1)
    message: str = ""


class EventOut(ORM):
    id: int
    rover_name: str
    zone_name: str | None
    type: str
    severity: Severity
    confidence: float
    message: str
    created_at: datetime


# --- incidents ---
class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = ""
    severity: Severity = "WARNING"
    zone_id: int | None = None
    event_id: int | None = None
    assignee: str | None = None


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    status: IncidentStatus | None = None
    severity: Severity | None = None
    assignee: str | None = None


class IncidentOut(ORM):
    id: int
    title: str
    description: str
    status: IncidentStatus
    severity: Severity
    assignee: str | None
    zone_id: int | None
    zone_name: str | None
    event_id: int | None
    created_at: datetime
    updated_at: datetime


# --- stats ---
class StatsOut(BaseModel):
    rovers_total: int
    rovers_online: int
    incidents_open: int
    events_last_hour: int
    events_by_type: dict[str, int]
