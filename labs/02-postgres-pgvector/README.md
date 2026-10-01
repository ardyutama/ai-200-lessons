# Lab 02 — Azure Database for PostgreSQL + pgvector

**Study-guide bullets covered:** connect and query via SDK · schema and index design · pgvector indexing strategies and compute overhead · RAG with metadata filters · connection optimization.

**Setup:** the `pgvec` container from [SETUP.md](../../SETUP.md) (`pgvector/pgvector:pg16` on :5432, user/pass `postgres`). floci-az emulates the Flexible Server control plane; the pgvector engine work happens against this real Postgres.

## Steps

1. **Connect.** `psycopg.connect("host=localhost dbname=postgres user=postgres password=postgres sslmode=disable")` — and note that real Azure Postgres requires `sslmode=require`. Say why.
2. **Schema + extension.** `CREATE EXTENSION vector;` then a table `docs(id bigserial primary key, tenant text, category text, content text, embedding vector(8))`. On Flexible Server the extension must first be allow-listed via the `azure.extensions` server parameter — know that step for the exam.
3. **Load.** Insert ~200 rows across 3 categories with random embeddings (numpy).
4. **Similarity search.** Nearest 5 to a query vector with each operator: `<->`, `<#>`, `<=>`. Know which is cosine.
5. **Indexes.** `EXPLAIN` the query (Seq Scan) → `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops);` → `EXPLAIN` again (Index Scan). Then drop it and try IVFFlat on an **empty** vs **populated** table; articulate the gotcha. Tune `ivfflat.probes` and `hnsw.ef_search` — recall vs compute.
6. **RAG with metadata filter.** `WHERE category = 'faq'` + ORDER BY distance LIMIT 5. Then the tenant-isolation variant: `WHERE tenant = $2`. Explain why filtering in SQL beats retrieve-then-filter.
7. **Connections.** Rewrite your script to use `psycopg_pool.ConnectionPool`. Name the Azure-side answer for connection storms: PgBouncer on Flexible Server.

## Done when

- [ ] You can write steps 4–6 SQL from memory
- [ ] You can explain HNSW vs IVFFlat (build time, memory, recall knobs, the empty-table trap)
- [ ] You can name the memory settings relevant to vector work (`shared_buffers`, `work_mem`, `maintenance_work_mem`)

## Cleanup

`docker rm -f pgvec`
