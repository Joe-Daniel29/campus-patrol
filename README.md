# Campus Patrol

A command-center dashboard for a fleet of campus patrol robots. Rovers report their pose and battery, raise detection events (unrecognised person after hours, door left open, SOS), and security staff triage those events as incidents.

> **Simulated data.** No physical robots are connected. A rover simulator posts telemetry and events to the same public API a real rover would use, and a seeder loads demo zones, rovers, events and incidents. Real hardware can be added later without backend changes.

## Architecture

```text
rover simulator ──HTTP──> FastAPI ──> PostgreSQL
                            │  └─ /metrics ──> Prometheus ──> Grafana
React dashboard ──/api──> nginx ──┘
```

| Part | Stack |
|---|---|
| `frontend/` | React + Vite, served by unprivileged nginx |
| `backend/` | FastAPI, SQLAlchemy, Alembic, pytest |
| `simulator/` | Python + httpx, one async task per virtual rover |
| database | PostgreSQL 16 |

## API

| Method | Path | Purpose |
|---|---|---|
| GET/POST | `/api/rovers` | List or register rovers |
| GET/PUT/DELETE | `/api/rovers/{id}` | Read, update or remove a rover |
| POST | `/api/telemetry` | Rover heartbeat (pose, battery); auto-registers new rovers |
| GET/POST | `/api/zones` | Campus zones in the map frame (metres) |
| GET/POST | `/api/events` | Detection events; filter by `severity`, `rover_id` |
| GET/POST | `/api/incidents` | List or open incidents; filter by `status` |
| GET/PUT/DELETE | `/api/incidents/{id}` | Acknowledge, resolve, edit or delete |
| GET | `/api/stats` | Fleet and incident summary |
| GET | `/health`, `/ready`, `/metrics` | Liveness, readiness (checks DB), Prometheus |

Swagger UI is at `/docs`. Set `INGEST_TOKEN` to require an `X-Rover-Token` header on telemetry and event ingestion.

## Run locally

```bash
docker compose up --build                    # app + database, seeded demo data
docker compose --profile sim up --build      # also start the rover simulator
```

- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

Tear down, including the database volume: `docker compose down -v`.

### Backend without Docker

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v                      # uses in-memory SQLite, no database needed
```

### Simulator as a load generator

```bash
ROVERS=200 INTERVAL=0.2 API_URL=http://localhost:8000 python simulator/simulator.py
```

`SIM_SEED` makes runs reproducible.

## Metrics

Beyond the default HTTP metrics: `patrol_rovers_total`, `patrol_rovers_online`, `patrol_incidents_open`, `patrol_rover_battery_percent{rover}`, `patrol_events_total{type,severity}`, `patrol_telemetry_total`.

## Privacy

The system stores event metadata only (type, zone, confidence, time), not images or video.

## Roadmap

- [x] Application, tests, Docker, Compose
- [ ] GitHub Actions: test, build, Trivy scan, push to GHCR
- [ ] Terraform: AWS VPC + EKS
- [ ] Helm chart, Ingress, HPA
- [ ] Prometheus + Grafana
- [ ] Troubleshooting exercises
