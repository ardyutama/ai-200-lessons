# Lab 08 — Kubernetes manifests (kind) — the Reddit regret lab

**Study-guide bullets covered:** deploy/manage applications on AKS using manifest files · monitor and troubleshoot on AKS by inspecting logs, events, and connectivity. (KEDA on Container Apps stays theory — cram those cards instead.)

**Setup:** `kind create cluster --name ai200` (see [SETUP.md](../../SETUP.md)). This is the lab to run **twice** — Kubernetes was the most over-represented topic in pass reports.

## Steps

1. **Deploy.** Write `deployment.yaml` by hand (don't paste): Deployment `web` (image `nginx:1.27`, 3 replicas, containerPort 80, `resources.requests/limits`, liveness + readiness probes on `/`). `kubectl apply -f deployment.yaml`.
2. **Expose.** Service `web` type ClusterIP, then change to LoadBalancer — explain the difference and why AKS gives it a real IP (cloud LB integration) while kind doesn't (pending EXTERNAL-IP; use `kubectl port-forward` instead).
3. **Config.** Add a ConfigMap + a Secret, mount as env vars on the Deployment. One sentence: why a Secret is not encryption.
4. **Roll.** Change the image tag, `kubectl apply`, `kubectl rollout status`, then `kubectl rollout undo`. Explain ReplicaSets.
5. **Break it (the important part).** Sabotage, then diagnose with only `get`/`describe`/`logs`:
   - wrong image tag → `ImagePullBackOff`
   - bad liveness path → `CrashLoopBackOff` via probe restarts
   - memory limit 32Mi on nginx… observe and explain OOMKill (exit 137)
6. **Events & nodes.** `kubectl get events --sort-by=.lastTimestamp`, `kubectl describe node`. Name the pressure conditions.
7. **Bridge to the exam.** Read an AKS YAML question pattern: given a broken manifest snippet, find the error (probe port, selector mismatch with Service, missing requests). Practice by deliberately misconfiguring the Service `selector` and explaining why no endpoints appear (`kubectl get endpoints web`).

## Done when

- [ ] Steps 1–5 twice, unaided
- [ ] You can recite the CrashLoopBackOff / ImagePullBackOff diagnosis trees
- [ ] Liveness vs readiness vs startup — one sentence each, cold

## Cleanup

`kind delete cluster --name ai200`
