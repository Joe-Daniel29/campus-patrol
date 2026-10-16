# Campus Patrol

A command-center dashboard for a fleet of campus patrol robots. Rovers report their pose and battery, raise detection events (unrecognised person after hours, door left open, SOS), and security staff triage those events as incidents.

**Presentation:** [docs/Campus-Patrol-Capstone.pptx](docs/Campus-Patrol-Capstone.pptx)

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

## Deploy to Kubernetes

```bash
# 1. Infrastructure (see terraform/README.md; costs money while it exists)
cd terraform && terraform init && terraform apply
$(terraform output -raw configure_kubectl) && cd ..

# 2. Cluster add-ons: ingress-nginx, metrics-server, Prometheus + Grafana
scripts/install-cluster-addons.sh

# 3. The application. Images are tagged with the commit SHA by CI.
helm upgrade --install campus-patrol ./helm/campus-patrol \
  -n campus-patrol --create-namespace \
  -f helm/campus-patrol/values-eks.yaml \
  --set backend.image=ghcr.io/<owner>/campus-patrol-backend  --set backend.tag=<sha> \
  --set frontend.image=ghcr.io/<owner>/campus-patrol-frontend --set frontend.tag=<sha> \
  --set simulator.enabled=true --set simulator.image=ghcr.io/<owner>/campus-patrol-simulator --set simulator.tag=<sha>

kubectl get pods,svc,hpa,ingress -n campus-patrol
helm list -n campus-patrol
```

For a local cluster (kind, minikube) use `-f helm/campus-patrol/values-dev.yaml` and add `patrol.local` to `/etc/hosts`.

Set the repository variable `DEPLOY_ENABLED=true` (plus the AWS secrets) and CI deploys every push to `main`.

### Autoscaling demo

```bash
scripts/load-test.sh start     # 200 simulated rovers reporting every 0.2s
kubectl get hpa -n campus-patrol -w
scripts/load-test.sh stop
```

### Monitoring

Prometheus scrapes `/metrics` through a ServiceMonitor, and a Grafana dashboard ("Campus Patrol") loads automatically from a ConfigMap. Alert rules cover offline rovers, a high 5xx ratio and an incident backlog.

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090
```

## Metrics

Beyond the default HTTP metrics: `patrol_rovers_total`, `patrol_rovers_online`, `patrol_incidents_open`, `patrol_rover_battery_percent{rover}`, `patrol_events_total{type,severity}`, `patrol_telemetry_total`.

## Security scanning

Every image is scanned by Trivy in CI before it can be pushed. The scan covers OS packages and language libraries and fails the job on any HIGH or CRITICAL vulnerability that has a fix available (`ignore-unfixed: true`), so nothing is published that could have been patched.

The first scan of the frontend image found 41 such issues (39 HIGH, 2 CRITICAL), all in the Alpine packages of the old `nginx-unprivileged:1.27-alpine` base image. One example is CVE-2026-31789, a heap buffer overflow in OpenSSL's `libcrypto3` 3.3.3, fixed in 3.3.7. It is rated CRITICAL but only exploitable on 32-bit systems, so it would not have been reachable on these 64-bit nodes. The pipeline failed the build anyway, which is the intended behaviour. Moving the base image to `nginx-unprivileged:1.30-alpine` cleared all 41, and the backend and simulator images (`python:3.12-slim`) scanned clean.

## Troubleshooting lab

Three deliberately broken manifests (bad image, Service selector mismatch, failing readiness probe) are in [`troubleshooting/`](troubleshooting/README.md).

## Privacy

The system stores event metadata only (type, zone, confidence, time), not images or video.

## Roadmap

- [x] Application, tests, Docker, Compose
- [x] GitHub Actions: test, build, Trivy scan, push to GHCR, gated Helm deploy
- [x] Terraform: AWS VPC + EKS
- [x] Helm chart, Ingress, HPA
- [x] Prometheus + Grafana, alert rules, dashboard
- [x] Troubleshooting exercises
- [x] Run end to end on AWS (EKS 1.31, 3 nodes): CI-built images deployed with Helm, HPA scaled 2 to 6 under load, Prometheus and Grafana verified
