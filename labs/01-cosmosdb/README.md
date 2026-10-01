# Lab 01 — Cosmos DB for NoSQL (floci-az)

**Study-guide bullets covered:** connect with the SDK and run queries · optimize RUs via indexing policies and consistency levels · store/retrieve embeddings + vector similarity · change feed processor.

**Setup:** `floci az start && eval $(floci az env)` and activate the repo venv.

## Steps

1. **Connect & create.** With the Python SDK, create a database `aidb` and container `docs` with partition key `/category`. Point `CosmosClient` at the emulator endpoint/keys floci-az prints.
2. **CRUD + query.** Insert 5 docs `{id, category, title, embedding:[3 floats]}`. Do a point read (id + partition key) and a parameterized cross-partition query; compare the request-charge headers (`x-ms-request-charge`) between them.
3. **Indexing policy.** Set an indexing policy excluding `/large_blob/*` from indexing; observe (conceptually — the emulator may not meter RUs) and be ready to explain the RU effect of excluded paths and when composite indexes are required (multi-key ORDER BY).
4. **Vector search.** Recreate the container with a vector embedding policy (`/embedding`, 3 dims, float32) and a `flat` vector index. Query with `SELECT c.title FROM c ORDER BY RANK VectorDistance(c.embedding, @qv)`. Swap to `quantizedFlat`/`diskANN` and say out loud when each is appropriate.
5. **Consistency.** Name all five levels in order; explain why Session is the default and what Strong costs in RU/latency.
6. **Change feed.** Read the change feed with `container.query_items_change_feed()` (or an infinite iterator), insert a new doc, confirm the handler sees it. Explain the role of the lease container in the hosted processor.

## Done when

- [ ] You can do steps 1–4 from memory, twice, without the notes
- [ ] You can whiteboard the change-feed components (monitored container, lease container, delegate, processor name)
- [ ] You can answer: "which vector index type for 1M embeddings and why?"

## Cleanup

`floci az stop` (state is disposable) or delete the container via SDK.
