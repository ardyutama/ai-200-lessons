"""Lab 03 — Azure Managed Redis — working file.

Steps follow README.md in this folder. Attempt-first rule: first pass may
consult SOLUTION.md; the two runs counting toward Solid Practice are closed-book.

Case thread: SupportBrain (continued from Lab 02) adds a Redis tier — a cache
for user/tenant metadata, and a semantic cache in front of the LLM:
embed prompt -> KNN -> hit above threshold returns the cached completion.

Shell setup (once per session):
    docker start redis-stack 2>/dev/null || docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
    source ../../.venv/bin/activate
(floci-az exposes no Redis in this build — redis-stack is the runtime, same
"real engine in Docker" split as Lab 02's pgvec.)

Naming: this file is redis-cache.py, NOT redis.py — a file named redis.py here
shadows the real redis package and breaks `import redis` with AttributeError.
"""

import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=False, protocol=2)

# --- Step 1: Cache-aside -----------------------------------------------------
# get_user(id): cache -> miss -> "DB" dict -> SET user:<id> EX 60. Update the
# DB, then DELETE the key. Why does delete-on-write beat update-in-place?
# TODO: your code here

# --- Step 2: Expiration ------------------------------------------------------
# SETEX / EXPIRE / TTL — interpret TTL -1 vs -2; watch a key vanish.
# TODO: your code here

# --- Step 3: Invalidation strategies (whiteboard, say out loud) --------------
# Compare: TTL, explicit delete, key versioning, pub/sub across app instances.

# --- Step 4: Eviction policies ------------------------------------------------
# CONFIG SET maxmemory 32mb + maxmemory-policy allkeys-lru. Contrast
# noeviction / allkeys-lru / volatile-lru — which does a cache want?
# TODO: your code here

# --- Step 5: Vector search -----------------------------------------------------
# FT.CREATE docidx ON HASH PREFIX 1 doc: SCHEMA embedding VECTOR HNSW 6
# TYPE FLOAT32 DIM 8 DISTANCE_METRIC COSINE tenant TAG. Load 50 docs
# (np.array(v, dtype=np.float32).tobytes()). Query:
# FT.SEARCH docidx "*=>[KNN 5 @embedding $vec]" PARAMS 2 vec <bytes> DIALECT 2.
# TODO: your code here

# --- Step 6: Semantic cache ----------------------------------------------------
# Build the SupportBrain semantic cache: embed prompt -> KNN -> hit above
# threshold returns cached completion, miss calls "LLM" and stores it.
# TODO: your code here

# --- Done-when extras ----------------------------------------------------------
# One sentence each, cold: what SET key token NX EX 30 gives you (locks);
# what r.pipeline() buys you (pipelining).
# TODO: your code here
