from __future__ import annotations

import hashlib
import re

from app.models import NormalizedQuery, TranscriptScope


def build_normalized_query(query: str) -> NormalizedQuery:
    compact = " ".join(query.split()).strip()
    lowered = compact.lower()
    lowered = re.sub(r"[^\w\s:/.-]+", " ", lowered)
    normalized = " ".join(lowered.split())
    fingerprint = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return NormalizedQuery(original=query, normalized=normalized, fingerprint=fingerprint)


def classify_scope(query: str) -> TranscriptScope:
    compact = " ".join(query.lower().split())
    if "sales call" in compact or "sales calls" in compact:
        return TranscriptScope(audience="sales")
    if "customer call" in compact or "customer calls" in compact:
        return TranscriptScope(audience="customer")
    return TranscriptScope(audience="both")
