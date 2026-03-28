from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    query_planning_enabled: bool
    synthesis_enabled: bool
    llm_provider: str
    llm_model: str
    llm_reasoning_effort: str
    embedding_provider: str
    embedding_model: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    top_k: int
    max_queries: int


def _to_bool(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    return Settings(
        query_planning_enabled=_to_bool(os.getenv("RUNTIME_QUERY_PLANNING_ENABLED"), default=True),
        synthesis_enabled=_to_bool(os.getenv("RUNTIME_SYNTHESIS_ENABLED"), default=True),
        llm_provider=os.getenv("RUNTIME_LLM_PROVIDER", "openai").strip() or "openai",
        llm_model=os.getenv("RUNTIME_LLM_MODEL", "gpt-5.2").strip() or "gpt-5.2",
        llm_reasoning_effort=(
            os.getenv("RUNTIME_LLM_REASONING_EFFORT", "medium").strip().lower() or "medium"
        ),
        embedding_provider=os.getenv("RUNTIME_EMBEDDING_PROVIDER", "openai").strip() or "openai",
        embedding_model=os.getenv("RUNTIME_EMBEDDING_MODEL", "text-embedding-3-large").strip() or "text-embedding-3-large",
        db_host=os.getenv("RUNTIME_DB_HOST", "").strip(),
        db_port=max(1, int(os.getenv("RUNTIME_DB_PORT", "5432"))),
        db_name=os.getenv("RUNTIME_DB_NAME", "").strip(),
        db_user=os.getenv("RUNTIME_DB_USER", "").strip(),
        db_password=os.getenv("RUNTIME_DB_PASSWORD", "").strip(),
        top_k=max(1, int(os.getenv("RUNTIME_TOP_K", "8"))),
        max_queries=max(1, min(8, int(os.getenv("RUNTIME_MAX_QUERIES", "4")))),
    )
