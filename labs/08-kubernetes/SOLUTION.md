# Solution 08 — Kubernetes manifests on kind (answer key)

> **Attempt-first rule.** First pass: you may consult this key. The two runs that count toward *Solid Practice* must be done with this file **closed** — and the README says to *type* `deployment.yaml` by hand, not paste it. When you're ready for a counted run, close this and work from [README.md](README.md) alone.

**The Case Thread.** SupportBrain (from [Lab 02](../02-postgres-pgvector/SOLUTION.md)) is going to production. The managed platform wraps its container in an AKS Deployment — but AKS doesn't invent new primitives, it *runs plain Kubernetes manifests* and adds cloud integration on top. The container below stays `nginx:1.27` (per the README): the exam is probing *probes, selectors, rollouts, and resources* — mechanics that are identical whether the image is nginx or SupportBrain's API. Anything AKS adds beyond stock Kubernetes is marked **Azure-side** and is say-it-out-loud knowledge.

**Setup (do once):**

```powershell
kind create cluster --name ai200        # see ../../SETUP.md
kubectl cluster-info                    # context should be kind-ai200
```

**Verified live** against kind **v1.37.0** (control-plane `ai200-control-plane`, containerd 2.3.4) on 2026-10-08. All manifests and commands below ran as written.

> **Note on the runtime split.** Per [ADR 0001](../../docs/adr/0001-local-only-prep-with-floci-az.md) there is no Azure subscription: kind is the "real engine in Docker" stand-in, and the things only AKS can do (cloud load balancers, managed identity, Azure Monitor) are **Azure-side** theory lines, same convention as Solution 01.

---

## Step 1 — Deploy

**Q.** Write `deployment.yaml` cold: Deployment `web`, image `nginx:1.27`, 3 replicas, `containerPort: 80`, resource requests *and* limits, liveness + readiness probes on `/`.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.27
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 64Mi
          limits:
            cpu: 250m
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
        readinessProbe:
          httpGet:
            path: /
            port: 80
```

```powershell
kubectl apply -f deployment.yaml
kubectl rollout status deployment web     # waits for 3/3 available
```

**Why / trap.** The label wiring is the whole game and it must match in **two** places: `spec.selector.matchLabels.app: web` must equal `spec.template.metadata.labels.app: web` — mismatch it and the API server *rejects the Deployment at apply time* ("selector does not match template labels"). `containerPort` is **documentation, not enforcement** — it does not open or restrict anything; the exam loves implying otherwise.

Requests vs limits, one sentence each: **requests** = what the scheduler reserves when placing the pod (placement decision); **limits** = the hard ceiling the kubelet enforces at runtime (cgroup). Verified live: if you later patch `limits.memory` *below* `requests.memory`, the API server refuses — `requests: Invalid value: "64Mi": must be less than or equal to memory limit of 32Mi`. Requests ≤ limits, always.

The two probes answer different questions (see Step 5 for the kill/restart consequences):
- **Liveness** on `/` — *"is the process healthy?"* Fail ⇒ kubelet **restarts the container**.
- **Readiness** on `/` — *"should this pod receive Service traffic?"* Fail ⇒ pod is **pulled from Service endpoints**, but never restarted.

---

## Step 2 — Expose

**Q.** Service `web` type `ClusterIP`, then change to `LoadBalancer`. Explain the difference, and why AKS hands it a real IP while kind doesn't.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

```powershell
kubectl apply -f service.yaml
kubectl get svc web
kubectl patch svc web -p '{\"spec\":{\"type\":\"LoadBalancer\"}}'
kubectl get svc web
```

Verified output after the patch:

```text
NAME   TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
web    LoadBalancer   10.96.131.39   <pending>     80:31881/TCP   ...
```

**Why / trap.** **ClusterIP** = a stable virtual IP reachable *only inside the cluster*. Verified from a throwaway pod: `kubectl run curl-test --image=curlimages/curl --restart=Never -- curl http://web.default.svc.cluster.local` returns **200** — the DNS name is `<service>.<namespace>.svc.cluster.local`. **LoadBalancer** = ClusterIP + NodePort + a request to the *cloud provider* to build an external load balancer.

**Azure-side (the exam point):** on **AKS** the cloud controller manager sees type `LoadBalancer` and provisions a real **Azure Load Balancer** with a public IP — `EXTERNAL-IP` fills in. On **kind** there is no cloud provider, so `EXTERNAL-IP` stays **`<pending>` forever** and the port-forward is the workaround:

```powershell
kubectl port-forward svc/web 18080:80     # verified: http://localhost:18080 -> 200
```

Exam trap: a `<pending>` EXTERNAL-IP on AKS is a *problem*; the same `<pending>` on kind/minikube is *expected*. Don't "fix" the local one.

---

## Step 3 — ConfigMap + Secret

**Q.** Add a ConfigMap and a Secret, mount both as env vars on the Deployment. One sentence: why is a Secret *not* encryption?

```powershell
kubectl create configmap web-config --from-literal=WELCOME_MESSAGE=hello-from-configmap
kubectl create secret generic web-secret --from-literal=API_KEY=s3cr3t-value
kubectl get secret web-secret -o jsonpath='{.data.API_KEY}'     # -> czNjcjN0LXZhbHVl
```

Add to the container in `deployment.yaml` (then `kubectl apply -f deployment.yaml`):

```yaml
        env:
        - name: WELCOME_MESSAGE
          valueFrom:
            configMapKeyRef:
              name: web-config
              key: WELCOME_MESSAGE
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: web-secret
              key: API_KEY
```

Verified inside the pod:

```powershell
kubectl exec deploy/web -- printenv WELCOME_MESSAGE   # hello-from-configmap
kubectl exec deploy/web -- printenv API_KEY           # s3cr3t-value
```

**Why / trap.** **A Secret is base64-*encoded*, not encrypted** — `czNjcjN0LXZhbHVl` decodes straight back to `s3cr3t-value`, and anyone with RBAC read on the Secret (or who can `exec` into the pod, as just shown) gets the plaintext. A Secret is *access-controlled and kept out of casual view*, not encrypted at rest by default. **Azure-side:** real protection is etcd encryption-at-rest + tight RBAC, or better, keep secrets out of the cluster entirely via the **Key Vault CSI driver**.

Practical note: env vars are read **once at container start** — editing the ConfigMap/Secret later does *not* update running pods until they restart. (Volume mounts, not env vars, are the auto-refreshing form — but env is what the exam's manifests use.)

---

## Step 4 — Roll

**Q.** Change the image tag, watch the rollout, then undo it. Explain what ReplicaSets have to do with it.

```powershell
kubectl set image deployment/web nginx=nginx:1.29
kubectl rollout status deployment web
kubectl rollout history deployment web      # REVISION 1, 2, 3...
kubectl get rs -l app=web
```

Verified — before `undo`:

```text
NAME             DESIRED   CURRENT   READY   AGE
web-568bcd9bdd   0         0         0       3m34s
web-57f44b5795   3         3         3       61s    <- the 1.29 ReplicaSet
web-99c775df7    0         0         0       2m8s
```

```powershell
kubectl rollout undo deployment web
kubectl get rs -l app=web                    # old RS scaled back to 3
kubectl get deploy web -o jsonpath='{.spec.template.spec.containers[0].image}'   # nginx:1.27
```

**Why / trap.** A Deployment does **not** manage pods directly — it manages **ReplicaSets**. Each distinct pod-template (each image change) spawns a **new ReplicaSet**; a rollout is the Deployment *scaling the new RS up while scaling the old RS down* (default strategy `RollingUpdate`, max 25% surge / 25% unavailable). `rollout undo` doesn't re-run a build — it **scales the previous ReplicaSet back up**, which is why rollback is near-instant and safe. The old ReplicaSets stick around (revisions) purely so undo has something to point at.

Exam one-liner: *"Rollback works because the old ReplicaSet is never deleted — undo just rescales it."*

---

## Step 5 — Break it (the important part)

Diagnose with only `kubectl get`, `describe`, `logs`. Recite these trees cold.

### 5a — Wrong image tag → `ImagePullBackOff`

```powershell
kubectl set image deployment/web nginx=nginx:9.99-doesnotexist
kubectl get pods -l app=web        # ErrImagePull -> ImagePullBackOff
```

Verified event text (`kubectl describe pod`):

```text
Warning  Failed   ... Failed to pull image "nginx:9.99-doesnotexist": ... not found
Warning  Failed   ... Error: ErrImagePull
Normal   BackOff  ... Back-off pulling image "nginx:9.99-doesnotexist"
Warning  Failed   ... Error: ImagePullBackOff
```

**Diagnosis tree:** pod stuck not-Running → `get pods` shows `ImagePullBackOff`/`ErrImagePull` → `describe pod` and read the **Events** — the registry said `not found`. Causes: typo'd tag (here), image doesn't exist, or private registry without an `imagePullSecret` (message becomes `unauthorized`/`authentication required`). **Fix:** correct the image — and notice the *old* ReplicaSet's pods stayed Running, so the bad rollout didn't take the service down. **Azure-side:** AKS pulling from ACR uses the node's managed identity / `acr-pull` role, not a username/password in the manifest.

### 5b — Bad liveness path → `CrashLoopBackOff`

```powershell
kubectl patch deployment web --type=json -p='[{\"op\":\"replace\",\"path\":\"/spec/template/spec/containers/0/livenessProbe/httpGet/path\",\"value\":\"/does-not-exist\"}]'
kubectl get pods -l app=web        # RESTARTS climbs 1,2,3,4 -> CrashLoopBackOff
```

Verified — `get pods` shows `CrashLoopBackOff` after ~4 restarts, and `describe pod` shows both probes failing *for different reasons*:

```text
Liveness:   http-get http://:80/does-not-exist delay=0s timeout=1s period=10s #success=1 #failure=3
Warning  Unhealthy  ... Liveness probe failed: HTTP probe failed with statuscode: 404
Normal   Killing    ... Container nginx failed liveness probe, will be restarted
Warning  Unhealthy  ... Readiness probe failed: ... connect: connection refused
```

**Diagnosis tree:** pod Running but `RESTARTS` keeps rising → `describe pod` → `Killing ... failed liveness probe` with `statuscode: 404` tells you the *container is fine, the probe is wrong* (nginx is up; `/does-not-exist` 404s). The readiness `connection refused` is the *consequence*, not the cause — the container is down mid-restart so it briefly can't accept connections. Contrast 5a: here the image pulled fine, the app runs, but the *probe config* kills it. **Fix:** correct the probe path (a 404 on the *app's* real route would instead point at the app). **Exam line:** CrashLoopBackOff = container starts then dies/restarts repeatedly; read `describe` events + `logs --previous` to find *why it exits*.

### 5c — Memory limit too low → `OOMKilled` (exit 137)

```powershell
kubectl patch deployment web --type=json -p='[{\"op\":\"replace\",\"path\":\".../resources/limits/memory\",\"value\":\"32Mi\"},{\"op\":\"replace\",\"path\":\".../resources/requests/memory\",\"value\":\"32Mi\"}]'
```

nginx idles under 32Mi, so it OOMs only under pressure. Verified by filling the container's memory (writes to `/dev/shm` are tmpfs and count against the container's cgroup):

```powershell
kubectl exec <pod> -- sh -c 'dd if=/dev/zero of=/dev/shm/fill bs=1M count=100'
# command terminated with exit code 137
kubectl get pod <pod> -o jsonpath='{.status.containerStatuses[0].lastState}'
# {"terminated":{...,"exitCode":137,"reason":"OOMKilled",...}}
```

Verified describe:

```text
Last State:     Terminated
  Reason:       OOMKilled
  Exit Code:    137
```

**Diagnosis tree:** pod restarts with no app error in `logs` → `describe pod` → `Last State: Terminated / Reason: OOMKilled / Exit Code: 137`. **137 = 128 + 9 (SIGKILL)** — the kernel OOM-killer shot the process for exceeding `limits.memory`. Unlike a liveness failure, OOM leaves *no* probe event and often no log line — the process is killed before it can complain. **Fix:** raise the memory limit (or fix the leak). **CPU is throttled, memory is killed** — exceeding a CPU limit never OOMs; exceeding a memory limit always can.

### The three probes, one sentence each (recite cold)

- **Liveness:** "Is the container alive? Fail ⇒ kubelet **restarts** it." (Fixes deadlocks.)
- **Readiness:** "Can it take traffic? Fail ⇒ removed from **Service endpoints**, no restart." (Used during startup and graceful shutdown.)
- **Startup:** "Give a slow-starting container time *before* liveness/readiness apply — while startup is unmet, the other probes are disabled." (Prevents liveness from killing a slow-booting app.)

---

## Step 6 — Events & nodes

**Q.** Read cluster events and node health. Name the pressure conditions.

```powershell
kubectl get events --sort-by=.lastTimestamp
kubectl describe node ai200-control-plane
```

Verified node conditions block:

```text
MemoryPressure   False   ... KubeletHasSufficientMemory   kubelet has sufficient memory available
DiskPressure     False   ... KubeletHasNoDiskPressure     kubelet has no disk pressure
PIDPressure      False   ... KubeletHasSufficientPID      kubelet has sufficient PID available
Ready            True    ... KubeletReady                  kubelet is posting ready status
```

**Why / trap.** The three node **pressure conditions** are **`MemoryPressure`, `DiskPressure`, `PIDPressure`** (plus the summary `Ready`). `True` on any pressure condition means the node is starving and the kubelet will start **evicting pods** (and stop accepting new ones) — `MemoryPressure=True` is the node-level cousin of a pod-level OOMKill. `kubectl get events` is your timeline: scheduling decisions, pulls, probe failures, kills, and scaling all land there, sorted oldest→newest with `--sort-by=.lastTimestamp`. When `describe pod` doesn't explain a *pending* pod, `get events` usually will (e.g. `Insufficient cpu` / `0/1 nodes are available`).

---

## Step 7 — Bridge to the exam: the broken-manifest question

**Q.** Deliberately misconfigure the Service `selector`, and explain why no endpoints appear. This is the exam's favorite AKS YAML pattern: *given a broken snippet, find the error.*

```powershell
kubectl patch svc web --type=merge -p='{\"spec\":{\"selector\":{\"app\":\"web-typo\"}}}'
kubectl get endpoints web
```

Verified:

```text
NAME   ENDPOINTS   AGE
web    <none>      10m      <- selector matches nothing, so no endpoints
```

Fix it and the endpoints return instantly:

```powershell
kubectl patch svc web --type=merge -p='{\"spec\":{\"selector\":{\"app\":\"web\"}}}'
kubectl get endpoints web    # 10.244.0.27:80,10.244.0.28:80,10.244.0.29:80
```

**Why / trap.** A Service has **no idea where pods are** — it continuously selects pods whose **labels match its `selector`**, and the set of matches is published as the Service's **endpoints**. `selector: app: web-typo` matches zero pods ⇒ `ENDPOINTS <none>` ⇒ the Service IP blackholes traffic even though every pod is healthy. The pods' *readiness* gates inclusion too: a matching-but-not-ready pod is withheld from endpoints (that's Step 1's readiness probe doing its job).

Version note (verified on v1.37): `kubectl get endpoints` prints *"v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice"* — the modern view is `kubectl get endpointslice -l kubernetes.io/service-name=web`. On a current exam, expect **EndpointSlice** wording.

**The three errors to spot on sight in an exam manifest** (the README's list, now with the mechanism):
1. **Probe port/path wrong** → liveness kills a healthy app (5b) → `CrashLoopBackOff`.
2. **Service `selector` ≠ pod `labels`** → no endpoints (this step) → connection refused/timeout to the Service IP.
3. **Missing `resources.requests`** → scheduler can't guarantee placement / BestEffort QoS, and on a busy node the pod is first to be evicted.

---

## Step 8 — Done-when recap (whiteboard, no notes)

**Q.** Cold, from memory: the deploy, the expose, and the three diagnosis trees.

```text
deploy     kubectl apply -f deployment.yaml; kubectl rollout status deployment web
expose     Service type ClusterIP (internal) | LoadBalancer (Azure LB on AKS / <pending> on kind)
config     configMapKeyRef / secretKeyRef env;  Secret = base64, NOT encryption
roll       new ReplicaSet scales up, old scales down;  undo = rescale previous RS

ImagePullBackOff   image tag/name wrong or no pull secret -> describe events: "not found"
CrashLoopBackOff   starts then dies -> describe: liveness 404/connection refused; logs --previous
OOMKilled (137)    memory limit exceeded -> describe Last State: Reason OOMKilled, Exit 137
selector mismatch  Service selector != pod labels -> get endpoints = <none>
```

Probe one-liners: **liveness** restarts, **readiness** controls traffic, **startup** delays the other two for slow booters.
Node pressures: **Memory, Disk, PID** (+Ready); `True` ⇒ pod eviction.

**Why / trap.** If you can reproduce this block and recite the three trees with the key closed, the lab is done — everything else is commentary.

---

## Self-check (map to "Done when")

- Steps 1–5 twice, unaided → your two **key-closed Solid Practice** runs (type the YAML, don't paste).
- Recite the CrashLoopBackOff / ImagePullBackOff / OOMKilled trees cold → Step 5.
- Liveness vs readiness vs startup, one sentence each → Step 5 list.
- "Why `<pending>` on kind but a real IP on AKS?" → **no cloud provider locally; AKS wires up an Azure Load Balancer**.
- "A Secret is encryption, true or false?" → **false — base64 only**.
- "Service has no endpoints, pods are Running?" → **selector ≠ pod labels**.

**Cleanup:** `kind delete cluster --name ai200` (the whole cluster is disposable).
