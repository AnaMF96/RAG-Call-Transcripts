from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ExecuteRequest:
    query: str
    request_id: str
    mode: str = "transcript_insights"
    options: dict[str, Any] | None = None


@dataclass(frozen=True)
class NormalizedQuery:
    original: str
    normalized: str
    fingerprint: str


@dataclass(frozen=True)
class TranscriptScope:
    audience: str
    date_start: str | None = None
    date_end: str | None = None


@dataclass(frozen=True)
class QueryPlanningRequest:
    query: str
    normalized_query: str
    audience: str
    date_start: str | None = None
    date_end: str | None = None
    max_queries: int = 4


@dataclass(frozen=True)
class RetrievalPlan:
    audience: str
    semantic_query: str
    queries: tuple[str, ...] = ()
    date_start: str | None = None
    date_end: str | None = None
    target_company: str | None = None
    target_people: tuple[str, ...] = ()
    intent_hint: str | None = None


@dataclass(frozen=True)
class RetrievedChunk:
    evidence_id: str
    call_id: str
    chunk_id: int
    chunk_index: int
    customer: str
    source_type: str
    transcript_date: str
    source_url: str
    quote_text: str
    similarity: float


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    call_id: str
    chunk_id: int
    chunk_index: int
    customer: str
    source_type: str
    transcript_date: str
    source_url: str
    quote_text: str
    similarity: float


@dataclass(frozen=True)
class SynthesisRequest:
    query: str
    audience: str
    evidence_items: tuple[EvidenceItem, ...]
    request_id: str


@dataclass(frozen=True)
class SynthesizedFinding:
    answer: str
    supporting_evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class Finding:
    answer: str
    supporting_evidence_ids: tuple[str, ...]
    evidence: EvidenceItem

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["supporting_evidence_ids"] = list(self.supporting_evidence_ids)
        return payload


@dataclass(frozen=True)
class RuntimeResponse:
    orientation: str
    findings: list[Finding]
    gaps: list[str]
    method: str

    def to_dict(self) -> dict[str, object]:
        return {
            "orientation": self.orientation,
            "findings": [item.to_dict() for item in self.findings],
            "gaps": self.gaps,
            "method": self.method,
        }
