#!/usr/bin/env bash
# Installs the cluster-level components the chart relies on:
# ingress-nginx (Ingress controller), metrics-server (needed by the HPA)
# and kube-prometheus-stack (Prometheus, Grafana, Operator CRDs).
set -euo pipefail

cd "$(dirname "$0")/.."

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

helm upgrade --install metrics-server metrics-server/metrics-server \
  --namespace kube-system

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f monitoring/prometheus-values.yaml

echo
echo "Load balancer hostname (may take a minute to appear):"
echo "  kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'"
