# Solution 02 — Azure Database for PostgreSQL + pgvector (answer key)

> **Attempt-first rule.** First pass: you may consult this key. The two runs that count toward *Solid Practice* must be done with this file **closed**. When you're ready for a counted run, close it and work from [README.md](README.md) alone.

**The Case Thread.** You are building **SupportBrain**, the support-docs copilot for a multi-tenant SaaS. Customers `contoso` and `fabrikam` store help articles tagged `faq`, `blog`, or `docs`. A user asks *"how do I reset my password"* → your job: embed the question, retrieve **that tenant's** nearest articles, hand them to the LLM. Every block below is the next thing you do on that job.

**Setup (do once):**

```bash
docker start pgvec 2>/dev/null || docker run -d --name pgvec -e POSTGRES_PASSWORD=postgres -p 5432:5432 pgvector/pgvector:pg16
source ../../.venv/bin/activate          # from this folder
# block 14 needs the pool extra: pip install -r ../../requirements.txt   (now psycopg[binary,pool])
```

Blocks paste into `postgres-pgvector.py` top to bottom; each is also runnable standalone. Blocks 5–15 reuse `DSN`, `embed()`, `qv`, and `EXPLAIN_SQL` where defined.

> **Note on the emulator split.** floci-az emulates the Flexible Server *control plane* (`az postgres ...`); the vector work below runs against the **real** local Postgres in `pgvec`. Anything marked **Azure-side** is say-it-out-loud exam knowledge, same convention as Solution 01.

---

## Block 1 — Connect

**Q.** Hour one on the job: connect to Postgres and prove it. What must change in this exact string before the same code runs against Azure Database for PostgreSQL Flexible Server — and why?

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

with psycopg.connect(DSN) as conn:
    print("connected:", conn.execute("SELECT version()").fetchone()[0][:38])
```

**Why / trap.** Locally `sslmode=disable` is fine. Flexible Server enforces TLS by default (`require_secure_transport` = ON), so the Azure connection string must carry **`sslmode=require`** (use `verify-full` to also validate the server cert). Exam trigger: "connection rejected / must be encrypted" → missing `sslmode=require`.

---

## Block 2 — Enable the extension

**Q.** Articles need vector search. Enable it — and name the Azure control-plane step that must happen **before** `CREATE EXTENSION` will succeed on Flexible Server.

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

with psycopg.connect(DSN) as conn:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print(conn.execute(
        "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'"
    ).fetchone())
```

**Why / trap.** **Azure-side:** Flexible Server gates extensions — first allow-list `vector` via the server parameter **`azure.extensions`** (portal → Server parameters, or `az postgres flexible-server parameter set --name azure.extensions --value vector`), **then** `CREATE EXTENSION vector;`. Skip the allow-list → permission error. That two-step order is the exam answer.

---

## Block 3 — Schema

**Q.** Design the `docs` table for SupportBrain: multi-tenant, categorized articles with an embedding column. What does `vector(8)` pin down, and what happens when a row arrives with 7 numbers?

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

with psycopg.connect(DSN) as conn:
    conn.execute("DROP TABLE IF EXISTS docs;")   # repeatable lab runs
    conn.execute("""
        CREATE TABLE docs (
            id        bigserial PRIMARY KEY,
            tenant    text NOT NULL,
            category  text NOT NULL,
            content   text NOT NULL,
            embedding vector(8)
        );
    """)
    print("docs table ready")
```

**Why / trap.** `vector(8)` **pins the dimension at the type level** — a 7- or 9-number value fails at INSERT. Real case: `text-embedding-3-small` → 1536 dims → `vector(1536)`; pgvector indexes cap at **2,000 dims** for `vector` (above that: `halfvec`). `tenant` and `category` stay ordinary columns on purpose — that's what makes blocks 12–13 plain SQL instead of application code.

---

## Block 4 — Embeddings that mean something

**Q.** No Azure OpenAI budget in this lab. Write a ~10-line deterministic embedder so texts that share words land near each other — then a password question *actually retrieves* password articles. What does the real SupportBrain call instead?

```python
import hashlib
import numpy as np

DIM = 8

def embed(text: str) -> str:
    """Deterministic bag-of-words embedder: shared words -> nearby vectors.
    Teaching stand-in for a real embedding model; returns pgvector text form."""
    vec = np.zeros(DIM)
    for token in text.lower().split():
        vec[int(hashlib.md5(token.encode()).hexdigest(), 16) % DIM] += 1.0
    norm = np.linalg.norm(vec)
    if norm:
        vec /= norm
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
```

**Why / trap.** Hash each word into one of 8 buckets, normalize → same words ⇒ cosine-close. It is **not semantic**: "reset password" and "forgot login" share no words, so they won't be close. Real SupportBrain: **Azure OpenAI `text-embedding-3-small/large`**, record the model+version next to the data, and never mix vectors from different models in one column. Returning the `[...]` string saves a client library — Postgres casts the text to `vector` on insert/query.

---

## Block 5 — Load the catalog

**Q.** Seed ~200 articles across both tenants and three categories, written so similar articles share words. Send the batch in one go.

```python
import psycopg

TOPICS = {
    "faq": [
        "how do i reset my password",
        "how do i change my billing plan",
        "how do i export my data",
        "how do i enable two factor authentication",
        "how do i delete my account",
        "how do i contact support",
    ],
    "blog": [
        "announcing dark mode in the product",
        "new dashboard released this quarter",
        "our roadmap for next year",
        "performance improvements shipped",
        "meet the team behind the product",
        "we raised funding to grow",
    ],
    "docs": [
        "api authentication uses bearer tokens",
        "webhook payloads are signed with hmac",
        "rate limits apply per api key",
        "pagination uses cursor parameters",
        "sdk retry policy and backoff",
        "error codes and troubleshooting",
    ],
}
TENANTS = ["contoso", "fabrikam"]

flat = [(c, s) for c, sents in TOPICS.items() for s in sents]
rows = []
for i in range(200):
    cat, sent = flat[i % len(flat)]
    content = f"{sent} walkthrough {i // len(flat)}"
    rows.append((TENANTS[i % 2], cat, content, embed(content)))

with psycopg.connect(DSN) as conn:
    conn.cursor().executemany(
        "INSERT INTO docs (tenant, category, content, embedding) VALUES (%s, %s, %s, %s::vector)",
        rows,
    )
    print("rows:", conn.execute("SELECT count(*) FROM docs").fetchone()[0])
    print(conn.execute(
        "SELECT tenant, category, count(*) FROM docs GROUP BY 1, 2 ORDER BY 1, 2"
    ).fetchall())
```

**Why / trap.** `executemany` batches efficiently; for a **real** initial catalog load the answer is **`COPY`** — orders of magnitude faster, and the exam's bulk-ingest keyword. Each row's embedding comes from its own content, so word overlap within a topic makes neighbors meaningful — that's what lets block 7 feel real. Tenants alternate, so each tenant ends up with ~100 articles across all 3 categories; block 13 exploits exactly that.

---

## Block 6 — The three distance operators

**Q.** A contoso user asks *"how do i reset my password"*. Show the nearest articles with **each** operator. Which one is cosine — and is bigger better or worse?

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"
qv = embed("how do i reset my password")

with psycopg.connect(DSN) as conn:
    for op, name in [("<->", "L2 / Euclidean"), ("<#>", "negative inner product"), ("<=>", "cosine distance")]:
        rows = conn.execute(
            f"SELECT content, embedding {op} %s::vector AS d FROM docs ORDER BY d LIMIT 3",
            (qv,),
        ).fetchall()
        print(f"{op} {name:24s}", [r[0][:38] for r in rows])
```

**Why / trap.** **`<=>` is cosine DISTANCE = 1 − cosine similarity** — *smaller* is closer; always `ORDER BY embedding <=> q LIMIT k` ascending. `<->` is L2/Euclidean; `<#>` is *negative* inner product (negated precisely so ascending order = max similarity). Exam anchors: cosine for normalized text embeddings — and the operator you query with **must match the index operator class** (block 9 cashes that in). The f-string here interpolates an operator from a fixed list — never f-string *user* input into SQL.

---

## Block 7 — The RAG moment

**Q.** Put it together: question in → embedding → the top-5 rows you'd paste into the LLM prompt. Run it for the password question and eyeball the result — does it deserve to be called retrieval?

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

def retrieve(question: str, k: int = 5):
    with psycopg.connect(DSN) as conn:
        return conn.execute(
            """
            SELECT tenant, category, content,
                   round((embedding <=> %s::vector)::numeric, 4) AS distance
            FROM docs
            ORDER BY distance
            LIMIT %s
            """,
            (embed(question), k),
        ).fetchall()

for row in retrieve("how do i reset my password"):
    print(row)
```

**Why / trap.** This function **is RAG minus the generation step**: embed query → vector search → stuff results into the prompt. Because the embedder is deterministic you can *verify* retrieval quality locally — the top hits should all be password-reset articles. Notice both tenants appear: that's the leak block 13 fixes. On the exam the same shape shows up as AOAI embeddings + `embedding <=> @q` + prompt stuffing.

---

## Block 8 — EXPLAIN baseline

**Q.** Before optimizing anything, capture the plan for the retrieve query. What do you expect with no index, and how do you prove it?

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"
qv = embed("how do i reset my password")
EXPLAIN_SQL = """
EXPLAIN (COSTS OFF)
SELECT id FROM docs ORDER BY embedding <=> %s::vector LIMIT 5
"""

with psycopg.connect(DSN) as conn:
    for line in conn.execute(EXPLAIN_SQL, (qv,)).fetchall():
        print(line[0])
```

Expected: `Sort` over **`Seq Scan` on docs**.

**Why / trap.** No index → **Seq Scan**: read every row, compute every distance, sort, keep 5 — O(N) distance computations per query. `EXPLAIN` only estimates; `EXPLAIN (ANALYZE, BUFFERS)` actually runs the query (real timings, buffer hits) — that's the case-review habit. `(COSTS OFF)` keeps output readable for your notes.

---

## Block 9 — HNSW

**Q.** Build an HNSW index that serves the cosine query, then re-run EXPLAIN. Two traps: which operator class must you name, and why might the plan **still** show Seq Scan on this 200-row lab table?

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"
qv = embed("how do i reset my password")
EXPLAIN_SQL = "EXPLAIN (COSTS OFF) SELECT id FROM docs ORDER BY embedding <=> %s::vector LIMIT 5"

with psycopg.connect(DSN, autocommit=True) as conn:
    conn.execute("CREATE INDEX docs_hnsw ON docs USING hnsw (embedding vector_cosine_ops);")
    conn.execute("SET enable_seqscan = off;")   # reveal the index plan on a tiny table
    for line in conn.execute(EXPLAIN_SQL, (qv,)).fetchall():
        print(line[0])
```

**Why / trap.** (1) **Operator class must match the query operator**: `vector_cosine_ops` serves `<=>`, `vector_l2_ops` serves `<->`, `vector_ip_ops` serves `<#>`. Mismatch → planner silently ignores the index. (2) On 200 rows a Seq Scan is genuinely cheaper, so the planner skips the index — `SET enable_seqscan = off` forces the plan into view; on the real 100k-row catalog the planner chooses it by itself. HNSW is a graph index: best recall/speed tradeoff, **slower build, more memory** — the comparison table lives in block 15.

---

## Block 10 — IVFFlat and the empty-table trap

**Q.** SupportBrain's deploy pipeline wants to create **all** indexes at schema-migration time, *before* any data exists. Prove why that's a bug for IVFFlat.

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"
qv = embed("how do i reset my password")

with psycopg.connect(DSN, autocommit=True) as conn:
    conn.execute("DROP INDEX IF EXISTS docs_hnsw;")     # README: drop HNSW first
    conn.execute("DROP TABLE IF EXISTS docs2;")
    conn.execute("CREATE TABLE docs2 (LIKE docs);")     # empty clone
    # trap: index built BEFORE data exists — watch the server log warning
    conn.execute("CREATE INDEX docs2_ivf ON docs2 USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);")
    conn.execute("INSERT INTO docs2 SELECT * FROM docs;")
    conn.execute("SET enable_seqscan = off; SET ivfflat.probes = 1;")
    approx = [r[0] for r in conn.execute(
        "SELECT id FROM docs2 ORDER BY embedding <=> %s::vector LIMIT 5", (qv,))]
    exact = [r[0] for r in conn.execute(
        "SELECT id FROM docs  ORDER BY embedding <=> %s::vector LIMIT 5", (qv,))]
    print("exact :", exact)
    print("approx:", approx)
    conn.execute("REINDEX INDEX docs2_ivf;")            # the fix
```

Verified output on this corpus — same 5 ids, **wrong order** from the empty-built index; `REINDEX` (with data present) restores sane results (still approximate — that's the point of ANN):

```
exact : [145, 91, 109, 73, 37]
approx: [109, 37, 145, 73, 91]
after REINDEX: [145, 109, 73, 37, 91]
```

**Why / trap.** IVFFlat partitions vectors into `lists` clusters via **k-means computed at build time**. Built on an empty (or unrepresentative) table there are no real centroids; later inserts pile into whatever lists exist, and with `probes = 1` the search visits only one list → **recall collapses** (pgvector logs *"ivfflat index created with little data"*). Rules: **load first, then build**, or `REINDEX` after a bulk load. HNSW has no such trap — it updates incrementally. That contrast is core exam material.

---

## Block 11 — Recall knobs

**Q.** A fabrikam admin reports retrieval misses obvious articles. Name the two runtime knobs (one per index type), the direction each trades, and *where* they get set.

```sql
SET ivfflat.probes  = 10;    -- default 1:  visit more lists          -> better recall, more compute
SET hnsw.ef_search  = 100;   -- default 40: bigger candidate queue    -> better recall, more latency
```

Build-time partners (fixed at `CREATE INDEX`):

```sql
CREATE INDEX ... USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);   -- rule of thumb: rows/1000, up to ~1M rows
CREATE INDEX ... USING hnsw  (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

**Why / trap.** `probes` / `ef_search` are **session GUCs — set per query or transaction, not stored in the index**; `lists` / `m` / `ef_construction` are frozen at build. Recall up ⇄ latency/compute up — the exam phrase is *"tune for recall vs compute overhead"*. Hold onto "session GUC": it detonates in block 14.

---

## Block 12 — RAG with a metadata filter

**Q.** Retrieval must stay on-topic: only `faq` articles may answer how-to questions. Write the filtered query, then argue why it beats fetching top-50 and dropping non-faq rows in Python.

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

def retrieve_faq(question: str, k: int = 5):
    with psycopg.connect(DSN) as conn:
        return conn.execute(
            """
            SELECT category, content,
                   round((embedding <=> %s::vector)::numeric, 4) AS distance
            FROM docs
            WHERE category = 'faq'
            ORDER BY distance
            LIMIT %s
            """,
            (embed(question), k),
        ).fetchall()

for row in retrieve_faq("how do i reset my password"):
    print(row)
```

**Why / trap.** **Filter in SQL**: the engine returns the true top-k *within the subset* — one round trip, correct pagination, no wasted bandwidth. Retrieve-then-filter can return **fewer than k usable rows** (even zero) and silently degrades answer quality. Case-review nuance, say it out loud: with an ANN index, a hard filter can starve the graph walk — pgvector ≥ 0.8 adds iterative index scans (`SET hnsw.iterative_scan = relaxed_order`) for exactly this.

---

## Block 13 — Tenant isolation

**Q.** The incident that ends startups: a contoso user gets a fabrikam article in their answer. Write the query that makes that impossible, and run the password question for both tenants to prove disjoint results.

```python
import psycopg

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

def retrieve_tenant(question: str, tenant: str, k: int = 5):
    with psycopg.connect(DSN) as conn:
        return conn.execute(
            """
            SELECT tenant, category, content,
                   round((embedding <=> %s::vector)::numeric, 4) AS distance
            FROM docs
            WHERE tenant = %s AND category = 'faq'
            ORDER BY distance
            LIMIT %s
            """,
            (embed(question), tenant, k),
        ).fetchall()

print("contoso :", [r[0] for r in retrieve_tenant("how do i reset my password", "contoso")])
print("fabrikam:", [r[0] for r in retrieve_tenant("how do i reset my password", "fabrikam")])
```

**Why / trap.** The `tenant` predicate **is** the isolation boundary — *every* retrieval query carries it, always as a parameter, never an f-string. Same idea as lab 01's partition key: locality + isolation in one decision. At scale add a B-tree on `tenant` (or partition the table per tenant); the strict version adds **Row-Level Security** so even a buggy query can't leak. Say the RLS line out loud — it's a classic exam upgrade.

---

## Block 14 — Connection pooling

**Q.** Traffic spike: 200 concurrent support chats, each opening a fresh Postgres connection → the server drowns in connection setup. Fix the client side, then name the Azure-side answer — and the trap our recall knobs from block 11 just created.

```python
import psycopg
from psycopg_pool import ConnectionPool

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

pool = ConnectionPool(DSN, min_size=1, max_size=5)

def retrieve_pooled(question: str, tenant: str, k: int = 5):
    with pool.connection() as conn:
        conn.execute("SET LOCAL hnsw.ef_search = 100")   # scoped to THIS transaction
        return conn.execute(
            """
            SELECT content, round((embedding <=> %s::vector)::numeric, 4) AS distance
            FROM docs
            WHERE tenant = %s AND category = 'faq'
            ORDER BY distance
            LIMIT %s
            """,
            (embed(question), tenant, k),
        ).fetchall()

print(retrieve_pooled("how do i reset my password", "contoso")[:2])
pool.close()
```

**Why / trap.** Client side: reuse connections via `psycopg_pool` (needs the `psycopg[pool]` extra — already in [requirements.txt](../../requirements.txt); re-run `pip install -r requirements.txt` once). **Azure-side answer: PgBouncer built into Flexible Server, port 6432** — the exam answer to connection storms. The trap you just set for yourself: PgBouncer in **transaction pooling** means session state does not survive checkout — a bare `SET hnsw.ef_search` leaks or vanishes between checkouts, so use `SET LOCAL` inside the transaction (or the pool's `configure` hook). *Session GUCs + transaction pooling = silent recall regression* — same story for prepared statements.

---

## Block 15 — Done-when recap (whiteboard, no notes)

**Q.** HNSW vs IVFFlat on four axes, and the three memory settings that matter for vector work.

| Axis | HNSW | IVFFlat |
|---|---|---|
| Structure | proximity graph | k-means lists (centroids) |
| Build | slower, more memory | faster, leaner |
| Recall/speed tradeoff | best; default choice | good; needs tuning |
| Inserts after build | fine (incremental) | **degrades — the empty-table trap** |
| Build knobs | `m`, `ef_construction` | `lists` (rows/1000) |
| Runtime knob | `hnsw.ef_search` (default 40) | `ivfflat.probes` (default 1) |

Memory settings: **`shared_buffers`** (page cache — keep the index hot), **`work_mem`** (per-operation sort/hash memory), **`maintenance_work_mem`** (index builds — bigger = faster HNSW builds).

---

## Self-check (map to "Done when")

- Write blocks 6–13 SQL from memory, twice, key closed → your two **Solid Practice** runs.
- "Index for ~1M embeddings, high recall?" → **HNSW** (accept the build cost). "Fast build on a loaded table, tight memory?" → **IVFFlat, built after the load**.
- "Connection storm on Flexible Server?" → **PgBouncer :6432 + a client pool**.
- "`CREATE EXTENSION vector` fails in Azure?" → allow-list **`azure.extensions`** first.
- "Which memory settings?" → `shared_buffers`, `work_mem`, `maintenance_work_mem`.

**Cleanup:** `docker rm -f pgvec` (state is disposable).
