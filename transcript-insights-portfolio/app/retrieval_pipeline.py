from __future__ import annotations

from typing import Sequence

from app.db_client import DatabaseClient
from app.embedding_adapter import EmbeddingAdapter
from app.models import RetrievalPlan, RetrievedChunk


class RetrievalPipeline:
    """Embeddings retrieval over transcript chunks with pgvector-style SQL."""

    def __init__(
        self,
        *,
        db_client: DatabaseClient,
        embedding_adapter: EmbeddingAdapter,
    ) -> None:
        self._db_client = db_client
        self._embedding_adapter = embedding_adapter

    def collect(self, *, plan: RetrievalPlan, top_k: int) -> list[RetrievedChunk]:
        query_embedding = self._embedding_adapter.embed_query(plan.semantic_query)
        sql = self._build_similarity_sql(
            vector_literal=vector_to_literal(query_embedding),
            audience=plan.audience,
            limit=top_k,
        )
        rows = self._db_client.query_rows(sql)
        return [self._to_chunk(row) for row in rows]

    @staticmethod
    def _build_similarity_sql(
        *,
        vector_literal: str,
        audience: str,
        limit: int,
    ) -> str:
        audience_clause = ""
        if audience == "sales":
            audience_clause = "AND c.source_type = 'sales'"
        elif audience == "customer":
            audience_clause = "AND c.source_type = 'customer'"

        return f"""
SELECT
  ce.evidence_id,
  ce.call_id,
  ce.chunk_id,
  ce.chunk_index,
  c.customer_name AS customer,
  c.source_type,
  c.transcript_date,
  c.source_url,
  tc.content AS quote_text,
  1 - (ce.embedding <=> {vector_literal}::vector) AS similarity
FROM chunk_embeddings ce
JOIN transcript_chunks tc ON tc.chunk_id = ce.chunk_id
JOIN calls c ON c.call_id = ce.call_id
WHERE 1 = 1
  {audience_clause}
ORDER BY similarity DESC
LIMIT {limit}
""".strip()

    @staticmethod
    def _to_chunk(row: dict[str, object]) -> RetrievedChunk:
        return RetrievedChunk(
            evidence_id=str(row.get("evidence_id", "")),
            call_id=str(row.get("call_id", "")),
            chunk_id=int(row.get("chunk_id", 0) or 0),
            chunk_index=int(row.get("chunk_index", 0) or 0),
            customer=str(row.get("customer", "Redacted customer")),
            source_type=str(row.get("source_type", "")),
            transcript_date=str(row.get("transcript_date", "")),
            source_url=str(row.get("source_url", "https://example.invalid/source")),
            quote_text=str(row.get("quote_text", "")),
            similarity=float(row.get("similarity", 0.0) or 0.0),
        )


def vector_to_literal(values: Sequence[float]) -> str:
    return "[" + ",".join(f"{value:.6f}" for value in values) + "]"
