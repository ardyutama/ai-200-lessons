# Mini-mock 01 — AI-200 (20 questions, 30 minutes)

The Oct 9 confidence check. Bar: **≥ 17/20**. Closed book.

**1.** Cosmos DB change feed processor tracks progress using: A) a lease container B) Event Grid C) a stored procedure D) Redis

**2.** pgvector: which index gives better recall/latency at the cost of slower builds and more memory? A) IVFFlat B) B-tree C) HNSW D) GIN

**3.** Redis `SET k v EX 60 NX` means: A) set always, expire 60s B) set only if absent, expire 60s C) set only if present D) expire 60ms

**4.** Container Apps environment is best described as: A) a VNet B) a secure boundary of apps sharing networking and logging C) a registry D) a revision

**5.** `kubectl describe pod` is the right first step for: A) app exceptions B) ImagePullBackOff C) slow queries D) RBAC errors

**6.** AKS: selector mismatch between Service and Pod labels shows up as: A) CrashLoopBackOff B) empty `kubectl get endpoints` C) ImagePullBackOff D) OOMKilled

**7.** Service Bus sessions guarantee: A) encryption B) FIFO per session by one consumer at a time C) push delivery D) dedup across topics

**8.** Event Grid advanced filters operate on: A) only the subject B) fields in the event data payload C) headers D) the topic name

**9.** EventGridEvent vs CloudEvents — pick CloudEvents when: A) you need Azure-only features B) portability/standardization matters C) you need sessions D) never

**10.** Functions: output bindings exist to: A) trigger functions B) write to other services declaratively, without SDK code C) store secrets D) scale the app

**11.** host.json controls: A) local secrets B) runtime behavior (logging, retries, concurrency) C) plan pricing D) DNS

**12.** Key Vault URI for latest secret version: A) requires the version segment B) omit the version segment C) use HTTP D) use the resource id

**13.** App Configuration labels are used for: A) billing B) environment/variant separation of the same key C) encryption D) RBAC

**14.** OTel: a messaging send should use span kind: A) server B) client C) producer D) internal

**15.** OTel ratio sampler that keeps ~10% of traces: A) always_on B) parentbased_always_off C) traceidratio 0.1 D) jaeger_remote

**16.** KQL: `requests | summarize count() by resultCode | render piechart` — the pipe order matters because: A) render must come first B) summarize reshapes rows before render C) it doesn't D) render filters

**17.** KQL: filter to the last day and compute p50/p95 durations: write it below (free form).
`dependencies | where timestamp > ____ | summarize ____, ____ by name`

**18.** Managed Identity's role in real-Azure Key Vault access (conceptual): A) apps authenticate without stored credentials, authorized via RBAC B) it stores secrets C) it replaces Key Vault D) it rotates keys

**19.** On floci-az, why can't you practice Managed Identity? A) no network B) emulator uses fixed Azurite-style dev credentials; no Entra ID C) licensing D) ARM only

**20.** Exam logistics: after the final Yes/No section starts you can: A) review everything B) review only case studies C) not return to previous questions D) pause the timer

## Key

1-A · 2-C · 3-B · 4-B · 5-B · 6-B · 7-B · 8-B · 9-B · 10-B · 11-B · 12-B · 13-B · 14-C · 15-C · 16-B · 17: `ago(1d)`, `percentile(duration, 50)`, `percentile(duration, 95)` · 18-A · 19-B · 20-C

Score: __ / 20. Below 17 → cram the lapsed Domain tomorrow morning before your final card pass.
