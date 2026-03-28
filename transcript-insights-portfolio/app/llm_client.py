from __future__ import annotations

import json
from typing import Any, Protocol

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency for portfolio artifact.
    OpenAI = None


class LLMClient(Protocol):
    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        reasoning_effort: str,
    ) -> dict[str, Any]:
        ...


class OpenAIResponsesClient:
    """Minimal wrapper around the Responses API used by planner and synthesizer."""

    def __init__(self, *, api_key: str) -> None:
        if OpenAI is None:
            raise RuntimeError("openai is not installed. This repository preserves the integration shape only.")
        if not api_key.strip():
            raise RuntimeError("OPENAI_API_KEY is required for the live LLM path.")
        self._client = OpenAI(api_key=api_key)

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        reasoning_effort: str,
    ) -> dict[str, Any]:
        response = self._client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw_text = getattr(response, "output_text", "") or "{}"
        return _parse_json_object(raw_text)


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1]).strip() if len(lines) >= 2 else "{}"
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        return {}
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return {}
