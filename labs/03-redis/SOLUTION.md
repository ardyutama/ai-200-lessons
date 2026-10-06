# Solution 03 — Azure Managed Redis (answer key)

> **Attempt-first rule.** First pass: you may consult this key. The two runs that count toward *Solid Practice* must be done with this file **closed**. When you're ready for a counted run, close it and work from [README.md](README.md) alone.

**The Case Thread.** SupportBrain (from [Lab 02](../02-postgres-pgvector/SOLUTION.md)) is getting traffic. Postgres serves retrieval well, but two things are hot: **tenant/user metadata lookups** (per chat request) and **the LLM bill** — users keep asking the same password question in slightly different words. You add a Redis tier: a classic cache in front of the metadata, and a *semantic* cache in front of the LLM. Every block below is the next thing you do on that job.

**Setup (do once):**

```bash
docker start redis-stack 2>/dev/null || docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
source ../../.venv/bin/activate          # from this folder
```

Blocks paste into `redis-cache.py` top to bottom; each is also runnable standalone. Blocks 5–12 reuse `embed()` / `embed_bytes()` where defined.

> **Note on the runtime split.** The README sends you to floci-az first — but this floci build exposes **no Redis** (no `redis-cli`, no listening port, `floci az services` empty). So *all* snippets below target the README's own fallback, `redis-stack` in Docker — the same "real engine in Docker" split as Solution 02's `pgvec`. Anything marked **Azure-side** is say-it-out-loud exam knowledge, same convention as Solution 01. Verified live against Redis **7.4.7** / RediSearch **2.10.20** (`redis/redis-stack:latest`, 2026-10-06).

---

## Block 1 — Connect

**Q.** First line of the job: connect redis-py and prove it. What must change in the client options before this same code connects to Azure Managed Redis — and what number is the giveaway?

```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=False, protocol=2)
print(r.ping())
```

**Why / trap.** Local redis-stack is plaintext on 6379. **Azure-side:** Azure Managed Redis is **TLS-only by default on the Enterprise-style port 10000** — the client needs `redis.Redis(host=..., port=10000, password=<access-key>, ssl=True)`. Seeing **10000** in an exam question *is* the TLS signal; a plaintext client ("can't connect" / hangs) is the classic trap. `decode_responses=False` is deliberate here: later blocks store raw float32 bytes, and bytes round-trip cleanly.

**Version trap (verified live):** redis-py 8.x negotiates **RESP3** by default, and under RESP3 `FT.SEARCH` returns a **dict** (`total_results` / `results` / `extra_attributes`) instead of the flat `[count, key, [fields], ...]` list every exam example and every block below parses. `protocol=2` pins the flat shape — drop it and blocks 10–11 die with `KeyError: 0`. *RESP3 changed the RediSearch response shape* is exactly the kind of version footgun the exam borrows.

---

## Block 2 — Cache-aside: the read path

**Q.** SupportBrain loads `user:42` (plan, quota, home region) on every chat request. Write `get_user(id)`: cache → miss → "DB" (a dict) → populate with a 60-second TTL.

```python
import json
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True, protocol=2)

DB = {
    "42": {"name": "Ada (contoso)", "plan": "enterprise"},
    "7":  {"name": "Grace (fabrikam)", "plan": "standard"},
}

def get_user(user_id: str) -> dict:
    key = f"user:{user_id}"
    cached = r.get(key)
    if cached is not None:                       # HIT — DB never touched
        print("hit  ", key)
        return json.loads(cached)
    print("miss ", key)
    user = DB[user_id]                           # fall through to the "DB"
    r.set(key, json.dumps(user), ex=60)          # populate with TTL
    return user

print(get_user("42"))   # miss
print(get_user("42"))   # hit
```

**Why / trap.** This *is* the **cache-aside (lazy loading)** pattern the exam names: the application — not the cache — owns the miss logic, and the populate write always carries a **TTL** (`ex=60`) so stale entries self-destruct. Real exam pattern, in one breath: *try cache → miss → DB → SET with TTL*. The lazy/populate half alone is worthless without the write-path half — that's block 3.

---

## Block 3 — Cache-aside: the write path

**Q.** Ada upgrades her plan. Write `update_user(id, changes)` — and defend the choice: why **delete** the cache key instead of updating it in place?

```python
def update_user(user_id: str, changes: dict) -> None:
    DB[user_id].update(changes)        # 1. DB first — the source of truth
    r.delete(f"user:{user_id}")        # 2. THEN invalidate the cache key

update_user("42", {"plan": "ultimate"})
print(get_user("42"))                  # miss -> repopulates fresh
```

(Standalone run: paste block 2 above it first — it defines `DB`, `r`, `get_user`.)

**Why / trap.** Order matters: **DB first, then delete** — if you deleted first, a concurrent reader could repopulate the cache with the *old* value before the DB write lands. Why delete over update-in-place: (1) a crash between "update cache" and "update DB" leaves the cache **permanently** diverged; a failed delete just means one stale TTL window; (2) with computed/joined payloads, recomputing on next miss is simpler and safer than dual-writing; (3) you never pay to warm a key nobody reads again. Exam line: *write-through to the DB, invalidate the cache.*

---

## Block 4 — Expiration

**Q.** Set a session key three ways, inspect its TTL, and explain the two **negative** TTL return values you must never confuse.

```python
import time
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True, protocol=2)

r.set("session:abc", "token-xyz", ex=30)      # SETEX's modern inline form
print(r.ttl("session:abc"))                    # ~30
r.set("profile:42", "ad-hoc"); r.expire("profile:42", 30)   # EXPIRE: attach TTL after the fact
print(r.ttl("profile:42"))                     # ~30

r.set("forever:key", "no ttl")
print(r.ttl("forever:key"))                    # -1
r.delete("forever:key")
print(r.ttl("forever:key"))                    # -2

r.set("session:short", "tick", ex=1); time.sleep(1.1)
print("vanished:", r.get("session:short"))     # None — observed the vanish
```

**Why / trap.** **`TTL` returns −1 = key exists but has NO expiry; −2 = key does not exist.** Mixing these up in code ("−1 means missing") is a real-world bug and an exam favorite. Expired keys are removed **lazily** (when accessed) **and actively** (background sampling) — expiry is *eventually* exact, don't build correctness on millisecond timing. `SETEX` is the classic set+TTL command — redis-py 8.x marks `setex()` deprecated in favor of `SET ... EX n` (used above), but the *command name* is still what the exam's syntax cards quiz.

---

## Block 5 — Invalidation strategies

**Q.** SupportBrain now runs 4 app instances behind a load balancer. Whiteboard (say out loud) four invalidation strategies, when each wins, and which two the exam expects by default.

**Answer (recite and compare):**

| Strategy | How | Wins when | Fails when |
|---|---|---|---|
| **TTL expiry** | every key self-expires | data tolerates bounded staleness (prices, weather) | staleness window is unacceptable |
| **Explicit delete on write** | writer deletes key after DB update | strong freshness, single writer (block 3) | multiple app instances — other instances' *local* state won't hear about it |
| **Key versioning** | bump the key itself: `user:42:v3` → `v4` | deploys / schema changes — old keys are abandoned, no delete storm | orphan keys linger until TTL; readers must know the current version |
| **Pub/sub invalidation** | writer publishes `invalidate user:42`; every instance flushes | many app instances needing coherent local caches | added moving part; a missed message = stale until TTL |

**Why / trap.** The exam defaults are **TTL + delete-on-write** — reach for the others only when the scenario adds a constraint (multi-instance coherence → pub/sub; zero-downtime schema change → versioning). The belt-and-braces production answer: **explicit invalidation *plus* a backstop TTL** — every strategy except TTL fails open to "stale forever" without one. ("There are only two hard things in computer science: cache invalidation, naming things, and off-by-one errors.")

---

## Block 6 — Eviction policies

**Q.** The cache node has 32 MB. Configure it, then contrast `noeviction`, `allkeys-lru`, and `volatile-lru` — which one does a *cache* want, and which one is a booby trap here?

```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True, protocol=2)

r.config_set("maxmemory", "32mb")
r.config_set("maxmemory-policy", "allkeys-lru")
print(r.config_get("maxmemory"), r.config_get("maxmemory-policy"))
```

(Verified: redis-stack defaults are `maxmemory=0` — *no limit* — and `noeviction`, so this CONFIG SET is a real change, not a no-op. **Azure-side:** on managed tiers you set these per cache instance via configuration, not ad-hoc `CONFIG SET`.)

**Why / trap.** At the memory wall: **`noeviction`** = reject writes with errors — correct for a *store* (queues, session state you can't lose), wrong for a cache. **`allkeys-lru`** = evict the least-recently-used key overall — **the cache answer**: any key is fair game because everything is recomputable. **`volatile-lru`** = evict LRU *only among keys with a TTL* — the trap: if your populate path ever wrote keys without TTL (a bug, a different client), they're **immortal**, memory fills, and the policy degenerates into noeviction anyway. Rule: a cache wants an **`allkeys-*`** policy; reach for `volatile-*` only when the instance deliberately mixes cache data with must-keep TTL-less data.

---

## Block 7 — NX locks (done-when extra)

**Q.** Two chat instances race to rebuild the `docs:embeddings` batch job. One line of Redis makes one of them win. Which flags do what — and what kills the lock if the winner crashes?

```python
import time
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True, protocol=2)

got = r.set("lock:job", "instance-1", nx=True, ex=30)   # True  — winner
print("first :", got)
print("second:", r.set("lock:job", "instance-2", nx=True, ex=30))  # None — loser
print("ttl    :", r.ttl("lock:job"))                    # ~30 — crash-safety fuse
r.delete("lock:job")
```

**Why / trap.** **`NX` = set only if Not eXists** — the first caller wins, everyone else gets `None`: that's the distributed-lock primitive. The paired **`EX 30`** is the fuse: if the winner crashes mid-job the lock *expires* instead of deadlocking the fleet. (Mirror flag: **`XX`** = set only if it *does* exist — update-if-present semantics.) Say the sentence cold: *"SET key token NX EX 30 gives me a mutually exclusive, self-expiring lock."* The token value matters in production: only delete the lock if you still own the token (Lua compare-and-delete), or you'll release someone else's lock after your own expired.

---

## Block 8 — Pipelining (done-when extra)

**Q.** SupportBrain warms 500 tenant keys at deploy time — one RTT per `SET` is 500 round trips. Fix it, and state the one-sentence answer.

```python
import time
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True, protocol=2)

t0 = time.perf_counter()
for i in range(500):
    r.set(f"warm:{i}", f"v{i}")
print(f"one-by-one: {time.perf_counter() - t0:.3f}s")

t0 = time.perf_counter()
pipe = r.pipeline()
for i in range(500):
    pipe.set(f"warm:{i}", f"v{i}")
pipe.execute()
print(f"pipelined : {time.perf_counter() - t0:.3f}s")   # ~10-50x faster, even locally
```

**Why / trap.** Say the sentence: *"Pipelining batches multiple commands into one network round trip — it's the main throughput lever, not a correctness tool."* A plain `pipeline()` is **not atomic** (other clients interleave) — that's its point: same guarantees as sequential commands, minus the RTTs. Pass `transaction=True` (the default) for MULTI/EXEC atomicity; pass `transaction=False` when you want pure batching. Don't confuse with Pub/Sub (that's messaging; this is transport).

---

## Block 9 — Vector search: index + load

**Q.** The semantic cache needs similarity search over prompt embeddings. Create the RediSearch index cold — the exact `FT.CREATE` from the README — then load 50 cached prompts (both tenants, three question families) as float32 bytes.

```python
import hashlib
import numpy as np
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=False, protocol=2)
DIM = 8

def embed(text: str) -> np.ndarray:
    """Deterministic bag-of-words embedder (same as Lab 02): shared words -> nearby vectors."""
    vec = np.zeros(DIM, dtype=np.float32)
    for token in text.lower().split():
        vec[int(hashlib.md5(token.encode()).hexdigest(), 16) % DIM] += 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm else vec

def embed_bytes(text: str) -> bytes:
    return embed(text).astype(np.float32).tobytes()

try:
    r.execute_command("FT.DROPINDEX", "docidx")
except redis.ResponseError:
    pass

# the exam-cold line: ON HASH, PREFIX 1 doc:, HNSW, 8 = TYPE/DIM/DISTANCE_METRIC + tenant TAG
r.execute_command(
    "FT.CREATE", "docidx", "ON", "HASH", "PREFIX", 1, "doc:",
    "SCHEMA", "embedding", "VECTOR", "HNSW", 6,
    "TYPE", "FLOAT32", "DIM", DIM, "DISTANCE_METRIC", "COSINE",
    "tenant", "TAG",      # indexed beside the vector -> block 11 filters on it
)

QUESTIONS = [
    "how do i reset my password",
    "how do i change my billing plan",
    "how do i export my data",
    "how do i enable two factor authentication",
    "api authentication uses bearer tokens",
]
TENANTS = ["contoso", "fabrikam"]

pipe = r.pipeline()
for i in range(50):
    q = f"{QUESTIONS[i % len(QUESTIONS)]} variant {i // len(QUESTIONS)}"
    pipe.hset(f"doc:{i}", mapping={
        "tenant": TENANTS[i % 2],
        "prompt": q,
        "completion": f"ANSWER[{q}]",      # semantic-cache payload — block 11 uses it
        "embedding": embed_bytes(q),
    })
pipe.execute()
print("docs:", len(r.keys("doc:*")))
```

**Why / trap.** The `HNSW 6` is **counted pairs**: 3 parameters × 2 tokens each (`TYPE FLOAT32`, `DIM 8`, `DISTANCE_METRIC COSINE`) — miscount and the command rejects. RediSearch hashes don't nest: `HSET doc:n embedding <bytes>` stores the vector as a **flat binary string field**, which is why `np.float32.tobytes()` and `decode_responses=False` matter. The extra `tenant TAG` in the schema is deliberate: **only declared fields are indexed** — skip it and block 11's `@tenant:{...}` filter matches *nothing* (verified: returns 0 hits on a full index), the silent-failure version of Lab 02's missing composite index. Real SupportBrain: same Azure OpenAI `text-embedding-3-small` as the Postgres side, `DIM 1536`; never mix models in one index. Note `PREFIX 1 doc:` — the index only sees keys under that namespace; the `user:*`/`session:*` keys from blocks 2–4 stay out.

---

## Block 10 — Vector search: KNN query

**Q.** Write the KNN query cold: the 5 nearest cached prompts to a freshly worded password question — and name the incantation without which the parser rejects you.

```python
qvec = embed_bytes("password reset help please")
raw = r.execute_command(
    "FT.SEARCH", "docidx", "*=>[KNN 5 @embedding $vec]",
    "PARAMS", 2, "vec", qvec,
    "SORTBY", "__embedding_score",
    "DIALECT", 2,
)
print("hits:", raw[0])
print("ids  :", raw[1::2])   # even indexes are doc keys, odd are field lists
```

**Why / trap.** **`DIALECT 2`** is the exam's favorite footgun: vector KNN syntax (`*=>[KNN k @field $param]`) was introduced in query dialect 2 — omit it and the query **fails or misinterprets**, it does not fall back gracefully. `PARAMS 2` is the count-of-tokens convention again (one pair: `vec`, the blob). The score field `__embedding_score` is cosine **distance** (0 = identical) — *smaller is closer*, same mental model as pgvector's `<=>`. Redis-side this is in-memory HNSW: sub-millisecond KNN with no disk round trips, which is exactly the *"5 most similar embeddings in under 5 ms"* scenario the cards drill.

---

## Block 11 — The semantic cache

**Q.** Build the case-thread payoff: `semantic_answer(prompt, tenant)` — embed → KNN → hit above threshold returns the cached completion; miss calls the "LLM" and caches it. Why must the tenant be in the query, not filtered after?

```python
import numpy as np

THRESHOLD = 0.15   # cosine distance: below = same question, semantically

def llm(prompt: str) -> str:
    """Stand-in for the AOAI call SupportBrain is paying for."""
    return f"FRESH-ANSWER[{prompt}]"

def semantic_answer(prompt: str, tenant: str) -> str:
    qvec = embed_bytes(prompt)
    raw = r.execute_command(
        "FT.SEARCH", "docidx",
        "(@tenant:{%s})=>[KNN 1 @embedding $vec]" % tenant,
        "PARAMS", 2, "vec", qvec,
        "SORTBY", "__embedding_score",
        "DIALECT", 2,
    )
    if raw[0] > 0:
        fields = raw[2]
        score = float(fields[fields.index(b"__embedding_score") + 1])
        cached_prompt = fields[fields.index(b"prompt") + 1].decode()
        if score < THRESHOLD:                      # semantic HIT
            print(f"hit   score={score:.4f} matched={cached_prompt!r}")
            return fields[fields.index(b"completion") + 1].decode()
        print(f"miss  score={score:.4f} (nearest: {cached_prompt!r})")
    else:
        print("miss  empty index")

    completion = llm(prompt)                       # pay for it once...
    n = r.incr("doc:counter")
    r.hset(f"doc:new{n}", mapping={
        "tenant": tenant, "prompt": prompt,
        "completion": completion, "embedding": embed_bytes(prompt),
    })
    return completion                              # ...cached for the next asker

print(semantic_answer("how do i reset my password", "contoso"))       # hit
print(semantic_answer("can you help me reset my password", "contoso"))  # hit — no shared words needed? (see below)
print(semantic_answer("how do i reset my password", "fabrikam"))      # hit — fabrikam's own entry
print(semantic_answer("when is the next solar eclipse", "contoso"))   # miss -> LLM -> cached
```

**Why / trap.** This **is** the exam scenario *"sub-millisecond semantic cache for LLM responses"*: embed incoming prompt → KNN against cached prompt embeddings → similarity above threshold returns the cached completion, else call the LLM and store. Three production notes: (1) the **`(@tenant:{...})` pre-filter inside the KNN expression** keeps contoso from ever receiving fabrikam's cached answer — same isolation boundary as Lab 02's `WHERE tenant = %s` (here it's tag syntax; the Lab 02 lesson about retrieve-then-filter returning *fewer than k* applies identically); (2) the threshold is on **distance**, so *below* = hit — inverted-boolean bugs live here; (3) honest caveat — with our 8-dim word-hashing embedder, "can you help me reset my password" only matches because it still contains *password*+ *reset*; the real AOAI embedder is what makes genuinely differently-worded prompts hit. Every `doc:new*` key should carry a TTL in production (semantic cache entries go stale when the product ships changes) — block 5's backstop.

---

## Block 12 — Done-when recap (whiteboard, no notes)

**Q.** Cold, from memory: the cache-aside write, the index, and the query.

```text
cache-aside read   GET -> miss -> DB -> SET k v EX 60
cache-aside write  UPDATE db;  DEL cache-key        (DB first, then invalidate)
lock               SET lock:job <token> NX EX 30
batch              pipe = r.pipeline(); ...; pipe.execute()

FT.CREATE docidx ON HASH PREFIX 1 doc:
  SCHEMA embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 8 DISTANCE_METRIC COSINE tenant TAG
FT.SEARCH docidx "*=>[KNN 5 @embedding $vec]" PARAMS 2 vec <bytes> DIALECT 2
```

Eviction one-liner: a cache wants **`allkeys-lru`**; `noeviction` is for stores; `volatile-lru` betrays you the day a key ships without TTL.

**Why / trap.** The whole lab in two commands and four lines. If you can write this block with the key closed, the lab is done — everything else is commentary.

---

## Self-check (map to "Done when")

- Cache-aside from memory, twice — blocks 2–3, key closed → your two **Solid Practice** runs.
- Write `FT.CREATE` / `FT.SEARCH` cold, including `HNSW 6` and **`DIALECT 2`**.
- One sentence each: **NX** = *"set only if absent — a self-expiring distributed lock with EX"*; **pipelining** = *"many commands, one round trip — throughput lever, not a transaction."*
- `TTL` on a key with no expiry? → **−1**. On a missing key? → **−2**.
- "Can't connect to Azure Managed Redis"? → **`ssl=True`, port 10000**.
- "Which eviction policy for a cache?" → **`allkeys-lru`** — never `noeviction`.

**Cleanup:** `docker rm -f redis-stack` (state is disposable).
