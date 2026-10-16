#!/usr/bin/env bash
# Drives CPU on the backend by scaling up the in-cluster rover simulator, so the
# HPA has something to react to. Watch it with: kubectl get hpa -n campus-patrol -w
#
#   scripts/load-test.sh start     # 200 rovers reporting every 0.2s
#   scripts/load-test.sh stop      # back to normal
set -euo pipefail

RELEASE="${RELEASE:-campus-patrol}"
NAMESPACE="${NAMESPACE:-campus-patrol}"
CHART="$(dirname "$0")/../helm/campus-patrol"
ROVERS="${ROVERS:-200}"
INTERVAL="${INTERVAL:-0.2}"

case "${1:-}" in
  start)
    helm upgrade "$RELEASE" "$CHART" -n "$NAMESPACE" --reuse-values \
      --set simulator.enabled=true \
      --set simulator.rovers="$ROVERS" \
      --set simulator.interval="$INTERVAL"
    ;;
  stop)
    helm upgrade "$RELEASE" "$CHART" -n "$NAMESPACE" --reuse-values \
      --set simulator.rovers=8 \
      --set simulator.interval=2
    ;;
  *)
    echo "usage: $0 start|stop" >&2
    exit 1
    ;;
esac
