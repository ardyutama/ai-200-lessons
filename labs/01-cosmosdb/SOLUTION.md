# Solution 01 — Cosmos DB for NoSQL (answer key)

> **Attempt-first rule.** First pass: you may consult this key. The two runs that count toward *Solid Practice* must be done with this file **closed**. When you're ready for a counted run, close it and work from [README.md](README.md) alone.

**Setup (do once):** `floci az start && eval $(floci az env)`, activate the repo venv. Note: `floci az env` does **not** print any Cosmos variable — derive the endpoint/key by hand (same dev key as storage).

Set these so every snippet below is self-contained:

```bash
export COSMOS_ENDPOINT="http://localhost:4577/devstoreaccount1-cosmos"
export COSMOS_KEY="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMh0=="
# connection-string form, if needed:
export AZURE_COSMOS_CONNECTIONSTRING="AccountEndpoint=$COSMOS_ENDPOINT;AccountKey=$COSMOS_KEY;"
```

> **Note on snippets.** floci-az emulates Cosmos; it does **not** meter RUs, enforce consistency, or run a real change-feed host. So some steps are *write it and say the answer out loud* — the snippet is the syntax you must be able to produce cold, and the "Why / trap" is what the exam actually probes.

---

## Step 1 — Connect & create

**Q.** Write the code to create a database `aidb` and a container `docs` partitioned on `/category`. What's the one parameter that silently creates if it already exists?

```python
import os
from azure.cosmos import CosmosClient, PartitionKey

client = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential=os.environ["COSMOS_KEY"])

db = client.create_database_if_not_exists(id="aidb")
container = db.create_container_if_not_exists(
    id="docs",
    partition_key=PartitionKey(path="/category"),
    offer_throughput=400,          # RU/s; ignored by the emulator, required on real Cosmos
)
print("created:", container.id)
```

**Why / trap.** `create_*_if_not_exists` is idempotent — use it in labs; on the exam, know it vs the raising `create_*`. **Partition key is immutable** after creation: you cannot change `/category` later, you must migrate to a new container. Choose the key for **even distribution + point-read locality**, not for query convenience.

---

## Step 2 — CRUD + query (and the RU cost difference)

**Q.** Insert docs, then show the cheapest read and the expensive alternative. Which header tells you the RU charge, and why is one read so much cheaper?

```python
import os, uuid
from azure.cosmos import CosmosClient

client = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential=os.environ["COSMOS_KEY"])
container = client.get_database_client("aidb").get_container_client("docs")

# create 5 docs
for i, cat in enumerate(["faq", "blog", "faq", "docs", "blog"]):
    container.upsert_item({
        "id": f"doc{i}", "category": cat, "title": f"Title {i}",
        "embedding": [float(i), 0.1 * i, 0.2 * i],
    })

# CHEAP: point read — id + partition key → single logical partition, lowest RU
item = container.read_item(item="doc0", partition_key="faq")
print("point-read RU:", container.client_connection.last_response_headers.get("x-ms-request-charge"))

# EXPENSIVE: parameterized cross-partition query (no partition key in WHERE → fans out)
q = list(container.query_items(
    query="SELECT * FROM c WHERE c.title = @t",
    parameters=[{"name": "@t", "value": "Title 0"}],
    enable_cross_partition_query=True,
))
print("query returned", len(q))
```

**Why / trap.** The cost header is **`x-ms-request-charge`**. A **point read** (id + partition key) costs ~1 RU and hits one partition; a **query without the partition key** fans out to every physical partition and costs many RUs. On the exam, the cheapest pattern is always *read by id + known partition key*; always pass query values as **parameters** (`@name`) to avoid injection and enable plan caching.

---

## Step 3 — Indexing policy (RU optimization)

**Q.** Everything is indexed by default. How do you stop paying RU to index a large blob path, and when does a composite index become *required* rather than optional?

```python
import os
from azure.cosmos import CosmosClient, PartitionKey

client = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential=os.environ["COSMOS_KEY"])
db = client.get_database_client("aidb")

indexing_policy = {
    "indexingMode": "consistent",
    "automatic": True,
    "includedPaths": [{"path": "/*"}],            # index everything...
    "excludedPaths": [
        {"path": "/large_blob/*"},                # ...except the big, never-filtered blob
        {"path": "/_etag/?"},
    ],
}
container = db.create_container_if_not_exists(
    id="docs_idx", partition_key=PartitionKey(path="/category"),
    indexing_policy=indexing_policy,
)
print("excluded /large_blob/*")
```

**Why / trap.** Default = **every path indexed** → you pay RU for writes on paths you never query. Excluding `/large_blob/*` cuts **write RU and storage**. The hard exam trigger: **composite indexes are required for `ORDER BY` on two or more properties** (e.g. `ORDER BY c.category, c.title`) — without one the query fails, not just slows. Single-property `ORDER BY` needs no composite index. Excluded paths are readable but only scan/filterable, so they can't serve range/equality lookups.

---

## Step 4 — Vector search

**Q.** Recreate the container for vector search: declare the vector policy *and* the index, then query by similarity. Which index do you pick for ~1M embeddings, and why?

```python
import os, numpy as np
from azure.cosmos import CosmosClient, PartitionKey

client = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential=os.environ["COSMOS_KEY"])
db = client.get_database_client("aidb")

try:
    db.delete_container("docs_vec")
except Exception:
    pass

container = db.create_container(
    id="docs_vec",
    partition_key=PartitionKey(path="/category"),
    vector_embedding_policy={                      # declares the vector field
        "vectorEmbeddings": [{
            "path": "/embedding", "dataType": "float32",
            "dimensions": 3, "distanceFunction": "cosine",
        }]
    },
    indexing_policy={
        "includedPaths": [{"path": "/*"}],
        "excludedPaths": [{"path": "/embedding/*"}],  # don't double-index the vector
        "vectorIndexes": [{"path": "/embedding", "type": "flat"}],
    },
)

container.upsert_item({"id": "a", "category": "x", "embedding": [1.0, 0.0, 0.0]})
container.upsert_item({"id": "b", "category": "x", "embedding": [0.0, 1.0, 0.0]})

qv = [0.9, 0.1, 0.0]
for row in container.query_items(
    query="SELECT c.id FROM c ORDER BY RANK VectorDistance(c.embedding, @qv)",
    parameters=[{"name": "@qv", "value": qv}],
    enable_cross_partition_query=True,
):
    print("nearest:", row["id"])
```

**Why / trap.** Both halves are required — a `vector_embedding_policy` entry **and** a matching `vectorIndexes` entry, and the path must be **excluded** from regular indexing. **Index choice:** `flat` = exact/brute-force (small data, highest recall, no recall tuning); `quantizedFlat` = flat with quantization (medium, faster, cheaper); **`diskANN` = the answer for ~1M+ vectors** (approximate, memory-efficient, scales to large catalogs). `VectorDistance` must sit inside **`RANK ... ORDER BY`**, and the `dimensions` in the policy must match the data.

---

## Step 5 — Consistency levels

**Q.** Name all five consistency levels in order. Why is Session the default, and what does Strong cost you?

**Answer (recite, in order from strongest to weakest):**

**Strong → Bounded Staleness → Session → Consistent Prefix → Eventual**

**Why / trap.** **Session is the default** because it gives a single client/session read-your-own-writes at low RU — strong enough for a user editing their own data, cheap enough to be the default. **Strong** guarantees linearizability but costs **~2× the RU** on reads and the highest latency, and is unavailable with multi-region writes. Mnemonic for the order: **S**trong, **B**ounded, **S**ession, **C**onsistent, **E**ventual — "Some Big Systems Crash Eventually." Exam traps: Strong is *not* free; Eventual is cheapest/fastest; Bounded Staleness bounds lag by *time or versions (K/T)*.

---

## Step 6 — Change feed

**Q.** Read the change feed, insert a doc, confirm it appears. Then name the four components of the *hosted* change-feed processor and the lease container's job.

```python
import os, time
from azure.cosmos import CosmosClient

client = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential=os.environ["COSMOS_KEY"])
container = client.get_database_client("aidb").get_container_client("docs")

# start from now, loop for changes
for change in container.query_items_change_feed(is_start_from_beginning=False):
    print("change:", [d["id"] for d in change])
    break

container.upsert_item({"id": "new-1", "category": "faq", "title": "New"})
time.sleep(0.5)
for change in container.query_items_change_feed(is_start_from_beginning=False):
    for d in change:
        if d["id"] == "new-1":
            print("saw new-1 via change feed")
    break
```

**Why / trap.** The change feed is the **insert/update log** (no deletes; **soft-delete needs a TTL + `isDeleted` flag**, "capture intermediate changes" mode). Whiteboard the four hosted-processor components: **(1) monitored container** (the data), **(2) lease container** (tracks per-partition progress/checkpoints so the processor can resume and load-balance across instances), **(3) delegate** (your code that handles a batch of changes), **(4) processor instance/host** (named via `processor_name`). The **lease container** is what makes scaling-out and crash-recovery safe — that's the line the exam wants.

---

## Self-check (map to "Done when")

- Can you do steps 1–4 from memory, twice? → that's two **key-closed** runs.
- Can you whiteboard: monitored container, lease container, delegate, processor name?
- "Which vector index for 1M embeddings and why?" → **diskANN** (approximate, memory-efficient, scales; `flat`/`quantizedFlat` don't).

**Cleanup:** `floci az stop` (state is disposable).
