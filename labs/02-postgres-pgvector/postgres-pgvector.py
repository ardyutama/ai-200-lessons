"""Lab 02 — Azure Database for PostgreSQL + pgvector — working file.

Steps follow README.md in this folder. Attempt-first rule: first pass may
consult SOLUTION.md; the two runs counting toward Solid Practice are closed-book.

Case thread: you are building SupportBrain — multi-tenant support-docs RAG.
Tenants: contoso, fabrikam. Categories: faq, blog, docs. A user question comes
in as text -> embed -> nearest articles for THAT tenant -> stuff into the prompt.

Shell setup (once per session):
    docker start pgvec 2>/dev/null || docker run -d --name pgvec -e POSTGRES_PASSWORD=postgres -p 5432:5432 pgvector/pgvector:pg16
    source ../../.venv/bin/activate
(step 7 needs the pool extra: pip install -r ../../requirements.txt)
"""

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

# --- Step 1: Connect ---------------------------------------------------------
# Prove the connection. What must change in DSN on real Flexible Server, and why?
# TODO: your code here
import psycopg
import hashlib
import numpy as np

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

DSN = "host=localhost dbname=postgres user=postgres password=postgres sslmode=disable"

# --- Step 2: Extension + schema ----------------------------------------------
# CREATE EXTENSION vector — Azure-side prerequisite: azure.extensions server
# parameter. Table: docs(id, tenant, category, content, embedding vector(8)).
# TODO: your code here
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
# --- Step 3: Embedder + load ---------------------------------------------------
# Deterministic bag-of-words embedder (stand-in for AOAI text-embedding-3);
# insert ~200 rows across both tenants and 3 categories in ONE batch.
# TODO: your code here
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
# --- Step 4: Similarity search ---------------------------------------------------
# Nearest 5 to a query vector with <->, <#>, <=>. Which one is cosine?
# TODO: your code here
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
# --- Step 5: Indexes ---------------------------------------------------------------
# EXPLAIN (Seq Scan) -> CREATE INDEX ... USING hnsw (opclass!) -> EXPLAIN.
# Drop it; try IVFFlat built on an EMPTY vs POPULATED table — say the trap.
# Tune ivfflat.probes / hnsw.ef_search: recall vs compute.
# TODO: your code here
qv = embed("how do i reset my password")

with psycopg.connect(DSN, autocommit=True) as conn:
    conn.execute("DROP INDEX IF EXISTS docs_hnsw;")     # README: drop HNSW first
    conn.execute("DROP TABLE IF EXISTS docs2;")
    conn.execute("CREATE TABLE docs2 (LIKE docs);")     # empty clone
    conn.execute("CREATE INDEX docs2_ivf ON docs2 USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);")
    conn.execute("INSERT INTO docs2 SELECT * FROM docs;")
    conn.execute("SET enable_seqscan = off; SET ivfflat.probes = 1;")
    approx = [r[0] for r in conn.execute(
        "SELECT id FROM docs2 ORDER BY embedding <=> %s::vector LIMIT 5", (qv,))]
    exact = [r[0] for r in conn.execute(
        "SELECT id FROM docs  ORDER BY embedding <=> %s::vector LIMIT 5", (qv,))]
    print("exact :", exact)
    print("approx:", approx)
    conn.execute("REINDEX INDEX docs2_ivf;")  

# --- Step 6: RAG with metadata filter + tenant isolation -----------------------------
# WHERE category = 'faq'; then WHERE tenant = %s. Why does filtering in SQL
# beat retrieve-then-filter? What incident does the tenant predicate prevent?
# TODO: your code here
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
# --- Step 7: Connection pooling ------------------------------------------------------
# Rewrite with psycopg_pool.ConnectionPool. Azure-side answer to connection
# storms: PgBouncer on Flexible Server (port 6432). What happens to session
# GUCs (probes / ef_search) under transaction pooling?
# TODO: your code here
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