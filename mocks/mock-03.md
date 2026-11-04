# Mock 03 — AI-200 (54 questions, 100 minutes)

Built fresh for the retake sprint from the study guide's four skill areas at their published weights: containers 20–25%, data 25–30%, connect and consume 20–25% (integration), secure, monitor and troubleshoot 20–25% (ops). The split is **containers 13 · data 15 · integration 13 · ops 13**, so every area lands near its weight. The scenarios are original.

Rules: closed book. Bar: **≥ 85% (46/54)**. Formats mirror the sitting: case study, single choice, (Select TWO), (Ordering), (Matching), (Dropdown), CLI or code fill-in, and a **no-return** Yes/No block (Q51–Q54): write your answer and don't change it.

---

## Case Study (Q1–Q5) — Litware Logistics

Litware Logistics turns scanned bills of lading (BOLs) into searchable shipment records. Customers upload a BOL through an intake API hosted as a custom container on App Service. The upload is written to Blob Storage, and Event Grid forwards the Blob Created event to a Service Bus queue. An OCR worker on Azure Container Apps scales on that queue with KEDA, runs OCR, and stores 1,536-dimension embeddings in Cosmos DB for NoSQL, partitioned by tenant. The OCR vendor key lives in Key Vault, and the API reads it through an App Service Key Vault reference. Runtime settings live in App Configuration. Every upload must be traceable from the API request to the OCR worker.

**Q1.** The vendor rotates the OCR key every 90 days, and the API must pick up each new key without a redeploy. Which app setting value should the team use?
A) `@Microsoft.KeyVault(SecretUri=https://litware-kv.vault.azure.net/secrets/ocr-key/9f1c2e7a)`
B) `@Microsoft.KeyVault(SecretUri=https://litware-kv.vault.azure.net/secrets/ocr-key)`
C) The key typed in as plain text, and edited by hand at each rotation
D) `@Microsoft.KeyVault(SecretUri=https://litware-kv.vault.azure.net/)`

**Q2.** (Select TWO) The API publishes each BOL message to the queue, and the OCR worker must continue the same trace. Which TWO statements are correct?
A) The API writes the W3C `traceparent` value into the message's application properties
B) Service Bus propagates trace context on its own, so no application code is needed
C) The worker calls `propagate.extract()` on the message's application properties to continue the trace
D) Setting `message_id` to the HTTP request ID links the two spans
E) The trace ID is copied into the message's `content_type`

**Q3.** (Dropdown) The OCR worker's Container App sets no scale limits. Select the defaults: minimum replicas per revision = **____**; maximum replicas per revision = **____**.
- Minimum options: `0` / `1`
- Maximum options: `10` / `100`

**Q4.** (Ordering) Arrange the steps to ship a new OCR worker image without a local Docker daemon.
A) Check that the new revision is healthy with `az containerapp revision list`
B) Build and push the image in the cloud with `az acr build`
C) Point the Container App at the new image tag with `az containerapp update --image`
D) Lock the built tag with `az acr repository update --write-enabled false`

**Q5.** One tenant's container holds 300 BOL embeddings and uses a `diskANN` vector index. Its vector queries are slow and cost more RU than expected. What explains this?
A) `diskANN` needs one physical partition per tenant
B) `diskANN` needs at least 1,000 indexed vectors; below that, each query runs as a full scan
C) 1,536-dimension vectors are supported only by the `flat` index
D) Vector search requires the consistent indexing mode to be set to `none`

---

## Section 2 — Regular questions (Q6–Q50)

**Q6.** A team wants the image rebuilt every night at 02:00 UTC, whether or not the code changed. Which ACR Tasks trigger fits?
A) Source code commit trigger
B) Base image update trigger
C) Timer (schedule) trigger
D) Pull request trigger

**Q7.** (Select TWO) Which TWO statements about an App Service app setting that holds a Key Vault reference are correct?
A) The app's identity needs read access to the secret, such as the Key Vault Secrets User role
B) The value takes the form `@Microsoft.KeyVault(SecretUri=...)`
C) The secret is stored in the app setting in plain text beside the reference
D) The reference fails to resolve unless it includes a version
E) Key Vault references require the Premium plan

**Q8.** Which change to a Container App creates a new revision?
A) Shifting ingress traffic weights between two existing revisions
B) Turning ingress off and back on
C) Changing the container image tag
D) Rotating a secret value

**Q9.** (Matching) Match each scaling need to the scale rule type that fits. Options may be used once, more than once, or not at all.
1. Scale on the number of messages waiting in a Service Bus queue
2. Scale on the number of concurrent HTTP requests
3. Scale on average CPU utilization across replicas
4. Scale on the number of concurrent TCP connections

A) Custom rule with type `azure-servicebus`
B) HTTP scale rule
C) Custom rule with type `cpu`
D) TCP scale rule
E) Fixed replica count with no scale rule

**Q10.** A Pod stays `Pending`, and its events show `FailedScheduling: Insufficient cpu`. Which command shows that scheduling reason for one Pod?
A) `kubectl logs <pod>`
B) `kubectl describe pod <pod>`
C) `kubectl exec <pod> -- top`
D) `kubectl port-forward <pod> 8080:80`

**Q11.** (Ordering) Arrange the steps to roll back a bad Deployment `catalog-api` on AKS.
A) `kubectl rollout undo deployment/catalog-api`
B) `kubectl rollout status deployment/catalog-api` shows the rollout is stuck
C) `kubectl rollout history deployment/catalog-api` to find the last good revision
D) `kubectl rollout status deployment/catalog-api` again to confirm the rollback

**Q12.** A Container App must accept calls only from other apps in the same environment, never from the internet. Which setting does this?
A) Ingress `external: false` (internal ingress)
B) Ingress `external: true` with an IP restriction
C) `minReplicas: 1`
D) Dapr enabled

**Q13.** Why should app settings that hold Key Vault references usually be marked as slot settings?
A) So staging and production each keep their own vault values through a slot swap
B) Because slot settings are encrypted and ordinary settings are not
C) Because a slot cannot read Key Vault unless the setting is a slot setting
D) Because slot settings replace the managed identity

**Q14.** A team must copy `nginx:1.27` from Docker Hub into its registry without a local Docker daemon. Which command does this?
A) `docker push litwarereg.azurecr.io/nginx:1.27`
B) `az acr import --name litwarereg --source docker.io/library/nginx:1.27 --image nginx:1.27`
C) `az acr build --registry litwarereg --image nginx:1.27 .`
D) `az acr run --registry litwarereg --cmd "pull nginx" /dev/null`

**Q15.** (CLI fill-in) Write the Azure CLI command that streams live console logs from the Container App `ocr-worker` in resource group `rg-litware`.

**Q16.** A Deployment's Pods must run only on nodes labelled `pool=gpu`. Which Pod spec field enforces this?
A) `spec.template.spec.nodeSelector`
B) `spec.template.spec.affinity.podAntiAffinity`
C) `spec.template.spec.tolerations`
D) `spec.template.spec.priorityClassName`

**Q17.** Which Python SDK call reads one known item in a single request, when you already have its `id` and partition key value?
A) `container.query_items(query="SELECT * FROM c WHERE c.id = @id")`
B) `container.read_item(item="bol-1042", partition_key="contoso")`
C) `container.upsert_item(body=doc)`
D) `container.query_items_change_feed(start_time="Beginning")`

**Q18.** (Select TWO) Which TWO statements about Cosmos DB queries and the partition key are correct?
A) A query that omits the partition key fans out across partitions and costs more RU
B) A query that filters on the partition key path routes to a single partition
C) Cross-partition queries are not supported in Cosmos DB for NoSQL
D) A point read can omit the partition key and stay cheap
E) Adding `TOP 1` makes any query single-partition

**Q19.** (Code fill-in) Write the query body that returns the five chunks nearest to the query vector `@q` in the container, nearest first, with each chunk's `id` and a `score` alias.

**Q20.** Which Python call reads the latest-version change feed of a container from the beginning?
A) `container.read_all_items()`
B) `container.query_items_change_feed(start_time="Beginning")`
C) `container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True)`
D) `container.query_items_change_feed(mode="AllVersionsAndDeletes", start_time="Beginning")`

**Q21.** Which pgvector HNSW index option sets the maximum number of connections per graph layer, with a default of 16?
A) `hnsw.ef_search`
B) `m`
C) `lists`
D) `probes`

**Q22.** A tenant's HNSW search returns fewer rows than requested. Which change raises the candidate list at query time, without rebuilding the index?
A) `SET hnsw.ef_construction = 200`
B) `SET hnsw.ef_search = 100`
C) `SET ivfflat.probes = 100`
D) `SET maintenance_work_mem = '8GB'`

**Q23.** A 3,072-dimension embedding column needs an approximate index in pgvector 0.8.x without DiskANN. Which column type fits?
A) `vector(3072)` with an HNSW index
B) `halfvec(3072)` with an HNSW index
C) `vector(3072)` with an IVFFlat index
D) `text` holding the embedding as JSON

**Q24.** An app should pool connections through the built-in PgBouncer on an Azure Database for PostgreSQL flexible server. Which port does it connect to?
A) 5432
B) 6432
C) 8432
D) 5439

**Q25.** Which Redis command returns a key's value and resets its expiry in one atomic step?
A) `GET` followed by `EXPIRE`
B) `GETEX key EX 60`
C) `SETNX key value`
D) `GETDEL key`

**Q26.** A team adds `/notes/*` to `excludedPaths` to cut write RU. What happens to queries that filter on `notes`?
A) They fail with a configuration error
B) They still run, but as a full scan with higher RU
C) They return only results from the last 24 hours
D) They are served from a lazy index

**Q27.** A container needs TTL on its items, and a bulk load wants `indexingMode: none`. What happens?
A) Both work together, and TTL pauses during the load
B) The `none` mode is rejected while TTL is enabled, because TTL requires indexing
C) TTL is silently disabled during the load
D) The load runs faster because TTL stops the index

**Q28.** A RediSearch index must filter vectors by tenant with `@tenant:{contoso}`. How must `tenant` be declared in `FT.CREATE`?
A) `tenant TEXT`
B) `tenant TAG`
C) `tenant NUMERIC`
D) Not declared; hash fields are filterable automatically

**Q29.** (Ordering) Arrange the steps to set up pgvector and index a table on an Azure Database for PostgreSQL flexible server.
A) Create the HNSW index on the embedding column with `vector_cosine_ops`
B) Allow `vector` in `azure.extensions`, then run `CREATE EXTENSION vector;`
C) Create the table with an `embedding vector(1536)` column
D) Bulk-load the rows with `COPY`

**Q30.** (Select TWO) Which TWO statements about Service Bus sessions are correct?
A) A session receiver holds an exclusive lock on one session and receives that session's messages in order
B) Sessions are supported on the Standard tier but not on Basic
C) Sessions require the Premium tier
D) Two receivers can hold the lock on the same session at the same time
E) Sessions guarantee exactly-once delivery

**Q31.** A message must become visible to receivers at 09:00 UTC tomorrow. Which Python SDK call handles this?
A) `sender.send_messages(msg)` with `time_to_live` set to nine hours
B) `sender.schedule_messages([msg], schedule_time_utc=...)`
C) `receiver.defer_message(msg)`
D) `admin.create_queue(...)` with `auto_delete_on_idle` set

**Q32.** A subscription must receive only events whose `data.sizeBytes` is greater than 10485760. Which advanced filter does this?
A) `{"operatorType": "NumberGreaterThan", "key": "data.sizeBytes", "value": 10485760}`
B) `{"operatorType": "StringContains", "key": "data.sizeBytes", "values": ["10485760"]}`
C) `{"operatorType": "NumberIn", "key": "data.sizeBytes", "values": [10485760]}`
D) `{"operatorType": "NumberLessThan", "key": "data.sizeBytes", "value": 10485760}`

**Q33.** Which subscription filter delivers Blob Created events only for the `bols` container of one storage account?
A) `--subject-ends-with bols`
B) `--subject-begins-with /blobServices/default/containers/bols/`
C) `--subject-begins-with bols`
D) `--subject-begins-with /blobServices/default/containers/bol`

**Q34.** Which Python v2 decorator starts a function on messages from a Service Bus topic subscription?
A) `@app.service_bus_queue_trigger(arg_name="msg", queue_name="jobs", connection="SB_CONN")`
B) `@app.service_bus_topic_trigger(arg_name="msg", topic_name="events", subscription_name="high", connection="SB_CONN")`
C) `@app.event_grid_trigger(arg_name="event")`
D) `@app.queue_trigger(arg_name="msg", queue_name="jobs", connection="AzureWebJobsStorage")`

**Q35.** (Code fill-in) Write the Python v2 decorator that runs a timer function every 5 minutes (UTC, NCRONTAB with six fields), does not run when the host starts, and binds the timer object to the parameter `tick`.

**Q36.** A Service Bus-triggered function scales on queue length, but its connection lacks the rights the scaler needs. What does the trigger do?
A) It fails at startup with a permissions error
B) It silently falls back to peek-based message estimation, which can scale late or wrong
C) It dead-letters every message after the first poll
D) It stops receiving until the role is added

**Q37.** (Select TWO) Which TWO statements about `local.settings.json` are correct?
A) Core Tools reads its `Values` section when you run the app locally
B) Its values are not published to Azure with the app, so they must be added as app settings
C) Its values override app settings in Azure
D) It must be committed to source control so that CI can run the app
E) Setting `AzureWebJobsStorage` to `UseDevelopmentStorage=true` is safe to publish

**Q38.** A timer-triggered function throws an exception on one run. What happens next?
A) The runtime retries that run up to five times
B) It is not retried; it runs again at its next scheduled time
C) The run's message moves to a dead-letter queue
D) It runs immediately on another instance

**Q39.** A subscription has two advanced filters: `StringContains` on `Subject` for `devtestlab`, and `StringContains` on `Subject` for `Microsoft.Compute`. Which events pass?
A) Events whose subject contains either text
B) Events whose subject contains both texts
C) Events whose subject contains neither text
D) Every event, because the filters are ignored

**Q40.** An HTTP-triggered function uses `auth_level=FUNCTION`. What must a caller send to pass?
A) A Microsoft Entra bearer token only
B) A function key, for example in the `code` query string or the `x-functions-key` header
C) Nothing; the endpoint is public
D) The storage account key

**Q41.** A monitoring tool must list which secrets exist and when they expire, but must never read a secret value. Which built-in role fits?
A) Key Vault Secrets User
B) Key Vault Reader
C) Key Vault Administrator
D) Key Vault Secrets Officer

**Q42.** Which setting makes a deleted secret or vault impossible to purge before its retention period ends?
A) Soft-delete, which is on by default
B) Purge protection
C) Recovering the vault after deletion
D) A managed identity on the vault

**Q43.** (Select TWO) Which TWO credential types are part of the default chain used by `DefaultAzureCredential`?
A) `ManagedIdentityCredential`
B) `AzureCliCredential`
C) `UsernamePasswordCredential`
D) `DeviceCodeCredential`
E) A SAS token passed in the query string

**Q44.** (Ordering) Arrange the steps so that an App Configuration key resolves to a Key Vault secret at runtime.
A) The app reads the App Configuration key, then resolves the secret reference against Key Vault
B) Create the secret in Key Vault
C) Grant the app's identity the Key Vault Secrets User role on the secret or the vault
D) Create the App Configuration key as a Key Vault reference (content type `application/vnd.microsoft.appconfig.keyvaultref+json`)

**Q45.** Which built-in feature filter turns a feature on for a named list of users and groups?
A) Time window
B) Targeting
C) Canary label
D) Environment variable

**Q46.** A service must keep about 10 percent of traces, but it must still honor the parent's sampling decision in distributed traces. Which sampler fits?
A) `AlwaysOn`
B) `ParentBased(TraceIdRatioBased(0.1))`
C) `TraceIdRatioBased(0.1)` alone
D) `AlwaysOff`

**Q47.** Once soft-delete is enabled on a Key Vault, what can you do?
A) Disable it from the portal at any time
B) Nothing: soft-delete cannot be disabled once enabled
C) Disable it only by opening a support ticket
D) Disable it with `az keyvault update --enable-soft-delete false`

**Q48.** (Code fill-in) Write the KQL that returns the five slowest requests from the last two hours, showing `name` and `duration`, slowest first.

**Q49.** (Dropdown) To plot failed requests in 15-minute buckets as a time series, the query ends with `| summarize failures = count() by bin(timestamp, ____)` followed by `| render ____`.
- Blank 1 options: `15m` / `15` / `1d`
- Blank 2 options: `timechart` / `piechart` / `barchart`

**Q50.** A deploy changes 40 keys in App Configuration. The workers should reload once, not 40 times. Which pattern fits?
A) Watch all 40 keys and reload on each change
B) Update one sentinel key after the batch, and have the workers watch only that key
C) Restart the app once per key change
D) Move all 40 keys into Key Vault

---

## Section 3 — Yes/No, no-return (Q51–Q54)

**Q51.** By default, the Service Bus trigger completes a message after the function succeeds, and abandons it when the function throws. Yes / No

**Q52.** An HNSW index can be built directly on a `vector(3072)` column in pgvector 0.8.x. Yes / No

**Q53.** Every instance of a scaled-out timer-triggered function runs the schedule, so each instance fires once per interval. Yes / No

**Q54.** A W3C `traceparent` value carries the trace ID, the parent span ID, and trace flags. Yes / No

---

## Answer key

| Q | Ans | Domain | Why |
|---|---|---|---|
| 1 | B | ops | No version means the app reads the latest version; a pinned version never moves; the vault root is not a secret URI |
| 2 | A, C | ops | Service Bus carries only properties; the app injects traceparent on send and extracts it on receive (checked in-process with OpenTelemetry) |
| 3 | 0 / 10 | containers | Per-revision defaults are minimum 0 and maximum 10 |
| 4 | B -> C -> A -> D | containers | Build in ACR Tasks, update the app (an image change creates a revision), verify the revision, then lock the tag |
| 5 | B | data | quantizedFlat and diskANN need at least 1,000 indexed vectors; below that the query is a full scan |
| 6 | C | containers | Timer triggers run on a schedule; the other three respond to events |
| 7 | A, B | containers | Managed identity with read access, plus the SecretUri syntax; the version is optional |
| 8 | C | containers | Image and container settings are revision-scope; traffic, ingress, and secret values are application-scope |
| 9 | 1-A, 2-B, 3-C, 4-D (E unused) | containers | HTTP, TCP, and custom rules cover the needs; a fixed count is not a scale rule |
| 10 | B | containers | Describe prints the Events section, where the scheduler gives its reason; logs need a running container |
| 11 | B -> C -> A -> D | containers | Detect the stuck rollout, inspect history, undo, then confirm |
| 12 | A | containers | Internal ingress is reachable only inside the environment; external with a restriction is still external |
| 13 | A | containers | Each environment usually has its own vault, so the values must not swap |
| 14 | B | containers | az acr import copies images from another registry without a pull, tag, or push |
| 15 | See fill-in key | containers | Fill-in answers are listed below the scorecard |
| 16 | A | containers | nodeSelector places Pods by node label; the other fields do different jobs |
| 17 | B | data | A point read is the cheapest way to fetch one known item |
| 18 | A, B | data | Omitting the partition key fans out across partitions; filtering on it routes to one partition |
| 19 | See fill-in key | data | TOP N is required; ORDER BY VectorDistance drives the vector search |
| 20 | B | data | D is invalid: AllVersionsAndDeletes cannot start from the beginning |
| 21 | B | data | m sets connections per layer (default 16); ef_search is a query-time setting |
| 22 | B | data | ef_search is the query-time candidate list (default 40); the others are build-time or IVFFlat settings |
| 23 | B | data | vector indexes stop at 2,000 dimensions; halfvec indexes go up to 4,000 (pgvector README) |
| 24 | B | data | 6432 is the built-in PgBouncer port; 8432 serves worker nodes in elastic clusters |
| 25 | B | data | GETEX returns the value and sets the expiry in one step (Redis command; not re-fetched) |
| 26 | B | data | Dropping an indexed path forces a full scan for queries that use it |
| 27 | B | data | TTL requires indexing, so the none mode is rejected while TTL is on |
| 28 | B | data | TAG fields support exact-match filters; undeclared fields are not indexed |
| 29 | B -> C -> D -> A | data | Allow-list the extension, create it, create the table, load the rows, then index |
| 30 | A, B | integration | One lock per session, FIFO within it; Standard and Premium support sessions, Basic does not |
| 31 | B | integration | schedule_messages enqueues for a future time; TTL controls expiry, not start time |
| 32 | A | integration | NumberGreaterThan compares numbers; the others test equality, text, or the wrong direction |
| 33 | B | integration | Blob subjects follow /blobServices/default/containers/<name>/; the trailing slash stops prefix matches |
| 34 | B | integration | The topic trigger takes a topic name and a subscription name |
| 35 | See fill-in key | integration | Six NCRONTAB fields with seconds first; run_on_startup stays false |
| 36 | B | integration | Missing rights cause a silent fallback to peek-based estimation |
| 37 | A, B | integration | local.settings.json drives local runs only; publish carries app settings, and development storage must not be published |
| 38 | B | integration | Timer triggers do not retry; the next run follows the schedule |
| 39 | B | integration | Separate filters combine with AND; values inside one filter combine with OR |
| 40 | B | integration | FUNCTION auth level needs a function key, sent as code or x-functions-key (Learn, HTTP trigger article) |
| 41 | B | ops | Reader sees metadata only; Secrets User reads values |
| 42 | B | ops | Purge protection blocks purging until retention ends; soft-delete only allows recovery |
| 43 | A, B | ops | Managed identity and Azure CLI are in the chain; username/password and device code are not |
| 44 | B -> C -> D -> A | ops | Secret first, then the grant, then the reference, then the read; the store holds only the pointer |
| 45 | B | ops | Targeting filters name users and groups; the time window uses a date range |
| 46 | B | ops | ParentBased honors the parent's decision; the ratio applies to new root traces |
| 47 | B | ops | Soft-delete is on by default and cannot be disabled once enabled |
| 48 | See fill-in key | ops | top sorts and limits in one step; ago anchors the window |
| 49 | 15m / timechart | ops | bin takes a timespan literal; render timechart draws a time series |
| 50 | B | ops | One sentinel change signals the batch; watching one key avoids 40 triggers |
| 51 | Yes | integration | Trigger default: complete on success, abandon on exception |
| 52 | No | data | HNSW on the vector type is limited to 2,000 dimensions; use halfvec for up to 4,000 |
| 53 | No | integration | The timer runs once across all instances when the app scales out |
| 54 | Yes | ops | The header is 00-trace-id-parent-id-flags |

### Fill-in key (Q15, Q19, Q35, Q48)

- **Q15:** `az containerapp logs show --name ocr-worker --resource-group rg-litware --follow` (`--type console` is the default; `--type system` shows platform logs)
- **Q19:** `SELECT TOP 5 c.id, VectorDistance(c.embedding, @q) AS score FROM c ORDER BY VectorDistance(c.embedding, @q)`
- **Q35:** `@app.timer_trigger(schedule="0 */5 * * * *", arg_name="tick", run_on_startup=False)`
- **Q48:**

```kusto
requests
| where timestamp > ago(2h)
| top 5 by duration desc
| project name, duration
```

---

## Scorecard

| Domain | Questions | Your score | Target |
|---|---|---|---|
| containers (Sec 1) | Q3, Q4, Q6–Q16 (13) | __ / 13 | ≥ 11 |
| data (Sec 2) | Q5, Q17–Q29, Q52 (15) | __ / 15 | ≥ 13 |
| integration (Sec 3) | Q30–Q40, Q51, Q53 (13) | __ / 13 | ≥ 11 |
| ops (Sec 4) | Q1, Q2, Q41–Q50, Q54 (13) | __ / 13 | ≥ 11 |
| **Total** | | __ / 54 | **≥ 46 (85%)** |

For every miss: re-read the matching study-guide bullet, then redo the matching lab step before you move on.

---

## How each key was checked (2026-11-04)

- **Learn pages:** App Service Key Vault references (Q1, Q7, Q13); Container Apps scaling, revisions, ingress, and log streaming (Q3, Q8, Q9, Q12, Q15); ACR Tasks (Q6); Cosmos DB vector search and indexing policies (Q5, Q19, Q26, Q27); Cosmos DB change feed pull model (Q20); Service Bus sessions (Q30); Event Grid event filtering and handlers (Q32, Q33, Q39); Functions HTTP trigger (Q40); Functions Service Bus and timer triggers (Q34, Q36, Q38, Q53); Functions local settings (Q37); Key Vault RBAC and soft-delete (Q41, Q42, Q47); App Configuration feature filters (Q45).
- **pgvector:** the upstream README (Q21, Q22, Q23, Q52). Confirm the Azure extension version before the sitting.
- **Installed packages and CLI:** azure-identity (Q43), azure-appconfiguration (Q44), azure-servicebus (Q31), OpenTelemetry in-process (Q2, Q46, Q54), and `az acr import`, `az containerapp logs show`, `az containerapp update` (Q4, Q14, Q15).
- **Upstream behavior, not re-fetched:** Q10, Q11, Q16 (Kubernetes); Q25 (Redis); Q48 and Q49 (KQL operators); Q50 (App Configuration sentinel pattern).

Sources: [App Service Key Vault references](https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references) · [Container Apps scaling](https://learn.microsoft.com/en-us/azure/container-apps/scale-app) · [Container Apps revisions](https://learn.microsoft.com/en-us/azure/container-apps/revisions) · [Container Apps ingress](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview) · [Container Apps log streaming](https://learn.microsoft.com/en-us/azure/container-apps/log-streaming) · [ACR Tasks](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tasks-overview) · [Cosmos DB vector search](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search) · [Cosmos DB indexing policies](https://learn.microsoft.com/en-us/azure/cosmos-db/index-policy) · [Cosmos DB change feed pull model](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/change-feed-pull-model) · [pgvector](https://github.com/pgvector/pgvector) · [PgBouncer on Flexible Server](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-pgbouncer) · [Service Bus sessions](https://learn.microsoft.com/en-us/azure/service-bus-messaging/message-sessions) · [Event Grid filtering](https://learn.microsoft.com/en-us/azure/event-grid/event-filtering) · [Event Grid handlers](https://learn.microsoft.com/en-us/azure/event-grid/event-handlers) · [Functions HTTP trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger) · [Functions Service Bus trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-trigger) · [Functions timer trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer) · [Functions local development](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local) · [Key Vault RBAC](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide) · [Key Vault soft-delete](https://learn.microsoft.com/en-us/azure/key-vault/general/soft-delete-overview) · [App Configuration feature filters](https://learn.microsoft.com/en-us/azure/azure-app-configuration/howto-feature-filters)
