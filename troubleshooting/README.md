# Troubleshooting lab

Each manifest breaks something on purpose. Apply it, diagnose it with `kubectl`, fix it, and note the root cause.

```bash
kubectl apply -f k8s/namespace.yaml   # if the namespace does not exist yet
```

| # | Apply | Symptom | Diagnose with | Root cause | Fix |
|---|---|---|---|---|---|
| 1 | `broken-image.yaml` | `ImagePullBackOff` | `kubectl get pods -n campus-patrol`, `kubectl describe pod <pod>`, `kubectl get events --sort-by=.lastTimestamp` | The image tag does not exist in the registry | Correct the image reference and re-apply |
| 2 | `broken-service.yaml` | Pods `Running`, but the Service routes nowhere | `kubectl get endpoints patrol-broken-service`, `kubectl get pods --show-labels`, `kubectl describe svc patrol-broken-service` | Service selector `patrol-website` does not match pod label `patrol-web` | Fix the selector; endpoints appear |
| 3 | `broken-probe.yaml` | Pod `Running` but `0/1` Ready | `kubectl describe pod <pod>` (look for `Readiness probe failed: HTTP probe failed with statuscode: 404`) | The readiness probe path does not exist | Point the probe at `/` |

Clean up: `kubectl delete -f troubleshooting/ -n campus-patrol`.

## Applying this to the real app

The same three failures apply to the Campus Patrol chart. For example, the backend's `/ready` probe checks the database, so if PostgreSQL is down the backend pods stay `0/1` and the Service has no ready endpoints. The Ingress then returns 503 for `/api`, and the dashboard shows "Cannot reach the API". Trace it with `kubectl get pods`, `kubectl describe pod`, and `kubectl logs`.
