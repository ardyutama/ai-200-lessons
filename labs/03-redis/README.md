# Lab 03 — Azure Managed Redis (floci-az)

**Study-guide bullets covered:** caching, expiration, invalidation · vector indexing for similarity search.

**Setup:** `floci az start && eval $(floci az env)` — floci-az runs a real Redis. Use `redis-cli -p <port>` (see `floci az status`) and redis-py. If `FT.*` commands error with "unknown command", the emulated Redis lacks RediSearch — fall back: `docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest` and repeat step 5 there.

## Steps

1. **Cache-aside.** Write a `get_user(id)` that reads cache → miss → "DB" (a dict) → `SET user:<id> ... EX 60`. Then update the DB and **delete** the key. Explain why delete-on-write beats update-in-place for cache coherence.
2. **Expiration.** `SETEX`, `EXPIRE`, `TTL` (interpret -1 vs -2). Observe a key vanish.
3. **Invalidation strategies.** Be ready to compare: TTL, explicit delete, key versioning, pub/sub invalidation across app instances.
4. **Eviction policies.** Set `maxmemory 32mb` + `allkeys-lru` (via CONFIG SET if permitted, else conceptually). Contrast `noeviction` vs `allkeys-lru` vs `volatile-lru`; which one does a cache want?
5. **Vector search.** Create an index: `FT.CREATE docidx ON HASH PREFIX 1 doc: SCHEMA embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 8 DISTANCE_METRIC COSINE`. Load 50 docs with `HSET doc:n embedding <float32 bytes>` (redis-py: `np.array(v, dtype=np.float32).tobytes()`). Query: `FT.SEARCH docidx "*=>[KNN 5 @embedding $vec]" PARAMS 2 vec <bytes> DIALECT 2`.
6. **Semantic cache scenario.** Describe (or build) the LLM semantic-cache pattern: embed prompt → KNN → hit above threshold returns cached completion.

## Done when

- [ ] Cache-aside implemented from memory, twice
- [ ] You can write the FT.CREATE/FT.SEARCH syntax cold, including `DIALECT 2`
- [ ] You can explain NX locks and pipelining in one sentence each

## Cleanup

`floci az stop` (and `docker rm -f redis-stack` if used).
