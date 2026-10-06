"""Lab 01 — Cosmos DB for NoSQL (floci-az) — working file.

Steps follow README.md in this folder. Attempt-first rule: first pass may
consult SOLUTION.md; the two runs counting toward Solid Practice are closed-book.

Shell setup (once per session):
    floci az start && eval $(floci az env)
    export COSMOS_ENDPOINT="http://localhost:4577/devstoreaccount1-cosmos"
    export COSMOS_KEY="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMh0=="
(floci az env prints NO Cosmos var — endpoint/key are derived by hand.)
"""

import os
from azure.cosmos import CosmosClient, PartitionKey

# --- Step 1: Connect & create ---------------------------------------------
# Database `aidb`, container `docs`, partition key /category.
# TODO: your code here

client = CosmosClient(os.environ["COSMOS_ENDPOINT"], 
credential=os.environ["COSMOS_KEY"])
db = client.get_database_client("aidb")
container = db.get_container_client("docs")


# --- Step 2: CRUD + query --------------------------------------------------
# 5 docs {id, category, title, embedding[3]}; point read vs parameterized
# cross-partition query; compare x-ms-request-charge.

for i, cat in enumerate(["faq", "blog", "faq", "docs", "blog"]):
        container.upsert_item({
            "id": f"doc{i}", "category": cat, "title": f"Title {i}",
            "embedding": [float(i), 0.1 * i, 0.2 * i]
     })

# --- Step 3: Indexing policy ------------------------------------------------
# Exclude /large_blob/*; know when composite indexes are REQUIRED.
indexing_policy = {
    "indexingMode": "consistent",
    "automatic": True,
    "includedPaths": [{"path": "/*"}],
    "excludedPaths": [
        {"path": "/large_blob/*"},
        {"path": "/_etag/?"}
    ]
}

container = db.create_container_if_not_exists(
    id="docs_idx",
    partition_key=PartitionKey(path="/category"),
    indexing_policy= indexing_policy
)
print("excluded /large_blob/*")
# --- Step 4: Vector search --------------------------------------------------
# Vector policy (3 dims, float32) + flat index; ORDER BY RANK VectorDistance.

# --- Step 5: Consistency (whiteboard, say out loud) -------------------------
# Five levels in order; why Session is default; what Strong costs.

# --- Step 6: Change feed ----------------------------------------------------
# query_items_change_feed; role of the lease container in the hosted processor.


