from sqlalchemy import func, select

from app.models import Incident, Rover, Zone
from app.seed import seed_demo_data


def test_seed_populates_and_is_idempotent(db):
    seed_demo_data(db)
    seed_demo_data(db)
    assert db.scalar(select(func.count(Zone.id))) == 6
    assert db.scalar(select(func.count(Rover.id))) == 8
    assert db.scalar(select(func.count(Incident.id))) > 0
