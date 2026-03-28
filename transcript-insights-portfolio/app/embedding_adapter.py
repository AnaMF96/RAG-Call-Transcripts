from __future__ import annotations

from typing import Protocol

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency for portfolio artifact.
    OpenAI = None


class EmbeddingAdapter(Protocol):
    def embed_query(self, query: str) -> list[float]:
        ...


class OpenAIEmbeddingAdapter:
    """Portfolio-safe representation of the embeddings provider."""

    def __init__(self, *, api_key: str, model: str) -> None:
        if OpenAI is None:
            raise RuntimeError("openai is not installed. The embedding path is included for architecture fidelity.")
        if not api_key.strip():
            raise RuntimeError("OPENAI_API_KEY is required for the live embedding path.")
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def embed_query(self, query: str) -> list[float]:
        response = self._client.embeddings.create(model=self._model, input=query)
        return list(response.data[0].embedding)
