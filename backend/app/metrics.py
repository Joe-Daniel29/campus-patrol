from prometheus_client import REGISTRY, Counter
from prometheus_client.core import GaugeMetricFamily
from sqlalchemy import func, select

from .db import SessionLocal
from .models import Incident, Rover

EVENTS_TOTAL = Counter(
    "patrol_events_total", "Detection events received from rovers", ["type", "severity"]
)
TELEMETRY_TOTAL = Counter("patrol_telemetry_total", "Telemetry messages received from rovers")


class FleetCollector:
    """Computes fleet gauges from the database at scrape time."""

    def collect(self):
        rovers_total = GaugeMetricFamily("patrol_rovers_total", "Registered rovers")
        rovers_online = GaugeMetricFamily("patrol_rovers_online", "Rovers that reported recently")
        incidents_open = GaugeMetricFamily("patrol_incidents_open", "Incidents not yet resolved")
        battery = GaugeMetricFamily("patrol_rover_battery_percent", "Rover battery level", labels=["rover"])
        try:
            with SessionLocal() as db:
                rovers = list(db.scalars(select(Rover)))
                open_count = db.scalar(
                    select(func.count(Incident.id)).where(Incident.status != "RESOLVED")
                )
        except Exception:
            return
        rovers_total.add_metric([], len(rovers))
        rovers_online.add_metric([], sum(1 for r in rovers if r.online))
        incidents_open.add_metric([], open_count or 0)
        for r in rovers:
            battery.add_metric([r.name], r.battery)
        yield from (rovers_total, rovers_online, incidents_open, battery)


def register_collectors() -> None:
    # Guard against double registration (e.g. under uvicorn --reload or tests).
    if not getattr(register_collectors, "done", False):
        REGISTRY.register(FleetCollector())
        register_collectors.done = True
