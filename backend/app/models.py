from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .config import settings
from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    # SQLite returns naive datetimes; treat them as UTC.
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


class Zone(Base):
    """A named rectangle in the campus map frame (metres)."""

    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    x: Mapped[float] = mapped_column(Float, default=0)
    y: Mapped[float] = mapped_column(Float, default=0)
    width: Mapped[float] = mapped_column(Float, default=50)
    height: Mapped[float] = mapped_column(Float, default=50)


class Rover(Base):
    __tablename__ = "rovers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="IDLE")
    battery: Mapped[float] = mapped_column(Float, default=100)
    x: Mapped[float] = mapped_column(Float, default=0)
    y: Mapped[float] = mapped_column(Float, default=0)
    heading: Mapped[float] = mapped_column(Float, default=0)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def online(self) -> bool:
        if self.last_seen is None:
            return False
        age = utcnow() - as_utc(self.last_seen)
        return age <= timedelta(seconds=settings.online_window_seconds)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    rover_id: Mapped[int] = mapped_column(ForeignKey("rovers.id", ondelete="CASCADE"), index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("zones.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[str] = mapped_column(String(40))
    severity: Mapped[str] = mapped_column(String(10), default="INFO")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    rover: Mapped[Rover] = relationship(lazy="joined")
    zone: Mapped[Zone | None] = relationship(lazy="joined")

    @property
    def rover_name(self) -> str:
        return self.rover.name

    @property
    def zone_name(self) -> str | None:
        return self.zone.name if self.zone else None


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="OPEN", index=True)
    severity: Mapped[str] = mapped_column(String(10), default="WARNING")
    assignee: Mapped[str | None] = mapped_column(String(80), nullable=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("zones.id", ondelete="SET NULL"), nullable=True)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    zone: Mapped[Zone | None] = relationship(lazy="joined")

    @property
    def zone_name(self) -> str | None:
        return self.zone.name if self.zone else None
