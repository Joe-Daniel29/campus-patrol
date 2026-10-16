"""Demo data so the dashboard is populated before any rover connects.

Everything here is simulated; there is no real hardware behind these records.
Run directly with `python -m app.seed`, or set SEED_DEMO_DATA=true.
"""
import random
from datetime import timedelta

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Event, Incident, Rover, Zone, utcnow

ZONES = [
    ("Main Gate", "Vehicle and pedestrian entrance", 20, 250, 60, 80),
    ("Library", "Central library and reading rooms", 200, 60, 140, 100),
    ("Hostel Block", "Student residences", 520, 70, 180, 120),
    ("Canteen", "Dining hall and food court", 380, 260, 110, 90),
    ("Parking", "Staff and visitor parking", 120, 400, 200, 100),
    ("Sports Ground", "Playing fields and track", 560, 380, 200, 160),
]

EVENT_TYPES = [
    ("person_after_hours", "WARNING", "Unrecognised person detected after hours"),
    ("door_left_open", "WARNING", "Building door open outside access hours"),
    ("vehicle_restricted", "WARNING", "Vehicle in restricted area"),
    ("crowd_gathering", "INFO", "Group gathering above usual size"),
    ("sos_button", "CRITICAL", "SOS button pressed"),
    ("obstacle_blocked", "INFO", "Patrol path blocked, rerouting"),
]


def seed_demo_data(db: Session, seed: int = 42) -> None:
    if db.get_bind().dialect.name == "postgresql":
        # Serialise concurrent replicas; the lock is released when this transaction ends.
        db.execute(text("SELECT pg_advisory_xact_lock(727275)"))
    if db.scalar(select(func.count(Zone.id))):
        return  # already seeded

    rng = random.Random(seed)
    zones = [Zone(name=n, description=d, x=x, y=y, width=w, height=h) for n, d, x, y, w, h in ZONES]
    db.add_all(zones)
    db.flush()

    now = utcnow()
    rovers = []
    for i in range(1, 9):
        zone = zones[(i - 1) % len(zones)]
        rovers.append(
            Rover(
                name=f"rover-{i:02d}",
                status=rng.choice(["PATROLLING", "PATROLLING", "IDLE", "CHARGING"]),
                battery=round(rng.uniform(35, 98), 1),
                x=round(zone.x + rng.uniform(5, zone.width - 5), 1),
                y=round(zone.y + rng.uniform(5, zone.height - 5), 1),
                heading=round(rng.uniform(0, 359), 1),
                last_seen=now - timedelta(seconds=rng.randint(1, 20)),
            )
        )
    db.add_all(rovers)
    db.flush()

    events = []
    for _ in range(40):
        kind, severity, message = rng.choice(EVENT_TYPES)
        events.append(
            Event(
                rover_id=rng.choice(rovers).id,
                zone_id=rng.choice(zones).id,
                type=kind,
                severity=severity,
                confidence=round(rng.uniform(0.6, 0.99), 2),
                message=message,
                created_at=now - timedelta(minutes=rng.randint(1, 48 * 60)),
            )
        )
    db.add_all(events)
    db.flush()

    notable = [e for e in events if e.severity != "INFO"][:10]
    statuses = ["OPEN", "OPEN", "ACKNOWLEDGED", "RESOLVED"]
    for i, event in enumerate(notable):
        db.add(
            Incident(
                title=event.message,
                description=f"Raised from event {event.id} by {event.type}",
                status=statuses[i % len(statuses)],
                severity=event.severity,
                zone_id=event.zone_id,
                event_id=event.id,
                assignee="security-desk" if i % len(statuses) else None,
                created_at=event.created_at,
                updated_at=event.created_at,
            )
        )
    db.commit()


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_demo_data(session)
    print("Seed complete")
