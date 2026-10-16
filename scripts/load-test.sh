#!/usr/bin/env bash
# Drives CPU on the backend by scaling up the in-cluster rover simulator, so the
# HPA has something to react to. Watch it with: kubectl get hpa -n campus-patrol -w
#
#   scripts/load-test.sh start     # 200 rovers reporting every 0.2s
#   scripts/load-test.sh stop      # back to normal, and remove the extra rovers
set -euo pipefail

RELEASE="${RELEASE:-campus-patrol}"
NAMESPACE="${NAMESPACE:-campus-patrol}"
CHART="$(dirname "$0")/../helm/campus-patrol"
ROVERS="${ROVERS:-200}"
INTERVAL="${INTERVAL:-0.2}"
NORMAL_ROVERS=8

# The load test auto-registers rover-01..rover-N. Once the simulator is back to
# NORMAL_ROVERS, delete the rest so the dashboard does not keep showing them offline.
remove_extra_rovers() {
  local selector="app.kubernetes.io/instance=$RELEASE,app.kubernetes.io/component"
  kubectl rollout status deployment -n "$NAMESPACE" -l "$selector=simulator" --timeout=120s
  # rollout status returns while the old simulator pod is still terminating (and
  # still sending telemetry), so wait until only the desired pods remain.
  local desired
  desired=$(kubectl get deployment -n "$NAMESPACE" -l "$selector=simulator" -o jsonpath='{.items[0].spec.replicas}')
  for _ in $(seq 1 60); do
    [ "$(kubectl get pods -n "$NAMESPACE" -l "$selector=simulator" --no-headers | wc -l)" -le "$desired" ] && break
    sleep 2
  done
  kubectl exec -i -n "$NAMESPACE" "$(kubectl get deployment -n "$NAMESPACE" -l "$selector=backend" -o name)" \
    -- python - "$NORMAL_ROVERS" <<'PY'
import re, sys
from app.db import SessionLocal
from app.models import Rover

keep = int(sys.argv[1])
with SessionLocal() as db:
    extra = [r for r in db.query(Rover) if (m := re.fullmatch(r"rover-(\d+)", r.name)) and int(m.group(1)) > keep]
    for rover in extra:
        db.delete(rover)
    db.commit()
print(f"removed {len(extra)} extra rovers")
PY
}

case "${1:-}" in
  start)
    helm upgrade "$RELEASE" "$CHART" -n "$NAMESPACE" --reuse-values \
      --set simulator.enabled=true \
      --set simulator.rovers="$ROVERS" \
      --set simulator.interval="$INTERVAL"
    ;;
  stop)
    helm upgrade "$RELEASE" "$CHART" -n "$NAMESPACE" --reuse-values \
      --set simulator.rovers="$NORMAL_ROVERS" \
      --set simulator.interval=2
    remove_extra_rovers
    ;;
  *)
    echo "usage: $0 start|stop" >&2
    exit 1
    ;;
esac
