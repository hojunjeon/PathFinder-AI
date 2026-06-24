# ULW Brief: SQLite embeddings with GMS

Objective: Configure PathFinder AI to create and store text-embedding-3-small embeddings in the SQLite development environment through the existing GMS_KEY/GMS gateway, without introducing pgvector or a separate vector database.

Tier: HEAVY. Justification: external GMS embeddings API integration plus DB schema/storage changes and retrieval behavior.

Skills: omo:ulw-loop for evidence-bound execution; omo:programming for Python code/tests; openai-docs for current embedding model/API facts; omo:git-master in STATUS mode only for dirty state and commit proposal.

Success criteria:
- C001 RED/GREEN: prove current SQLite chunk embedding path is missing, then store GMS text-embedding-3-small vectors on CompanySourceChunk with embedding_status transitions and no private data embedded.
- C002 Retrieval: prove SQLite vector search/ranking works locally without pgvector, falling back safely when embeddings are missing or GMS is unavailable.
- C003 Surface QA: drive a real CLI/Django shell/API-equivalent scenario that creates a public source chunk, embeds it via a mocked GMS embeddings response, queries it, and captures DB state/output plus cleanup receipt.

Constraints: preserve existing dirty work; no commit/stage without approval; no user private profile/cover letter/job posting stored in public embedding corpus; use GMS_KEY and GMS gateway; SQLite only; minimal implementation; keep previous GraphRAG retrieval intact.
