from __future__ import annotations

import os

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover - optional for local inspection.
    FastAPI = None

from app.config import load_settings
from app.db_client import PostgresQueryClient
from app.embedding_adapter import OpenAIEmbeddingAdapter
from app.llm_client import OpenAIResponsesClient
from app.models import ExecuteRequest
from app.planner import DeterministicQueryPlanner, OpenAIQueryPlanner
from app.retrieval_pipeline import RetrievalPipeline
from app.service import TranscriptInsightsService
from app.synthesizer import DeterministicFindingSynthesizer, OpenAIFindingSynthesizer


def build_service() -> TranscriptInsightsService:
    settings = load_settings()

    llm_client = OpenAIResponsesClient(api_key=os.getenv("OPENAI_API_KEY", "").strip())
    embedding_adapter = OpenAIEmbeddingAdapter(
        api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        model=settings.embedding_model,
    )
    db_client = PostgresQueryClient(
        host=settings.db_host,
        port=settings.db_port,
        db_name=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )

    query_planner = (
        OpenAIQueryPlanner(
            llm_client=llm_client,
            model=settings.llm_model,
            reasoning_effort="low",
        )
        if settings.query_planning_enabled
        else DeterministicQueryPlanner()
    )

    finding_synthesizer = (
        OpenAIFindingSynthesizer(
            llm_client=llm_client,
            model=settings.llm_model,
            reasoning_effort=settings.llm_reasoning_effort,
        )
        if settings.synthesis_enabled
        else DeterministicFindingSynthesizer()
    )

    retrieval_pipeline = RetrievalPipeline(
        db_client=db_client,
        embedding_adapter=embedding_adapter,
    )

    return TranscriptInsightsService(
        query_planner=query_planner,
        retrieval_pipeline=retrieval_pipeline,
        finding_synthesizer=finding_synthesizer,
        fallback_synthesizer=DeterministicFindingSynthesizer(),
    )


def execute_transcript_insights(payload: dict[str, str]) -> dict[str, object]:
    service = build_service()
    request = ExecuteRequest(
        query=str(payload.get("query", "")).strip(),
        request_id=str(payload.get("request_id", "portfolio-demo")).strip() or "portfolio-demo",
    )
    return service.execute(request).to_dict()


app = FastAPI(title="Transcript Insights Runtime") if FastAPI is not None else None

if app is not None:
    @app.post("/run")
    def run(payload: dict[str, str]) -> dict[str, object]:
        return execute_transcript_insights(payload)
