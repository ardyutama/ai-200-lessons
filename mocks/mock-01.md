# Mock 01 — AI-200 (timed, 100 minutes)

Rules: closed book first pass (on the real exam MS Learn *is* browsable — but grade yourself closed-book). 54 questions. Passing bar for this mock: **≥85% (46/54)**. The Yes/No section (Q51–54) is **no-return**: write your answer and don't change it.

---

## Case Study (Q1–Q5)

Contoso is building a support copilot on Azure. Architecture: product docs stored in **Cosmos DB for NoSQL** with 1,536-dim embeddings (5M items, growing); ingestion events flow through a **Service Bus topic** to **Azure Functions** that chunk and embed documents; app settings live in **App Configuration**; secrets in **Key Vault**; all components emit **OpenTelemetry** traces. Requirement: per-tenant answer isolation, zero-downtime config changes, and no lost poison messages.

**Q1.** Which Cosmos DB vector index type best fits 5M embeddings?
A) flat  B) quantizedFlat  C) diskANN  D) HNSW

**Q2.** How should per-tenant isolation be enforced in retrieval?
A) One Cosmos account per tenant  B) `WHERE tenantId = @t` filter inside the vector query  C) Retrieve top-100, filter tenants in app code  D) Separate vector index per tenant

**Q3.** A Function keeps failing on a malformed ingestion event. What happens with default PeekLock behavior and a max delivery count of 10?
A) Message is deleted after the first failure  B) Message is redelivered until it succeeds  C) After 10 failed deliveries it moves to the dead-letter queue  D) The topic pauses until manual intervention

**Q4.** Contoso must change a config value across all instances with minimal latency and no redeploy. Which App Configuration pattern?
A) Poll every key every second  B) Restart the app on each change  C) Sentinel key + refresh interval  D) Move config to Key Vault

**Q5.** Traces must show one operation spanning Function → Service Bus → worker. What carries the correlation?
A) message_id  B) session_id  C) traceparent context in message application properties  D) The Function host instance id

---

## Section 2 — Regular questions (Q6–Q50)

**Q6.** Which command builds a container image in Azure without a local Docker daemon?
A) `docker build --cloud`  B) `az acr build -r myreg -t img:1 .`  C) `az containerapp build`  D) `az aks build`

**Q7.** A Container App must scale on Service Bus backlog and cost nothing when idle. Configure:
A) CPU scaler, minReplicas 1  B) HTTP scaler, minReplicas 0  C) KEDA azure-servicebus scaler, minReplicas 0  D) Fixed replica count 0

**Q8.** In Container Apps, changing the container image creates:
A) A new revision  B) A new environment  C) An in-place update  D) A new ingress

**Q9.** To run blue/green on Container Apps you need:
A) Single revision mode  B) Multiple revision mode with traffic weights  C) Two environments  D) KEDA

**Q10.** AKS Pod shows `CrashLoopBackOff`. First diagnostic command?
A) `kubectl get nodes`  B) `kubectl rollout undo`  C) `kubectl logs <pod> --previous`  D) `kubectl delete pod`

**Q11.** A liveness probe failure causes Kubernetes to:
A) Remove the Pod from Service endpoints  B) Restart the container  C) Cordon the node  D) Scale the Deployment

**Q12.** A readiness probe failure causes Kubernetes to:
A) Restart the container  B) Remove the Pod from Service endpoints  C) Delete the Pod  D) Nothing

**Q13.** Exit code 137 on a container usually means:
A) Image pull failed  B) OOMKilled — exceeded memory limit  C) Probe timeout  D) DNS failure

**Q14.** Which manifest field makes the scheduler guarantee a Pod 250m CPU?
A) limits.cpu  B) requests.cpu  C) priorityClass  D) qosClass

**Q15.** Service type that provisions a public cloud load balancer on AKS:
A) ClusterIP  B) NodePort  C) LoadBalancer  D) ExternalName

**Q16.** App Service container listens on port 3000. Set:
A) `PORT=3000`  B) `WEBSITES_PORT=3000`  C) `EXPOSE 3000`  D) `CONTAINER_PORT=3000`

**Q17.** Which ACR tier is required for geo-replication?
A) Basic  B) Standard  C) Premium  D) Free

**Q18.** Cosmos DB default consistency level:
A) Strong  B) Bounded Staleness  C) Session  D) Eventual

**Q19.** Cheapest Cosmos DB read pattern (~1 RU/1KB):
A) Cross-partition query  B) Point read by id + partition key  C) Query with ORDER BY  D) Change feed

**Q20.** To cut write RU cost in Cosmos DB:
A) Switch to Strong consistency  B) Exclude un-queried paths in the indexing policy  C) Increase provisioned RU/s  D) Enable TTL

**Q21.** The Cosmos DB change feed processor requires which supporting resource?
A) A lease container  B) An Event Grid topic  C) A Redis cache  D) A stored procedure

**Q22.** The change feed does NOT capture:
A) Inserts  B) Updates  C) Deletes  D) Partition key changes

**Q23.** pgvector operator for cosine distance:
A) `<->`  B) `<=>`  C) `<#>`  D) `@@`

**Q24.** Which pgvector index must be built after the table is populated?
A) HNSW  B) IVFFlat  C) B-tree  D) GIN

**Q25.** Query-time recall knob for IVFFlat:
A) lists  B) probes  C) ef_construction  D) m

**Q26.** Best way to confirm Postgres uses your vector index:
A) `SELECT * FROM pg_indexes`  B) `EXPLAIN ANALYZE` shows an Index Scan  C) Check table size  D) `VACUUM`

**Q27.** On Azure Postgres Flexible Server, pgvector must first be enabled via:
A) `CREATE ROLE vector`  B) The `azure.extensions` server parameter  C) Restarting in Burstable tier  D) Support ticket

**Q28.** Connection storms against Azure Postgres are best mitigated by:
A) Longer TLS  B) Connection pooling / PgBouncer  C) Bigger embeddings  D) Read replicas

**Q29.** Cache-aside pattern on a write:
A) Update cache, then DB  B) Update DB, then delete cache key  C) Update both in a transaction  D) Wait for TTL

**Q30.** Redis eviction policy a cache should generally use:
A) noeviction  B) volatile-ttl  C) allkeys-lru  D) volatile-random

**Q31.** `TTL mykey` returns -1. Meaning:
A) Key doesn't exist  B) Key exists with no expiry  C) Key expires in 1s  D) Error

**Q32.** RediSearch KNN queries require:
A) `DIALECT 2`  B) `LIMIT 0 0`  C) JSON only  D) Cluster mode

**Q33.** Service Bus: exactly one of several workers processes each message. Use:
A) Topic with two subscriptions  B) Queue with competing consumers  C) Event Grid  D) Event Hubs

**Q34.** Which receive mode is at-most-once?
A) PeekLock  B) ReceiveAndDelete  C) Session lock  D) Defer

**Q35.** A message dead-letters when (choose the complete set):
A) MaxDeliveryCount exceeded only  B) TTL expiry, MaxDeliveryCount exceeded, explicit dead-letter, filter evaluation errors  C) Only when the receiver crashes  D) After 24 hours always

**Q36.** Most efficient Service Bus subscription filter type:
A) SQL filter  B) Correlation filter  C) TrueFilter  D) Action filter

**Q37.** Event Grid is the right choice when you need:
A) Ordered command processing with sessions  B) Reactive fan-out of lightweight "something happened" events, push delivery  C) Competing consumers  D) Message deferral

**Q38.** Event Grid retries failed deliveries:
A) Never  B) Once  C) Exponential backoff, ~24h / 30 attempts by default  D) Until the subscription is deleted

**Q39.** To dead-letter undeliverable Event Grid events you configure:
A) A Logic App  B) A storage blob container destination  C) A second subscription  D) TTL on the topic

**Q40.** Azure Functions v2 Python model defines triggers via:
A) function.json  B) Decorators like `@app.service_bus_queue_trigger`  C) host.json  D) ARM templates

**Q41.** A function can have how many triggers?
A) One  B) Two  C) Unlimited  D) One per binding

**Q42.** Timer trigger every 5 minutes (NCRONTAB):
A) `*/5 * * * *`  B) `0 */5 * * * *`  C) `0 0 */5 * * *`  D) `5 * * * * *`

**Q43.** Cold start is avoided on which Functions plan?
A) Consumption  B) Premium / Flex Consumption  C) Free  D) Shared

**Q44.** Secrets for a Function app should live in:
A) local.settings.json in git  B) host.json  C) App settings with Key Vault references  D) The function code

**Q45.** Key Vault's recommended authorization model:
A) Access policies  B) Azure RBAC  C) SAS tokens  D) Connection strings

**Q46.** Rotating a Key Vault **secret** used by running apps means:
A) Creating a new vault  B) Setting a new version under the same secret name; apps read latest  C) Redeploying all apps  D) Exporting and reimporting

**Q47.** Soft-delete on Key Vault:
A) Is opt-in and off by default  B) Keeps deleted objects recoverable for the retention period  C) Prevents reads  D) Replaces RBAC

**Q48.** In OpenTelemetry, the `traceparent` header provides:
A) Sampling config  B) Context propagation so spans join one distributed trace  C) Authentication  D) Span attributes

**Q49.** Write KQL: exceptions in the last 24h grouped by type. The correct query is:
A) `exceptions | where timestamp > ago(24h) | summarize count() by type`  B) `exceptions | group by type`  C) `SELECT type, COUNT(*) FROM exceptions`  D) `exceptions | top 24 by timestamp`

**Q50.** `bin(TimeGenerated, 5m)` in a KQL summarize does what?
A) Filters to 5-minute-old rows  B) Floors timestamps into 5-minute buckets for aggregation  C) Samples every 5th minute  D) Joins on time

---

## Section 3 — Yes/No (no return) (Q51–Q54)

**Q51.** Strong consistency in Cosmos DB costs approximately twice the RUs of Session consistency for reads. Yes / No
**Q52.** A Container Apps revision is mutable: you can update its image in place. Yes / No
**Q53.** Event Grid pushes events to handlers; Service Bus consumers pull (or hold a lock on) messages. Yes / No
**Q54.** In Kubernetes, a readiness probe failure restarts the container. Yes / No

---

## Answer key

| Q | Ans | Domain | Why |
|---|---|---|---|
| 1 | C | data | diskANN = ANN at scale on Cosmos DB |
| 2 | B | data | metadata-filtered RAG in the query |
| 3 | C | integration | PeekLock + MaxDeliveryCount → DLQ |
| 4 | C | ops | sentinel-key refresh pattern |
| 5 | C | ops | W3C context propagation |
| 6 | B | containers | ACR Tasks |
| 7 | C | containers | KEDA scale-to-zero on queue |
| 8 | A | containers | revision-scope change |
| 9 | B | containers | traffic splitting needs multiple mode |
| 10 | C | containers | previous container logs first |
| 11 | B | containers | liveness = restart |
| 12 | B | containers | readiness = remove from endpoints |
| 13 | B | containers | 137 = SIGKILL from OOM |
| 14 | B | containers | requests drive scheduling |
| 15 | C | containers | cloud LB provisioning |
| 16 | B | containers | WEBSITES_PORT |
| 17 | C | containers | Premium gates geo-replication |
| 18 | C | data | Session is default |
| 19 | B | data | point read cheapest |
| 20 | B | data | indexing policy excludes cut write RU |
| 21 | A | data | lease container tracks progress |
| 22 | C | data | change feed = inserts/updates only |
| 23 | B | data | `<=>` cosine |
| 24 | B | data | IVFFlat clusters existing rows |
| 25 | B | data | probes at query time; lists at build |
| 26 | B | data | EXPLAIN Index Scan |
| 27 | B | data | azure.extensions = VECTOR |
| 28 | B | data | pooling/PgBouncer |
| 29 | B | data | cache-aside invalidation |
| 30 | C | data | cache eviction choice |
| 31 | B | data | -1 = no expiry (-2 = missing) |
| 32 | A | data | KNN syntax needs dialect 2 |
| 33 | B | integration | queue + competing consumers |
| 34 | B | integration | delete-on-read |
| 35 | B | integration | the four DLQ triggers |
| 36 | B | integration | correlation = exact match, cheaper |
| 37 | B | integration | Event Grid = push facts |
| 38 | C | integration | default retry policy |
| 39 | B | integration | dead-letter destination |
| 40 | B | integration | v2 decorator model |
| 41 | A | integration | one trigger per function |
| 42 | B | integration | 6-field NCRONTAB with seconds |
| 43 | B | integration | pre-warmed instances |
| 44 | C | integration | Key Vault references |
| 45 | B | ops | RBAC recommended |
| 46 | B | ops | versioned secrets |
| 47 | B | ops | soft-delete default on |
| 48 | B | ops | context propagation |
| 49 | A | ops | core KQL shape |
| 50 | B | ops | bin() buckets time |
| 51 | Yes | data | quorum reads ~2× RU |
| 52 | No | containers | revisions are immutable |
| 53 | Yes | integration | push vs pull |
| 54 | No | containers | readiness removes endpoints; liveness restarts |

## Scorecard

| Domain | Questions | Your score | Target |
|---|---|---|---|
| containers | Q6–17, 52, 54 | __ / 15 | ≥ 13 |
| data | Q1–2, 18–32, 51 | __ / 18 | ≥ 15 |
| integration | Q3, 33–44, 53 | __ / 14 | ≥ 12 |
| ops | Q4–5, 45–50 | __ / 7 | ≥ 6 |
| **Total** | | __ / 54 | **≥ 46 (85%)** |

For every miss: re-read the matching study-guide bullet, redo the matching lab step, and flag the tag in Anki for tomorrow's cram.
