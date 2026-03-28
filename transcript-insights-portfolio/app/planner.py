from __future__ import annotations

from typing import Any

from app.llm_client import LLMClient
from app.models import QueryPlanningRequest, RetrievalPlan
from app.prompt_templates import QUERY_PLANNER_SYSTEM_PROMPT, QUERY_PLANNER_USER_PROMPT


class DeterministicQueryPlanner:
    """Fallback planner used when the LLM path is disabled or unavailable."""

    def plan(self, request: QueryPlanningRequest) -> RetrievalPlan:
        queries: list[str] = [request.normalized_query]
        intent_hint = "general"

        if any(token in request.normalized_query for token in ("embedded", "assistant", "agent")):
            queries.extend(
                [
                    "embedded ai assistant inside workflow",
                    "assistant inside product workflow",
                ]
            )
            intent_hint = "embedded_agent"
        elif any(token in request.normalized_query for token in ("objection", "blocker", "pain point")):
            queries.extend(
                [
                    "objections trust friction manual work",
                    "blocking issues in calls",
                ]
            )
            intent_hint = "pain_points"

        return RetrievalPlan(
            audience=request.audience,
            semantic_query=request.normalized_query,
            queries=tuple(dict.fromkeys(queries)),
            date_start=request.date_start,
            date_end=request.date_end,
            intent_hint=intent_hint,
        )


class OpenAIQueryPlanner:
    """LLM-backed planner path retained for architecture fidelity."""

    def __init__(
        self,
        *,
        llm_client: LLMClient,
        model: str,
        reasoning_effort: str,
    ) -> None:
        self._llm_client = llm_client
        self._model = model
        self._reasoning_effort = reasoning_effort

    def plan(self, request: QueryPlanningRequest) -> RetrievalPlan:
        payload = self._llm_client.generate_json(
            system_prompt=QUERY_PLANNER_SYSTEM_PROMPT,
            user_prompt=QUERY_PLANNER_USER_PROMPT.format(
                query=request.query,
                audience=request.audience,
                date_start=request.date_start or "N/A",
                date_end=request.date_end or "N/A",
            ),
            model=self._model,
            reasoning_effort=self._reasoning_effort,
        )
        return parse_retrieval_plan(payload=payload, request=request)


def parse_retrieval_plan(
    *,
    payload: dict[str, Any],
    request: QueryPlanningRequest,
) -> RetrievalPlan:
    semantic_query = str(payload.get("semantic_query", "")).strip() or request.normalized_query
    queries_raw = payload.get("queries")
    queries: list[str] = []
    if isinstance(queries_raw, list):
        for item in queries_raw:
            normalized = " ".join(str(item).split()).strip()
            if normalized:
                queries.append(normalized)
    if not queries:
        queries = [semantic_query]

    intent_hint_raw = str(payload.get("intent_hint", "")).strip().lower()
    intent_hint = intent_hint_raw or "general"

    return RetrievalPlan(
        audience=request.audience,
        semantic_query=semantic_query,
        queries=tuple(dict.fromkeys(queries))[: request.max_queries],
        date_start=request.date_start,
        date_end=request.date_end,
        intent_hint=intent_hint,
    )
