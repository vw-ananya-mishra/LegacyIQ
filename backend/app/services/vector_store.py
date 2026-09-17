"""
Vector Store - lightweight semantic search (embeddings + cosine similarity)
over the free-text knowledge in an ingested workbook: Documentation_Artifacts
excerpts, Business_Rules, and Modernization_Backlog recommendations.

This is the "Retrieval" half of a genuine Retrieval-Augmented Generation
pipeline:
  1. Retrieval  - embed the corpus once (cached per workbook_id), embed the
                  user's query, rank by cosine similarity  (this file)
  2. Augmentation - the top-k retrieved chunks are placed into the LLM prompt
                  as grounding context
  3. Generation - the LLM answers strictly from those chunks
                  (see AgentOrchestrator.knowledge_hub_search)

The index lives in memory per workbook_id (rebuilt on first search, or when
`force=True`). If no embedding provider is configured/reachable,
build_index() returns 0 and semantic_search() returns an empty list -
callers must treat that as "vector search unavailable" and say so, never
silently fall back to keyword matching pretending to be semantic search.
"""

import math
import sqlite3
from typing import Any, Dict, List, Optional

from app.services import llm_service

_INDEX_CACHE: Dict[str, List[Dict[str, Any]]] = {}


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _collect_documents(workbook_id: str) -> List[Dict[str, Any]]:
    from app.services.xlsx_ingestion import XLSXIngestionService
    svc = XLSXIngestionService()
    db_path = svc._get_db_path(workbook_id)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    docs: List[Dict[str, Any]] = []

    cursor.execute("SELECT * FROM documentation_artifacts")
    for row in cursor.fetchall():
        r = dict(row)
        text = f"{r.get('doc_title') or ''}. {r.get('excerpt') or ''}".strip(". ").strip()
        if text:
            docs.append({
                "id": r["id"], "text": text, "source_type": "documentation_artifact",
                "metadata": {
                    "doc_type": r.get("doc_type"), "application_id": r.get("application_id"),
                    "author": r.get("author"), "source_sheet": r.get("source_sheet"), "source_row": r.get("source_row"),
                },
            })

    cursor.execute("SELECT * FROM business_rules")
    for row in cursor.fetchall():
        r = dict(row)
        text = f"Business rule '{r.get('rule_name')}' in domain {r.get('business_domain')}, criticality {r.get('criticality')}."
        docs.append({
            "id": r["id"], "text": text, "source_type": "business_rule",
            "metadata": {"module_id": r.get("module_id"), "source_sheet": r.get("source_sheet"), "source_row": r.get("source_row")},
        })

    cursor.execute("SELECT * FROM modernization_backlog")
    for row in cursor.fetchall():
        r = dict(row)
        text = f"Modernization recommendation: {r.get('recommendation')} (target: {r.get('target_tech')}, risk: {r.get('risk_level')})."
        docs.append({
            "id": r["id"], "text": text, "source_type": "modernization_backlog",
            "metadata": {"application_id": r.get("application_id"), "source_sheet": r.get("source_sheet"), "source_row": r.get("source_row")},
        })

    return docs


def build_index(workbook_id: str, force: bool = False) -> int:
    """
    Embed and cache every searchable document for a workbook.
    Returns the number of documents indexed (0 if embeddings are unavailable).
    """
    if not force and workbook_id in _INDEX_CACHE:
        return len(_INDEX_CACHE[workbook_id])

    docs = _collect_documents(workbook_id)
    if not docs:
        _INDEX_CACHE[workbook_id] = []
        return 0

    texts = [d["text"] for d in docs]
    vectors: List[List[float]] = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        result = llm_service.embed_texts(batch)
        if result is None:
            _INDEX_CACHE[workbook_id] = []
            return 0
        vectors.extend(result)

    for doc, vec in zip(docs, vectors):
        doc["vector"] = vec

    _INDEX_CACHE[workbook_id] = docs
    return len(docs)


def is_index_ready(workbook_id: str) -> bool:
    return bool(_INDEX_CACHE.get(workbook_id))


def semantic_search(workbook_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Embed `query` and return the top_k most similar indexed documents,
    each with a cosine-similarity `score`. Builds the index on first use.
    Returns [] if embeddings are unavailable (vector search cannot run).
    """
    build_index(workbook_id)
    docs = _INDEX_CACHE.get(workbook_id) or []
    if not docs:
        return []

    query_vecs = llm_service.embed_texts([query])
    if not query_vecs:
        return []
    query_vec = query_vecs[0]

    scored = [
        {**{k: v for k, v in d.items() if k != "vector"}, "score": round(_cosine_similarity(query_vec, d["vector"]), 4)}
        for d in docs
    ]
    scored.sort(key=lambda d: d["score"], reverse=True)
    return scored[:top_k]
