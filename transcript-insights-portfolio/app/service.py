from __future__ import annotations

from app.models import EvidenceItem, ExecuteRequest, Finding, QueryPlanningRequest, RuntimeResponse, SynthesisRequest
from app.query_normalizer import build_normalized_query, classify_scope


class TranscriptInsightsService:
    def __init__(
        self,
        *,
        query_planner,
        retrieval_pipeline,
        finding_synthesizer,
        fallback_synthesizer,
    ) -> None:
        self._query_planner = query_planner
        self._retrieval_pipeline = retrieval_pipeline
        self._finding_synthesizer = finding_synthesizer
        self._fallback_synthesizer = fallback_synthesizer

    def execute(self, request: ExecuteRequest) -> RuntimeResponse:
        normalized = build_normalized_query(request.query)
        scope = classify_scope(normalized.normalized)
        planning_request = QueryPlanningRequest(
            query=request.query,
            normalized_query=normalized.normalized,
            audience=scope.audience,
            date_start=scope.date_start,
            date_end=scope.date_end,
        )
        retrieval_plan = self._query_planner.plan(planning_request)
        retrieved_chunks = self._retrieval_pipeline.collect(plan=retrieval_plan, top_k=8)
        evidence_items = tuple(
            EvidenceItem(
                evidence_id=item.evidence_id,
                call_id=item.call_id,
                chunk_id=item.chunk_id,
                chunk_index=item.chunk_index,
                customer=item.customer,
                source_type=item.source_type,
                transcript_date=item.transcript_date,
                source_url=item.source_url,
                quote_text=item.quote_text,
                similarity=item.similarity,
            )
            for item in retrieved_chunks
        )

        if not evidence_items:
            return RuntimeResponse(
                orientation="I could not find transcript evidence related to the question.",
                findings=[],
                gaps=["No transcript evidence matched the retrieval scope."],
                method="The runtime planned retrieval queries and attempted embeddings search, but no evidence passed selection.",
            )

        synthesis_request = SynthesisRequest(
            query=request.query,
            audience=scope.audience,
            evidence_items=evidence_items,
            request_id=request.request_id,
        )
        gaps: list[str] = []
        try:
            synthesized_findings = self._finding_synthesizer.synthesize(synthesis_request)
            synthesis_mode = "llm-assisted"
        except Exception as exc:
            synthesized_findings = self._fallback_synthesizer.synthesize(synthesis_request)
            synthesis_mode = "deterministic-fallback"
            gaps.append(f"Synthesis fallback used: {exc}")

        findings = [
            Finding(
                answer=item.answer,
                supporting_evidence_ids=item.supporting_evidence_ids,
                evidence=next(
                    evidence for evidence in evidence_items if evidence.evidence_id in item.supporting_evidence_ids
                ),
            )
            for item in synthesized_findings
        ]

        return RuntimeResponse(
            orientation="I searched transcript evidence and returned findings grounded in retrieved chunks.",
            findings=findings,
            gaps=gaps,
            method=(
                "The runtime normalized the question, optionally planned retrieval queries, "
                "retrieved transcript chunks, and used the "
                f"{synthesis_mode} path to build the final answer."
            ),
        )
