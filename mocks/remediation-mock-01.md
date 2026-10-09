# Remediation Mock 01 — AI-200 (targeted, 45 minutes)

Built from the 10 mock-01 misses (Q7, Q17, Q22, Q24, Q25, Q30, Q31, Q34, Q35, Q41) plus the Reddit signal: **Kubernetes appears more than expected** — so containers are over-weighted with scenarios mock-01 never touched. Every missed concept is re-probed at least twice from fresh angles.

Rules: closed book. 30 questions. Bar: **≥85% (26/30)**. Dropdown-style items mirror the real exam's "select the correct value" format. The Yes/No section (Q27–30) is **no-return**: write your answer and don't change it.

---

## Case Study (Q1–Q5) — SupportBrain

SupportBrain's ingestion pipeline: product docs live in **Cosmos DB for NoSQL**; a Function reacts to the **change feed** and pushes chunk jobs onto a **Service Bus queue**; a **Container Apps** worker (Python) receives jobs, embeds chunks, and upserts into **Azure Postgres + pgvector** (IVFFlat today); **Redis** caches retrieval results. Nightly backfills bulk-load ~2M embeddings into a staging table that then swaps in.

**Q1.** A tenant deletes a document in Cosmos DB. The change-feed Function never fires, and the stale embedding stays searchable. Why?
A) The lease container lost its checkpoint
B) By design: the change feed captures inserts/updates only — model deletion as an update (soft-delete flag) so the reaction fires
C) The Function's `maxRetryCount` was exhausted
D) The feed must be switched from latest-version mode

**Q2.** For the nightly 2M-row bulk load into an empty staging table, which index strategy is correct?
A) Build the IVFFlat index before the COPY so rows index as they arrive
B) Build HNSW before the COPY, because it clusters existing rows
C) COPY first, then build IVFFlat — it clusters rows present at build time; HNSW is the one that tolerates incremental inserts on an empty table
D) Skip the index; a sequential `<=>` scan is fine at 2M rows

**Q3.** The worker must never lose a chunk job even if it crashes mid-processing; duplicate delivery is tolerable (upserts are idempotent). Which receive mode?
A) ReceiveAndDelete — fastest, deleted on read
B) PeekLock — complete on success; abandon or lock expiry redelivers (at-least-once)
C) ReceiveAndDelete with prefetch
D) Deferral, retrieved by sequence number

**Q4.** A new requirement adds a nightly re-embed sweep on a schedule. The team proposes adding a `timerTrigger` to the existing queue-triggered function. Verdict?
A) Fine — a function accepts many triggers
B) Not allowed — exactly one trigger per function (bindings can be many); create a second function in the same Function App
C) Fine, but only in function.json, not the v2 decorator model
D) Replace the queue trigger with a timer that polls the queue

**Q5.** The worker Container App must scale with queue backlog and cost nothing when idle. Select the correct values for the scaler: `type: ____`, `minReplicas: ____`
A) `http`, `0`
B) `azure-servicebus`, `1`
C) `azure-servicebus`, `0`
D) `cpu`, `0`

---

## Section 2 — Regular questions (Q6–Q26)

**Q6.** Select the minimum ACR tier that supports geo-replication:
A) Basic  B) Standard  C) Premium  D) Any tier with a premium storage account

**Q7.** A Container App has only an HTTP scaling rule. Service Bus backlog grows to thousands, but replicas stay at 1. Why?
A) KEDA is not installed in the environment
B) The HTTP scaler counts concurrent HTTP requests — it cannot see Service Bus depth; add a KEDA `azure-servicebus` scaler
C) `minReplicas` is set too low
D) The app is in single revision mode

**Q8.** An AKS pod's app container must not start until Postgres accepts connections. Use:
A) A sidecar container running `pg_isready`
B) An initContainer that runs the check to completion before app containers start
C) A livenessProbe with a long period
D) `restartPolicy: OnFailure`

**Q9.** A pod needs the embeddings model name (non-secret) and the Postgres password. Correct wiring:
A) Both in a ConfigMap
B) Both in a Secret
C) Model name via ConfigMap env; password via Secret env (or Key Vault CSI)
D) Bake both into the image

**Q10.** HPA vs KEDA:
A) HPA scales on queue depth; KEDA scales on CPU
B) HPA scales on resource metrics (CPU/memory); KEDA scales on external event sources such as Service Bus depth
C) They are interchangeable
D) VPA replaces both

**Q11.** Postgres on AKS/kind must keep data across pod restarts. The manifest needs:
A) `emptyDir`
B) `hostPath` (production-grade)
C) A PersistentVolumeClaim bound to a PersistentVolume
D) A ConfigMap

**Q12.** `supportbrain-api` resolves in cluster DNS but `kubectl get endpoints supportbrain-api` is empty. Most likely cause:
A) CoreDNS is down
B) The Service selector matches no Pod labels
C) ImagePullBackOff
D) Node memory pressure

**Q13.** A legacy container takes ~90s to boot; the liveness probe kills it at 30s, looping forever. Correct fix:
A) Remove all probes
B) Add a startupProbe with failureThreshold × period covering worst-case boot — it suspends liveness/readiness until startup succeeds
C) Increase replicas
D) Switch to a readinessProbe only

**Q14.** After switching a Deployment to a private ACR tag, new pods are stuck `ImagePullBackOff`. First move:
A) `kubectl logs` for the app crash
B) `kubectl describe pod` — the events show the exact pull error (bad tag vs missing imagePullSecret/ACR auth)
C) `kubectl delete node`
D) Restart the kubelet

**Q15.** A document's partition key is changed (delete + re-insert under the new PK). What appears in the Cosmos DB change feed?
A) One update entry
B) Nothing
C) An insert of the new item only — the delete is never captured
D) A delete entry and an insert entry

**Q16.** IVFFlat recall is too low and the load window is closed — no rebuild allowed. Select the correct knob:
A) `lists` — raise it and rebuild
B) `probes` — raise it at query time (`SET ivfflat.probes = n`)
C) `m`
D) `ef_construction`

**Q17.** The team created an IVFFlat index on an empty table, then bulk-loaded 5M rows. Recall is poor and drifts as data grows. Root cause and fix:
A) pgvector bug — patch the extension
B) IVFFlat clusters the rows present at build time; built on an empty table its centroids are meaningless — REINDEX after the load
C) Too few connections in the pool
D) Wrong distance operator

**Q18.** Redis runs `volatile-ttl`; 90% of keys were SET without a TTL. Under memory pressure `evicted_keys` stays at 0 and writes start failing with OOM errors. Why, and the fix:
A) Redis bug — restart the cache
B) `volatile-ttl` only evicts keys that have a TTL — no-TTL keys are unevictable; a general cache should use `allkeys-lru`
C) TTLs are too long — shorten them
D) Switch to `noeviction`

**Q19.** A script treats `TTL sess:abc` returning -1 as "key missing" and re-SETs it on every request, hammering Postgres. What does -1 actually mean?
A) Key missing
B) Key exists with no expiry — the check should use `EXISTS`, not `TTL`
C) Key already expired
D) One second remaining

**Q20.** A cache holds a small set of permanently-hot keys plus a long tail of one-off reads. Best eviction policy:
A) `allkeys-lru`
B) `allkeys-lfu` — frequency-aware: one-off reads won't evict long-standing hot keys
C) `volatile-random`
D) `noeviction`

**Q21.** Which Redis output confirms evictions are actually happening?
A) `INFO stats` → `evicted_keys`
B) `DBSIZE`
C) `CONFIG GET maxmemory`
D) `SLOWLOG GET`

**Q22.** Which is NOT a Service Bus dead-letter trigger?
A) Message TTL expiry
B) MaxDeliveryCount exceeded
C) Filter evaluation exception on a subscription
D) Message larger than 256 KB at send time

**Q23.** A worker uses ReceiveAndDelete and crashes right after reading a message, before processing it. Result:
A) The message is redelivered
B) The message is gone — deleted before processing; ReceiveAndDelete is at-most-once
C) The message moves to the DLQ
D) The lock expires and another worker receives it

**Q24.** A PeekLock worker exceeds its 5-minute lock without completing or abandoning. What happens?
A) The message is deleted
B) The lock expires, DeliveryCount has incremented, and the message becomes available to other receivers; after MaxDeliveryCount it dead-letters
C) The message is duplicated into the topic
D) Nothing — the lock renews forever

**Q25.** PeekLock delivers at-least-once, so duplicates happen. The correct handler design:
A) Enable the exactly-once flag
B) Make processing idempotent (upsert by document id / dedupe key)
C) Switch to ReceiveAndDelete
D) Require sessions on every queue

**Q26.** A legacy v1 function.json lists two trigger entries (queue + timer). At startup the Functions host:
A) Runs both triggers
B) Fails to index the function — a function must have exactly one trigger
C) Honors the first trigger only
D) Merges them into one

---

## Section 3 — Yes/No (no return) (Q27–Q30)

**Q27.** HNSW can be built on an empty table and used immediately as rows are inserted incrementally. Yes / No
**Q28.** With `volatile-ttl`, keys that have no TTL will eventually be evicted once memory is full. Yes / No
**Q29.** The Cosmos DB change feed delivers hard deletes to the processor as delete entries. Yes / No
**Q30.** PeekLock provides at-least-once delivery, provided the receiver completes each message only after successful processing. Yes / No

---

## Answer key

| Q | Ans | Domain | Why |
|---|---|---|---|
| 1 | B | data | change feed = inserts/updates only; soft-delete surfaces removals |
| 2 | C | data | IVFFlat clusters rows at build time → build after bulk load; HNSW tolerates incremental |
| 3 | B | integration | PeekLock = at-least-once; ReceiveAndDelete loses messages on crash |
| 4 | B | integration | one trigger per function, always |
| 5 | C | containers | KEDA azure-servicebus scaler + minReplicas 0 = scale-to-zero on backlog |
| 6 | C | containers | geo-replication is Premium-gated |
| 7 | B | containers | HTTP scaler sees HTTP only; queue depth needs the KEDA servicebus scaler |
| 8 | B | containers | initContainers run to completion before app containers |
| 9 | C | containers | ConfigMap for config, Secret/KV-CSI for secrets — never mix |
| 10 | B | containers | HPA = resource metrics; KEDA = external event sources |
| 11 | C | containers | PVC for durable pod storage |
| 12 | B | containers | selector↔label mismatch = empty endpoints |
| 13 | B | containers | startupProbe protects slow-booting apps from liveness |
| 14 | B | containers | describe pod shows pull errors in events |
| 15 | C | data | PK change = delete+insert; deletes never appear |
| 16 | B | data | probes = query-time recall; lists is fixed at build |
| 17 | B | data | IVFFlat on empty table = meaningless centroids; rebuild after load |
| 18 | B | data | volatile-ttl leaves no-TTL keys unevictable → allkeys-lru |
| 19 | B | data | TTL: -1 = no expiry, -2 = gone |
| 20 | B | data | LFU protects long-lived hot keys from one-off churn |
| 21 | A | data | evicted_keys in INFO stats |
| 22 | D | integration | oversized messages are rejected at send — never enqueued, never dead-lettered |
| 23 | B | integration | deleted-on-read = at-most-once data loss on crash |
| 24 | B | integration | lock expiry → redelivery with DeliveryCount++ → DLQ at max |
| 25 | B | integration | at-least-once ⇒ idempotent handlers |
| 26 | B | integration | host indexing fails with two triggers |
| 27 | Yes | data | HNSW is incremental; IVFFlat is not |
| 28 | No | data | no-TTL keys are unevictable under volatile-* policies |
| 29 | No | data | change feed never captures deletes |
| 30 | Yes | integration | complete-after-success = at-least-once |

## Scorecard

| Domain | Questions | Your score | Target |
|---|---|---|---|
| containers | Q5–14 | __ / 10 | ≥ 9 |
| data | Q1–2, 15–21, 27–29 | __ / 12 | ≥ 10 |
| integration | Q3–4, 22–26, 30 | __ / 8 | ≥ 7 |
| **Total** | | __ / 30 | **≥ 26 (85%)** |

## Miss map (mock-01 → this mock)

| Mock-01 miss | Re-probed by |
|---|---|
| Q7 KEDA scale-to-zero | Q5, Q7 |
| Q17 ACR Premium geo-replication | Q6 |
| Q22 change feed / deletes | Q1, Q15, Q29 |
| Q24 IVFFlat build order | Q2, Q17, Q27 |
| Q25 probes vs lists | Q16 |
| Q30 allkeys-lru vs volatile-ttl | Q18, Q20, Q28 |
| Q31 TTL -1/-2 | Q19 |
| Q34 ReceiveAndDelete vs PeekLock | Q3, Q23, Q24, Q30 |
| Q35 DLQ trigger set | Q22, Q24 |
| Q41 one trigger per function | Q4, Q26 |

For every miss here: re-read the matching study-guide bullet, redo the matching lab step, and flag the `mock01` tag in Anki. Pass this (≥26) before sitting full mock-02.
