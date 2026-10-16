"""Virtual patrol rovers that talk to the API exactly as real hardware would.

Configuration (environment variables):
  API_URL        base URL of the backend              (default http://localhost:8000)
  ROVERS         number of virtual rovers             (default 8)
  INTERVAL       seconds between telemetry per rover  (default 2.0)
  EVENT_RATE     chance of an event per tick, 0..1    (default 0.02)
  SIM_SEED       RNG seed for reproducible runs       (default 42)
  INGEST_TOKEN   value for the X-Rover-Token header   (default empty)

Raise ROVERS and lower INTERVAL to use it as a load generator for autoscaling tests.
"""
import asyncio
import math
import os
import random

import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
ROVERS = int(os.getenv("ROVERS", "8"))
INTERVAL = float(os.getenv("INTERVAL", "2.0"))
EVENT_RATE = float(os.getenv("EVENT_RATE", "0.02"))
SEED = int(os.getenv("SIM_SEED", "42"))
TOKEN = os.getenv("INGEST_TOKEN", "")

SPEED = 4.0  # metres per tick
DOCK = (40.0, 290.0)  # charging dock, inside the Main Gate zone

EVENTS = [
    ("person_after_hours", "WARNING", "Unrecognised person detected after hours"),
    ("door_left_open", "WARNING", "Building door open outside access hours"),
    ("vehicle_restricted", "WARNING", "Vehicle in restricted area"),
    ("crowd_gathering", "INFO", "Group gathering above usual size"),
    ("obstacle_blocked", "INFO", "Patrol path blocked, rerouting"),
    ("sos_button", "CRITICAL", "SOS button pressed"),
]
EVENT_WEIGHTS = [3, 3, 2, 3, 3, 1]


class Rover:
    def __init__(self, index: int, zones: list[dict], rng: random.Random):
        self.name = f"rover-{index:02d}"
        self.rng = rng
        self.zones = zones
        self.battery = rng.uniform(50, 100)
        self.status = "PATROLLING"
        self.x, self.y = self._centre(zones[(index - 1) % len(zones)])
        self.heading = 0.0
        self.target = self._pick_target()

    @staticmethod
    def _centre(zone: dict) -> tuple[float, float]:
        return zone["x"] + zone["width"] / 2, zone["y"] + zone["height"] / 2

    def _pick_target(self) -> tuple[float, float]:
        return self._centre(self.rng.choice(self.zones))

    def zone_at(self) -> str | None:
        for z in self.zones:
            if z["x"] <= self.x <= z["x"] + z["width"] and z["y"] <= self.y <= z["y"] + z["height"]:
                return z["name"]
        return None

    def step(self) -> None:
        if self.status == "CHARGING":
            self.battery = min(100.0, self.battery + 3.0)
            if self.battery >= 95:
                self.status = "PATROLLING"
                self.target = self._pick_target()
            return
        if self.battery < 15 and self.status != "RESPONDING":
            self.target = DOCK
        dx, dy = self.target[0] - self.x, self.target[1] - self.y
        dist = math.hypot(dx, dy)
        if dist <= SPEED:
            self.x, self.y = self.target
            if self.target == DOCK:
                self.status = "CHARGING"
            else:
                self.target = self._pick_target()
        else:
            self.x += SPEED * dx / dist
            self.y += SPEED * dy / dist
            self.heading = (math.degrees(math.atan2(dy, dx)) + 360) % 360
        self.battery = max(0.0, self.battery - 0.15)

    def telemetry(self) -> dict:
        return {
            "rover": self.name,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "heading": round(self.heading, 1),
            "battery": round(self.battery, 1),
            "status": self.status,
        }

    def maybe_event(self) -> dict | None:
        if self.status == "CHARGING" or self.rng.random() > EVENT_RATE:
            return None
        kind, severity, message = self.rng.choices(EVENTS, weights=EVENT_WEIGHTS)[0]
        return {
            "rover": self.name,
            "zone": self.zone_at(),
            "type": kind,
            "severity": severity,
            "confidence": round(self.rng.uniform(0.6, 0.99), 2),
            "message": message,
        }


async def fetch_zones(client: httpx.AsyncClient) -> list[dict]:
    while True:
        try:
            response = await client.get("/api/zones")
            response.raise_for_status()
            zones = response.json()
            if zones:
                return zones
            print("No zones yet, waiting for the backend to seed them...")
        except httpx.HTTPError as exc:
            print(f"Backend not ready ({exc.__class__.__name__}), retrying...")
        await asyncio.sleep(3)


async def run_rover(rover: Rover, client: httpx.AsyncClient) -> None:
    await asyncio.sleep(rover.rng.uniform(0, INTERVAL))  # stagger start-up
    while True:
        rover.step()
        try:
            await client.post("/api/telemetry", json=rover.telemetry())
            event = rover.maybe_event()
            if event:
                await client.post("/api/events", json=event)
        except httpx.HTTPError as exc:
            print(f"{rover.name}: send failed ({exc.__class__.__name__})")
        await asyncio.sleep(INTERVAL)


async def main() -> None:
    headers = {"X-Rover-Token": TOKEN} if TOKEN else {}
    limits = httpx.Limits(max_connections=max(20, ROVERS))
    async with httpx.AsyncClient(base_url=API_URL, headers=headers, timeout=10, limits=limits) as client:
        zones = await fetch_zones(client)
        rng = random.Random(SEED)
        rovers = [Rover(i, zones, random.Random(rng.random())) for i in range(1, ROVERS + 1)]
        print(f"Simulating {len(rovers)} rovers against {API_URL} every {INTERVAL}s")
        await asyncio.gather(*(run_rover(r, client) for r in rovers))


if __name__ == "__main__":
    asyncio.run(main())
