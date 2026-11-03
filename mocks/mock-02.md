# Mock 02 — AI-200 retake (54 questions, 100 minutes)

Assembled from the ten retake batches (servicebus, eventgrid, functions, acr-appservice, aca-aks, cosmos, pgvector, redis, secrets-roles, otel-kql). Domain split deliberately over-samples the score report's weak skills: **containers 13 · data 15 · integration 15 · ops 11**. Every answer key was re-verified against the live Microsoft Learn pages on 2026-11-04 (the single exception is Q19, whose explicit warning lives in the upstream Kubernetes docs — see its key note). All scenarios are original; nothing is reproduced from Learn knowledge checks or real exam questions.

Rules: closed book. Bar: **≥ 85% (46/54)**. Formats mirror the Oct-10 sitting: case study, single-choice, (Select TWO) / (Select THREE), (Ordering), (Matching) — "options may be used once, more than once, or not at all" — (Dropdown), CLI/code fill-in, and a **no-return** Yes/No block (Q51–Q54): write your answer and don't change it.

---

## Case Study (Q1–Q5) — Contoso Claims

Contoso Claims runs an AI intake pipeline for insurance claims. A web API accepts scanned claim PDFs (some up to 80 MB) and must acknowledge submission in under a second. Each PDF is queued for an extraction worker that runs an LLM to pull claimant details, policy numbers, and damage estimates; extraction takes 10–90 seconds depending on document length. Multiple worker instances run in Azure Container Apps and must scale with backlog, dropping to zero overnight. A single malformed scan must not block the queue, and the claims team wants every skipped document visible for manual review within the hour. The namespace is Standard tier, and every claim needs an end-to-end trace from submission through extraction to the results store.

**Q1.** The 80 MB PDFs must be queued on the Standard-tier namespace (256 KB message limit). What's the correct approach?
A) Upgrade the namespace to Premium so the full PDF fits in one message
B) Base64-encode the PDF and split it across multiple correlated messages
C) Upload the PDF to Blob Storage and send a Service Bus message containing only the blob URI and claim metadata (claim-check pattern)
D) Compress the PDF with gzip before sending

**Q2.** (Select TWO) Which TWO configurations satisfy "scale with backlog, drop to zero overnight" for the Container Apps extraction workers?
A) A KEDA `azure-servicebus` scaler reading the queue's message count
B) An HTTP scaling rule with `minReplicas` set to 0
C) `minReplicas: 0` on the scale rule
D) A CPU-percentage scaling rule
E) `maxReplicas` left unset (unbounded)

**Q3.** (Dropdown) Select the correct values so a single malformed scan dead-letters instead of blocking the queue: receive mode = **____**; after the configured delivery attempts are exhausted, the dead-letter reason is **____**.
- Receive mode options: `PeekLock` / `ReceiveAndDelete`
- Reason options: `TTLExpiredException` / `MaxDeliveryCountExceeded` / `HeaderSizeExceeded`

**Q4.** The extraction worker's custom scale rule sets `messageCount: 5`. With 50 messages sitting in the queue, how many replicas does the scaler request?
A) 5
B) 10
C) 50
D) 1

**Q5.** The extraction worker wraps each message's processing in a span created with `kind=SpanKind.CONSUMER`. Which Application Insights table receives this span?
A) `dependencies`
B) `requests`
C) `traces`
D) `customMetrics`

---

## Section 2 — Regular questions (Q6–Q50)

**Q6.** A queue has "dead-lettering on message expiration" **disabled** (the opt-in setting). A message's TTL elapses before any receiver reads it. What happens?
A) It moves to the DLQ with reason `TTLExpiredException`
B) It is silently dropped — never routed to the DLQ
C) It blocks the queue until manually removed
D) It is redelivered with `DeliveryCount` incremented

**Q7.** (Select TWO) An App Service app pairs a main API container with a local-language-model sidecar container. Which TWO statements correctly describe how the model container must be wired?
A) Set `isMain: true` on the model container so it can receive its own external traffic
B) Set `isMain: false` on the model container and `isMain: true` on the API container
C) The API should call the model over a separate public HTTPS endpoint for isolation
D) The API should call the model at a `localhost` address on the model's target port
E) Both processes should run inside the same container image to guarantee they scale together

**Q8.** For a nightly ~2M-chunk re-embed bulk load into a Cosmos DB container, queries aren't needed until the load finishes. Which indexing change minimizes RU during the load, and what must happen afterward?
A) Switch to Eventual consistency for the duration of the load
B) Set `indexingMode: none` during the load, then switch back to `consistent` and let the index transformation complete before querying
C) Add more composite indexes so writes route faster
D) Enable lazy indexing for the container

**Q9.** A Function with managed identity `func-id` triggers on new blobs, extracts fields, and forwards each parsed invoice as a message onto a Service Bus queue — it never reads from that queue. Which single role should `func-id` receive on the Service Bus namespace to satisfy least privilege?
A) Azure Service Bus Data Owner
B) Azure Service Bus Data Receiver
C) Azure Service Bus Data Sender
D) Contributor

**Q10.** Which event schema should a custom Event Grid topic use so a third-party vendor (a non-Azure system) can consume events natively?
A) Event Grid schema
B) CloudEvents v1.0 schema
C) Custom schema with no input-schema mapping
D) Whatever schema the Blob Storage system topic uses

**Q11.** A Kubernetes `Ingress` object has been created on an AKS cluster with host and path rules, but requests to the host still fail to route anywhere. What is missing?
A) A ConfigMap holding the routing rules
B) An Ingress controller (such as the AKS application routing add-on) to actually act on the Ingress rules
C) A `LoadBalancer`-type Service
D) A PersistentVolumeClaim

**Q12.** A RAG assistant embeds documents with a 3,072-dimension model into Azure Database for PostgreSQL. The team wants an approximate index with 99%+ recall, and the table is expected to grow well past 10 million rows. Which index should they build?
A) A standard HNSW index directly on the embedding column
B) An IVFFlat index with `lists = 4000`
C) A DiskANN (`pg_diskann`) index with product quantization enabled
D) No index — rely on a sequential scan with a larger `work_mem`

**Q13.** A container image sets `configure_azure_monitor(connection_string="A")` in code, and the deployment's environment also defines `APPLICATIONINSIGHTS_CONNECTION_STRING="B"`. Which connection string does the app actually send telemetry to?
A) B — environment variables always win over code
B) A — code-provided values take the highest precedence
C) Neither — having both set raises a startup error
D) Whichever of the two was set most recently at runtime

**Q14.** A team wants a runtime-enforced retry policy (fixedDelay/exponentialBackoff) directly on a Service Bus-triggered function. What should they expect?
A) It works exactly like a Timer trigger's retry policy
B) Service Bus isn't one of the four trigger types that support retry policies (Cosmos DB, Event Hubs, Kafka, Timer) — it relies on its own binding-extension redelivery/dead-letter behavior instead
C) It works, but only in the Python v1 model
D) It works, but the maximum retry count must be -1

**Q15.** (Select THREE) A security reviewer insists every advanced ACR capability needs Premium. Which THREE capabilities are actually Premium-ONLY?
A) Geo-replication
B) Private endpoints (Private Link)
C) Content trust
D) Availability-zone redundancy
E) Repository-scoped tokens/scope maps

**Q16.** An Azure Managed Redis instance has the RediSearch module enabled. Which eviction policy must it use?
A) `allkeys-lru` — the standard cache choice
B) `volatile-lru` — the Azure Managed Redis default
C) `noeviction` — mandatory whenever RediSearch is enabled
D) `volatile-ttl` — evicts only keys with TTLs

**Q17.** (Select TWO) A Function's non-secret settings live in Azure App Configuration; a downstream API key is stored in Key Vault and referenced from App Configuration, so the Function reads both through one provider call. Which TWO role assignments must the Function's identity hold so the provider can resolve the Key Vault-referenced API key at runtime?
A) App Configuration Data Owner
B) App Configuration Data Reader
C) Key Vault Secrets User
D) Key Vault Secrets Officer
E) App Configuration Contributor

**Q18.** A session-enabled Service Bus subscription receives a message from a sender that didn't set a session id. What happens?
A) The message is processed with the session id treated as an empty string
B) The message is rejected at send, never enqueued
C) The message is dead-lettered with reason "Session ID is null"
D) The message waits indefinitely for a session to claim it

**Q19.** A team configures both a Horizontal Pod Autoscaler and a Vertical Pod Autoscaler on the same Deployment, both watching CPU utilization, hoping for extra responsiveness. What actually happens?
A) They work together safely and the Deployment scales twice as responsively
B) VPA's resource-request changes and HPA's CPU-utilization-based replica decisions conflict and fight each other — don't target the same metric with both
C) Kubernetes automatically disables one of the two autoscalers
D) HPA always takes precedence and VPA is silently ignored

**Q20.** (Select TWO) Compliance officers must see their own newly-uploaded filing immediately in their own session, while keeping read RU as low as possible. Select the TWO correct facts that satisfy this.
A) Session consistency reads cost 1x RU (single replica) — cheaper than Strong's 2x
B) Capture the session token from the upload's response headers and pass it on the subsequent read
C) Strong consistency guarantees this account-wide with no extra application code
D) Eventual consistency also guarantees read-your-writes as long as the session token is reused
E) Bounded Staleness is required to guarantee read-your-writes

**Q21.** (Select TWO) The Azure Monitor OpenTelemetry Distro for Python auto-instruments which TWO of the following with zero manual span code?
A) `requests` (HTTP client calls)
B) `boto3` (AWS SDK)
C) `psycopg2` (PostgreSQL driver)
D) `pandas` (dataframes)
E) `matplotlib` (plotting)

**Q22.** An Event Grid webhook endpoint returns `401 Unauthorized`. What does Event Grid do next?
A) Retries using the standard exponential backoff schedule
B) Never retries — on a webhook endpoint, 401 is treated the same as 400/403/413
C) Retries once immediately, then dead-letters
D) Automatically converts the subscription to pull delivery

**Q23.** An ACR registry's admin user has never been enabled. Once a developer enables it, how many passwords will it have?
A) One password, with downtime while rotating it
B) Two independent passwords, so one can rotate while the other keeps working
C) No password — admin login reuses the developer's own Entra identity
D) A single password that never expires and can't be regenerated

**Q24.** A developer runs `CREATE EXTENSION pgvector;` on a Flexible Server that already has `azure.extensions` set to `VECTOR,PG_DISKANN`. The command fails with an unrecognized-extension error. Why?
A) pgvector can only be enabled from the Azure portal, never from SQL
B) The installable extension name is `vector`, not `pgvector` — the correct command is `CREATE EXTENSION vector;`
C) `azure.extensions` values must be lowercase, and `VECTOR` is uppercase
D) `pg_diskann` must be dropped before `vector` can be created

**Q25.** (Dropdown) An App Configuration provider is configured with `refresh_on=[WatchKey("Sentinel")]` so a configuration change goes live without restarting the Function. Select the correct values: refresh_interval default = **____** seconds / minimum allowed value = **____** second.
- Default options: `30` / `60` / `300`
- Minimum options: `1` / `5` / `30`

**Q26.** Which Functions hosting plan is the only one that cannot use ZIP deployment, a container image, or source-control deployment — it has its own distinct deployment package mechanism?
A) Premium  B) Dedicated  C) Flex Consumption  D) Consumption (legacy)

**Q27.** (Select TWO) A Container Apps app named `tagger-api` runs in **single** revision mode. Which TWO statements correctly explain how it gets zero-downtime releases?
A) The platform waits for the new revision to pass health checks and match the old revision's replica count before shifting traffic
B) The team must manually run `az containerapp ingress traffic set` to move traffic to the new revision
C) The old revision deactivates automatically once the new one is healthy and fully scaled
D) Multiple revision mode must be enabled first, or there is no such thing as a zero-downtime single-revision deploy
E) Zero-downtime deploys are only possible using manual blue/green traffic splitting

**Q28.** A Cosmos DB composite index is defined as `(category ASC, price DESC)`. Which single ORDER BY clause can reuse this exact same index without creating a new one?
A) `ORDER BY category DESC, price ASC`
B) `ORDER BY category DESC, price DESC`
C) `ORDER BY price DESC, category ASC`
D) `ORDER BY category ASC`

**Q29.** An administrator runs `az role assignment create --role "Cosmos DB Built-in Data Reader" --assignee <principal-id> --scope <cosmos-account-id>` and the command fails, reporting that no such role definition exists in the subscription's role list. What's the most likely cause?
A) The role name has a typo and should be "Cosmos DB Data Reader"
B) Cosmos DB for NoSQL's data-plane roles are native to the database account, not standard Azure RBAC, so they must be assigned with `az cosmosdb sql role assignment create` instead
C) The identity needs the Cosmos DB Account Reader Role assigned first
D) Data-plane roles can only be assigned from the Azure portal

**Q30.** A Service Bus topic subscription's SQL filter rule throws an exception while evaluating an arriving message, and "dead-lettering on filter evaluation exceptions" is enabled. Where does the message end up?
A) It's silently discarded
B) It's redelivered to the publisher
C) It's moved to that subscription's dead-letter queue, with a reason describing the filter error
D) It's delivered to the subscription anyway, unfiltered

**Q31.** (Ordering) Arrange the steps to let an App Service web app pull a private image from ACR using managed identity instead of the registry admin account.
A) Set the `acrUseManagedIdentityCreds` app configuration to `true`
B) Enable a system-assigned managed identity on the web app
C) Grant that identity the `AcrPull` role scoped to the container registry
D) Restart the app and confirm the container pulls successfully

**Q32.** A team provisions a brand-new Azure Managed Redis cache, leaves the eviction policy untouched, and intends it as a pure throwaway cache (every key should be evictable under pressure). Is the out-of-the-box default correct for that intent?
A) Yes — the default is `allkeys-lru`, which evicts any key under pressure
B) No — the default is `volatile-lru`, which only evicts keys that carry a TTL
C) Yes — the default is `noeviction`, which is always safe for a pure cache
D) No — the default is `allkeys-random`

**Q33.** (Ordering) Arrange the KQL pipeline steps into the correct sequence to render a time chart of p95 request duration per cloud role over the last 24 hours:
A) `| render timechart`
B) `requests`
C) `| where timestamp > ago(24h)`
D) `| summarize percentile(duration, 95) by bin(timestamp, 1h), cloud_RoleName`

**Q34.** A team publishes one event to an Event Grid domain containing 50 tenant topics, expecting every tenant's topic to receive a copy. What actually happens?
A) All 50 topics receive the event — that's exactly what a domain is for
B) Only the one tenant topic named in the published event receives it; nothing is broadcast
C) The event is rejected because domains require a domain-scope subscription first
D) The event is dead-lettered because no `--included-event-types` was set

**Q35.** Which Container Apps Jobs trigger type should start a self-hosted GitHub Actions runner only when a workflow actually needs it?
A) Manual
B) Schedule
C) Event, using a GitHub Actions / Azure Pipelines scale rule
D) Jobs can't host CI runners — use an app instead

**Q36.** A Cosmos DB container stores 3,072-dimension embeddings (text-embedding-3-large) and has `EnableNoSQLVectorSearch` enabled. Which vector index type(s) can legally be used?
A) `flat` only
B) `quantizedFlat` or `diskANN` only — `flat`'s 505-dimension cap is exceeded
C) Any of `flat`, `quantizedFlat`, or `diskANN`
D) None — 3,072 dimensions isn't supported by any Cosmos DB vector index

**Q37.** (Ordering) Key Vault's automated secret-rotation flow via Event Grid — arrange the steps in the correct order:
A) The function stores the new credential as a new secret version in Key Vault
B) Key Vault emits a `SecretNearExpiry` event 30 days before the current version's expiration date
C) An Azure Function (or other handler) receives the event through Event Grid
D) The function generates a new credential at the target service

**Q38.** A developer wants a dedicated, GA Azure Functions binding to call Azure OpenAI for chat completions in a new project started today. What's the accurate guidance?
A) Use the `@app.generic_trigger` binding for Azure OpenAI chat completions — fully GA
B) There's no durable GA binding; call the OpenAI/Foundry SDK directly with DefaultAzureCredential, initialized once at module level — the old Azure OpenAI extension bindings are retiring 20 April 2027
C) Azure OpenAI can only be called from a Logic App, never from Functions
D) Use the Cosmos DB output binding to proxy the OpenAI call

**Q39.** (Matching) Match each App Service setting or command to what it controls. Options may be used once, more than once, or not at all.
1. `WEBSITES_PORT`
2. `WEBSITES_ENABLE_APP_SERVICE_STORAGE`
3. `acrUseManagedIdentityCreds`
4. `--slot-settings`

A) Keeps a value pinned to one deployment slot across a slot swap
B) Routes platform traffic to a non-default container listen port
C) Switches the ACR image-pull mechanism from admin credentials to managed identity
D) Persists container writes under `/home` across restarts and scale-out instances
E) Builds an image in the cloud without a local Docker daemon

**Q40.** A catalog search on Azure Database for PostgreSQL filters `WHERE category = 'rare_tag'`, then orders by an HNSW cosine index and applies `LIMIT 10`. For this rarely used category, fewer than 10 rows come back even though more than 10 matching rows exist in the table. What is the most likely cause?
A) The HNSW graph is corrupted and must be rebuilt
B) The ANN index found its nearest neighbors first; most didn't match the filter, so the result undershoots LIMIT before enough matches surface
C) Cosine distance cannot be combined with a WHERE clause
D) JSONB columns cannot be filtered using a WHERE clause

**Q41.** (Matching) Match each scenario to the single best-fitting role. Options may be used once, more than once, or not at all.

Options: A) Storage Blob Data Owner B) Azure Service Bus Data Sender C) Cosmos DB Built-in Data Reader D) Key Vault Secrets User E) Monitoring Metrics Publisher F) Azure Kubernetes Service RBAC Reader

1. A Functions host identity needs the minimum access to its own `AzureWebJobsStorage` account for internal blob-lease coordination (e.g. the Timer trigger's singleton lock).
2. A nightly batch job's managed identity must publish custom metrics to Azure Monitor and do nothing else.
3. A support engineer must view most Kubernetes objects in a namespace but must never be able to read Secrets.

**Q42.** (Ordering) Four of Event Grid's exponential-backoff retry waypoints are listed below out of order. Arrange them from first retry to last:
A) 5 minutes
B) 10 seconds
C) 1 hour
D) 30 seconds

**Q43.** (Ordering) Arrange the steps of a Container Apps **single revision mode** deploy into the correct sequence.
A) Traffic shifts entirely to the new revision
B) The new revision is provisioned and starts warming up
C) The new revision passes its health checks and reaches the old revision's replica count
D) The old revision deactivates and stops consuming resources

**Q44.** (Ordering) Put these steps in the correct order to safely add a new Cosmos DB composite index and retire an old one without ever degrading query correctness.
A) Remove the old, no-longer-needed composite index in a single follow-up policy update
B) Update the indexing policy to add the new composite index definition
C) Monitor index transformation progress until it reaches 100% (portal or SDK)
D) Confirm queries that should use the new composite index return correct, complete results

**Q45.** (CLI fill-in) Write the `az eventgrid` CLI flags to update event subscription `moderation-sub` so it stops retrying after 2 hours OR 5 attempts, whichever comes first (flags + values only).

**Q46.** (Matching) Match each AKS scaling method to what actually triggers it. Options may be used once, more than once, or not at all.
1. Horizontal Pod Autoscaler (HPA)
2. Vertical Pod Autoscaler (VPA)
3. Cluster Autoscaler
4. KEDA

A) Pods stuck `Pending` because the node pool lacks capacity
B) CPU/memory utilization or request rate across identical replicas
C) An external event source such as queue depth, including true scale-to-zero
D) Right-sizing a Pod's own CPU/memory requests (non-parallelizable workloads)
E) A fixed replica count set manually by an operator

**Q47.** (Matching) Match each Redis term to its description. Options may be used once, more than once, or not at all.
1. `XACK`
2. `PUBLISH`
3. `EF_RUNTIME`
4. `KEEPTTL`
5. `SCAN`

A) Marks a Streams message as successfully processed by a consumer-group member
B) Broadcasts to every current channel subscriber; lost if nobody is listening
C) Tunes an HNSW query's speed/accuracy trade-off
D) Preserves a key's existing TTL across a `SET` overwrite
E) Non-blocking, cursor-based iteration over the keyspace
F) Required clustering policy for RediSearch

**Q48.** (Matching) Match each fact to the Cosmos DB change feed mode it describes. Options may be used once, more than once, or not at all.
1. Captures hard deletes with explicit operation-type metadata
2. Enabled by default with zero configuration
3. Requires continuous backups (point-in-time restore) on the account
4. Can start reading from the very beginning of the container's history
5. All requests use Gateway connection mode regardless of app configuration

Options: A) Latest version mode  B) All versions and deletes mode  C) Both modes  D) Neither mode

**Q49.** (Matching) Match each pgvector distance operator or function to what it computes. Options may be used once, more than once, or not at all.
1. `<->`
2. `<=>`
3. `<#>`
4. `l1_distance()`

A) Cosine distance
B) Euclidean (L2) distance
C) Negative inner product
D) Taxicab (L1) distance — function only, no dedicated operator in Azure's pgvector docs
E) Hamming distance

**Q50.** (CLI fill-in) Complete the Azure CLI command to enable vector search on an existing Cosmos DB account named `contoso-filings` in resource group `rg-contoso`:
`az cosmosdb update -n contoso-filings -g rg-contoso --capabilities ____`

---

## Section 3 — Yes/No, no-return (Q51–Q54)

**Q51.** A repository-scoped, non-Microsoft Entra access token can be created on a Basic-tier Azure Container Registry. Yes / No

**Q52.** Bounded Staleness consistency can technically be configured on a Cosmos DB account that has multiple write regions. Yes / No

**Q53.** A Flex Consumption function app can configure deployment slots the same way a Premium-plan app can. Yes / No

**Q54.** Azure dashboard tiles pinned from a log query update in real time as new telemetry arrives. Yes / No

---

## Answer key

| Q | Ans | Domain | Why |
|---|---|---|---|
| 1 | C | integration | claim-check pattern: send the blob URI, not the payload; works on any tier (Standard 256 KB; oversize is rejected at send, never dead-lettered) |
| 2 | A, C | integration | KEDA `azure-servicebus` scaler reads queue depth; `minReplicas: 0` allows scale-to-zero — HTTP/CPU scalers can't see backlog |
| 3 | PeekLock / MaxDeliveryCountExceeded | integration | PeekLock + MaxDeliveryCount exhausts retries then dead-letters the poison message |
| 4 | B | containers | documented example: `messageCount: 5` with 50 messages → 50 ÷ 5 = 10 replicas |
| 5 | B | ops | `SpanKind.CONSUMER` (like `SERVER`) = inbound work → `requests`; `CLIENT`/`INTERNAL`/`PRODUCER` → `dependencies` |
| 6 | B | integration | dead-lettering-on-expiration is opt-in; disabled = expired messages are just dropped |
| 7 | B, D | containers | main is `isMain:true`/external; sidecars are `isMain:false`, reached over `localhost` on their target port |
| 8 | B | data | `indexingMode: none` removes write-time index overhead; switch back + wait for transformation before querying |
| 9 | C | ops | send-only ⇒ Azure Service Bus Data Sender; Receiver can't send, Owner/Contributor too broad |
| 10 | B | integration | CloudEvents is the open CNCF schema — parseable without Event-Grid-specific code |
| 11 | B | containers | a `Service` does L4 routing; an `Ingress` object is inert without a running Ingress controller |
| 12 | C | data | HNSW/IVFFlat cap at 2,000 indexable dims; 3,072-dim needs DiskANN + product quantization |
| 13 | B | ops | code beats the env var for the connection string (sampling config is the opposite precedence) |
| 14 | B | integration | live doc table: retry policies only for Cosmos DB, Event Hubs, Kafka, Timer triggers |
| 15 | A, B, C | containers | geo-replication, private link and content trust are Premium-only; zone redundancy + repository-scoped tokens are on every SKU (limits 100/500/50,000) — the classic trap |
| 16 | C | data | RediSearch forces `noeviction` (and Enterprise clustering) — mandatory, not a preference |
| 17 | B, C | ops | identity needs Data Reader on the store (read the pointer) AND Key Vault Secrets User on the vault (resolve the value) |
| 18 | C | integration | session-enabled entities dead-letter null-session-id messages with reason "Session ID is null" |
| 19 | B | containers | HPA and VPA must never target the same metric — VPA rewrites requests while HPA scales replicas on that same signal (mechanics on the Learn page; explicit warning is in upstream Kubernetes VPA docs) |
| 20 | A, B | data | Session = 1x RU + read-your-writes only when the session token is carried forward; Strong/Bounded cost 2x |
| 21 | A, C | ops | `requests` and `psycopg2` are named auto-instrumentations; boto3/pandas/matplotlib are untouched |
| 22 | B | integration | webhook endpoints never retry 400/401/403/413 (Azure-resource endpoints differ) |
| 23 | B | containers | ACR admin account always has two independent passwords for rotation without downtime |
| 24 | B | data | the binary/extension name is `vector`; `pgvector` is only the community nickname |
| 25 | 30 / 1 | ops | `refresh_interval` default 30s, minimum enforced 1s (azure-appconfiguration-provider source) |
| 26 | C | integration | package deployment is the ONLY code deployment technology Flex Consumption supports |
| 27 | A, C | containers | single revision mode is zero-downtime automatically: health checks + replica-count match, then old revision deactivates |
| 28 | A | data | full reversal of all directions is served by the same composite index; mixed reversal / reordered keys are not |
| 29 | B | ops | Cosmos DB for NoSQL data-plane RBAC is native, account-scoped — `az cosmosdb sql role assignment create`, not Azure RBAC |
| 30 | C | integration | opt-in setting dead-letters the offending message in that subscription's DLQ with the filter error |
| 31 | B -> C -> A -> D | containers | enable identity, grant AcrPull, flip `acrUseManagedIdentityCreds`, then verify |
| 32 | B | data | Azure Managed Redis default eviction is `volatile-lru` — no-TTL keys are unevictable under it |
| 33 | B -> C -> D -> A | ops | table, filter, aggregate/bin, render — `render` must be the final pipe stage |
| 34 | B | integration | Event Grid domains never broadcast; the publisher names one target topic per event |
| 35 | C | containers | Jobs' Event trigger type supports a GitHub Actions/Azure Pipelines scale rule to start runners on demand |
| 36 | B | data | `flat` caps at 505 dims; `quantizedFlat`/`diskANN` allow up to 4,096 |
| 37 | B -> C -> D -> A | ops | SecretNearExpiry (30 days out) → handler via Event Grid → generate new credential → store as new secret version |
| 38 | B | integration | no GA OpenAI binding; SDK + DefaultAzureCredential; extension retires 2027-04-20 (preview bundles ≥4.60.0 already exclude it) |
| 39 | 1-B, 2-D, 3-C, 4-A | containers | E (`az acr build`) is an ACR Tasks command, not an App Service setting — unused by design |
| 40 | B | data | ANN index returns nearest neighbours first, filter applied after — selective filters undershoot LIMIT; raise ef_search/probes, partial index, or DiskANN iterative_search |
| 41 | 1-A, 2-E, 3-F | ops | blob-lease rights = Storage Blob Data Owner; metrics-only = Monitoring Metrics Publisher; read-without-Secrets = AKS RBAC Reader |
| 42 | B -> D -> A -> C | integration | official schedule: 10s, 30s, 1 min, 5 min, 10 min, 30 min, 1 hr, 3 hr, 6 hr, then every 12 hr |
| 43 | B -> C -> A -> D | containers | provision → health checks + replica match → shift traffic → deactivate old |
| 44 | B -> C -> D -> A | data | add new index, wait for transformation, verify correctness, only then remove the old one |
| 45 | `--event-ttl 120 --max-delivery-attempts 5` | integration | TTL is in minutes (120 = 2 h); Event Grid stops at whichever limit hits first |
| 46 | 1-B, 2-D, 3-A, 4-C | containers | E (manual fixed replicas) describes no autoscaler — unused by design |
| 47 | 1-A, 2-B, 3-C, 4-D, 5-E | data | F describes a clustering policy, not a command — unused distractor |
| 48 | 1-B, 2-A, 3-B, 4-A, 5-B | data | deletes/PITR-requirement/Gateway-only = All versions and deletes; zero-config + from-the-beginning = Latest version (mode is GA today) |
| 49 | 1-B, 2-A, 3-C, 4-D | data | `<->`=L2, `<=>`=cosine, `<#>`=negative inner product; L1 is function-only; E (Hamming) unused |
| 50 | EnableNoSQLVectorSearch | data | `az cosmosdb update --capabilities EnableNoSQLVectorSearch`; auto-approved, up to ~15 min to take effect |
| 51 | Yes | containers | repository-scoped tokens + scope maps exist on all three SKUs (limits differ) |
| 52 | Yes | data | only Strong is hard-blocked on multi-write-region accounts; Bounded Staleness allowed (min K/T = 100,000 writes / 300 s; docs call it an anti-pattern) |
| 53 | No | integration | Flex Consumption supports no deployment slots at all; Premium supports 3 |
| 54 | No | ops | dashboard tiles refresh on a schedule; Live Metrics is the real-time tool |

## Scorecard

| Domain | Questions | Your score | Target |
|---|---|---|---|
| containers (Sec 1) | Q4, Q7, Q11, Q15, Q19, Q23, Q27, Q31, Q35, Q39, Q43, Q46, Q51 (13) | __ / 13 | ≥ 11 |
| data (Sec 2) | Q8, Q12, Q16, Q20, Q24, Q28, Q32, Q36, Q40, Q44, Q47, Q48, Q49, Q50, Q52 (15) | __ / 15 | ≥ 13 |
| integration (Sec 3) | Q1, Q2, Q3, Q6, Q10, Q14, Q18, Q22, Q26, Q30, Q34, Q38, Q42, Q45, Q53 (15) | __ / 15 | ≥ 13 |
| ops (Sec 4) | Q5, Q9, Q13, Q17, Q21, Q25, Q29, Q33, Q37, Q41, Q54 (11) | __ / 11 | ≥ 9 |
| **Total** | | **__ / 54** | **≥ 46 (85%)** |

## Weak-skill map (drill every miss the same day)

All Anki searches are within `deck:AI-200`; add `tag:retake1` to scope to the new cards.

| Q | Study-guide skill | Anki drill | Learn URL | From |
|---|---|---|---|---|
| 1 | Sec 3 · Service Bus — messages | `tag:servicebus tag:tiers` | https://learn.microsoft.com/en-us/training/modules/queue-process-operations-service-bus/4-structure-messages-ai-workloads/ | servicebus Q1 |
| 2 | Sec 3 · Service Bus — at scale | `tag:servicebus tag:keda` | https://learn.microsoft.com/en-us/azure/container-apps/scale-app | servicebus Q2 |
| 3 | Sec 3 · Service Bus — DLQ handling | `tag:servicebus tag:dlq` | https://learn.microsoft.com/en-us/training/modules/queue-process-operations-service-bus/5-process-messages-reliably/ | servicebus Q3 |
| 4 | Sec 1 · KEDA scaling in Container Apps | `tag:aca tag:keda` | https://learn.microsoft.com/en-us/training/modules/scale-containers-azure-container-apps/3-event-driven-scaling-keda | aca-aks Q1 |
| 5 | Sec 4 · OpenTelemetry SDK tracing | `tag:otel` | https://learn.microsoft.com/en-us/training/modules/instrument-app-opentelemetry/5-export-telemetry-azure-monitor | otel-kql Q1 |
| 6 | Sec 3 · Service Bus — DLQ handling | `tag:servicebus tag:dlq` | https://learn.microsoft.com/en-us/azure/service-bus-messaging/message-expiration | servicebus Q4 |
| 7 | Sec 1 · App Service containers (sidecars) | `tag:appservice tag:sidecar` | https://learn.microsoft.com/en-us/azure/app-service/overview-sidecar | acr-appservice Q2 |
| 8 | Sec 2 · Cosmos — indexing policies for RU | `tag:cosmos tag:indexing` | https://learn.microsoft.com/en-us/azure/cosmos-db/index-policy | cosmos Q1 |
| 9 | Sec 4 · Key Vault/App Config — RBAC roles | `tag:roles tag:servicebus` | https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-managed-service-identity | secrets-roles Q1 |
| 10 | Sec 3 · Event Grid — custom events | `tag:eventgrid tag:schema` | https://learn.microsoft.com/en-us/azure/event-grid/cloud-event-schema | eventgrid Q1 |
| 11 | Sec 1 · AKS — connectivity | `tag:aks tag:ingress` | https://learn.microsoft.com/en-us/azure/aks/app-routing | aca-aks Q4 |
| 12 | Sec 2 · Postgres — pgvector latency/compute | `tag:pgvector tag:diskann` | https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-optimize-performance-pgvector | pgvector Q1 |
| 13 | Sec 4 · OpenTelemetry SDK tracing | `tag:otel` | https://learn.microsoft.com/en-us/training/modules/instrument-app-opentelemetry/3-add-opentelemetry-sdk | otel-kql Q2 |
| 14 | Sec 3 · Functions — triggers and bindings | `tag:functions tag:retry` | https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-error-pages | functions Q4 |
| 15 | Sec 1 · ACR — tiers | `tag:acr` | https://learn.microsoft.com/en-us/azure/container-registry/container-registry-skus | acr-appservice Q4 |
| 16 | Sec 2 · Redis — vector indexing | `tag:redis tag:modules` | https://learn.microsoft.com/en-us/azure/redis/plan-redis-modules | redis Q1 |
| 17 | Sec 4 · App Configuration + Key Vault | `tag:appconfig tag:keyvault` | https://learn.microsoft.com/en-us/azure/azure-app-configuration/concept-enable-rbac | secrets-roles Q2 |
| 18 | Sec 3 · Service Bus — sessions | `tag:servicebus tag:sessions` | https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues | servicebus Q5 |
| 19 | Sec 1 · AKS — scaling | `tag:aks tag:keda` | https://learn.microsoft.com/en-us/azure/aks/concepts-scale | aca-aks Q5 |
| 20 | Sec 2 · Cosmos — consistency levels | `tag:cosmos tag:consistency` | https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels | cosmos Q2 |
| 21 | Sec 4 · OpenTelemetry SDK tracing | `tag:otel` | https://learn.microsoft.com/en-us/training/modules/instrument-app-opentelemetry/3-add-opentelemetry-sdk | otel-kql Q3 |
| 22 | Sec 3 · Event Grid — retries | `tag:eventgrid tag:retry` | https://learn.microsoft.com/en-us/azure/event-grid/delivery-and-retry | eventgrid Q4 |
| 23 | Sec 1 · ACR — authentication | `tag:acr` | https://learn.microsoft.com/en-us/azure/container-registry/container-registry-authentication | acr-appservice Q5 |
| 24 | Sec 2 · Postgres — pgvector setup | `tag:pgvector tag:extensions` | https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-use-pgvector | pgvector Q4 |
| 25 | Sec 4 · App Configuration | `tag:appconfig` | https://learn.microsoft.com/en-us/azure/azure-app-configuration/howto-best-practices | secrets-roles Q3 |
| 26 | Sec 3 · Functions — deploy function apps | `tag:functions tag:deploy` | https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies | functions Q5 |
| 27 | Sec 1 · Container Apps — revision management | `tag:aca tag:revisions` | https://learn.microsoft.com/en-us/training/modules/scale-containers-azure-container-apps/6-revision-modes-traffic-management | aca-aks Q2 |
| 28 | Sec 2 · Cosmos — composite indexes | `tag:cosmos tag:indexing` | https://learn.microsoft.com/en-us/training/modules/optimize-query-performance-azure-cosmos-db/3-configure-range-composite-indexes | cosmos Q4 |
| 29 | Sec 4 · RBAC — Cosmos data plane | `tag:roles tag:cosmosdb` | https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/security/how-to-grant-data-plane-role-based-access | secrets-roles Q4 |
| 30 | Sec 3 · Service Bus — topic filters | `tag:servicebus tag:filters` | https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues | servicebus Q6 |
| 31 | Sec 1 · App Service — pull from ACR | `tag:acr tag:appservice` | https://learn.microsoft.com/en-us/azure/app-service/tutorial-custom-container | acr-appservice Q7 |
| 32 | Sec 2 · Redis — expiration/invalidation | `tag:redis tag:eviction` | https://learn.microsoft.com/en-us/azure/redis/best-practices-memory-management | redis Q5 |
| 33 | Sec 4 · KQL | `tag:kql` | https://learn.microsoft.com/en-us/training/modules/analyze-telemetry-logs-metrics/2-write-basic-kql-queries | otel-kql Q4 |
| 34 | Sec 3 · Event Grid — domains | `tag:eventgrid` | https://learn.microsoft.com/en-us/azure/event-grid/event-domains | eventgrid Q6 |
| 35 | Sec 1 · Container Apps — jobs | `tag:aca tag:jobs` | https://learn.microsoft.com/en-us/azure/container-apps/jobs | aca-aks Q6 |
| 36 | Sec 2 · Cosmos — vector search | `tag:cosmos tag:vector` | https://learn.microsoft.com/en-us/azure/cosmos-db/index-policy | cosmos Q5 |
| 37 | Sec 4 · Key Vault — rotation | `tag:keyvault` | https://learn.microsoft.com/en-us/training/modules/manage-app-secrets-key-vault/4-handle-versioning-rotation/ | secrets-roles Q5 |
| 38 | Sec 3 · Functions — AI patterns | `tag:functions tag:openai` | https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-openai | functions Q6 |
| 39 | Sec 1 · App Service — settings | `tag:appservice` | https://learn.microsoft.com/en-us/training/modules/deploy-containers-azure-app-service/3-configure-runtime/ | acr-appservice Q9 |
| 40 | Sec 2 · Postgres — RAG metadata filter | `tag:pgvector tag:rag` | https://learn.microsoft.com/en-us/training/modules/optimize-vector-search-azure-database-postgresql/4-optimize-data-layout/ | pgvector Q5 |
| 41 | Sec 4 · RBAC role matching | `tag:roles` | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles | secrets-roles Q6 |
| 42 | Sec 3 · Event Grid — retries | `tag:eventgrid tag:retry` | https://learn.microsoft.com/en-us/azure/event-grid/delivery-and-retry | eventgrid Q8 |
| 43 | Sec 1 · Container Apps — revisions | `tag:aca tag:revisions` | https://learn.microsoft.com/en-us/training/modules/scale-containers-azure-container-apps/6-revision-modes-traffic-management | aca-aks Q7 |
| 44 | Sec 2 · Cosmos — index transformation | `tag:cosmos tag:indexing` | https://learn.microsoft.com/en-us/azure/cosmos-db/index-policy | cosmos Q7 |
| 45 | Sec 3 · Event Grid — delivery config | `tag:eventgrid tag:retry` | https://learn.microsoft.com/en-us/azure/event-grid/manage-event-delivery | eventgrid Q10 |
| 46 | Sec 1 · AKS — scaling methods | `tag:aks` | https://learn.microsoft.com/en-us/azure/aks/concepts-scale | aca-aks Q9 |
| 47 | Sec 2 · Redis — data operations | `tag:redis tag:messaging` | https://learn.microsoft.com/en-us/training/modules/implement-event-messaging-azure-managed-redis/3-redis-streams | redis Q8 |
| 48 | Sec 2 · Cosmos — change feed | `tag:cosmos tag:changefeed` | https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/change-feed-modes | cosmos Q9 |
| 49 | Sec 2 · Postgres — distance operators | `tag:pgvector` | https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-use-pgvector | pgvector Q8 |
| 50 | Sec 2 · Cosmos — vector search setup | `tag:cosmos tag:vector` | https://learn.microsoft.com/en-us/training/modules/implement-vector-search-azure-cosmos-db/2-store-retrieve-embeddings | cosmos Q10 |
| 51 | Sec 1 · ACR — tokens | `tag:acr` | https://learn.microsoft.com/en-us/azure/container-registry/container-registry-token-based-repository-permissions | acr-appservice Q11 |
| 52 | Sec 2 · Cosmos — consistency levels | `tag:cosmos tag:consistency` | https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels | cosmos Q12 |
| 53 | Sec 3 · Functions — hosting plans | `tag:functions tag:hosting` | https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale | functions Q11 |
| 54 | Sec 4 · KQL / dashboards | `tag:kql tag:appinsights` | https://learn.microsoft.com/en-us/training/modules/analyze-telemetry-logs-metrics/4-build-dashboards-app-telemetry | otel-kql Q6 |
