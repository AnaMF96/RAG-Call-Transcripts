from __future__ import annotations

import json

from app.llm_client import LLMClient
from app.models import EvidenceItem, SynthesisRequest, SynthesizedFinding
from app.prompt_templates import SYNTHESIS_SYSTEM_PROMPT, SYNTHESIS_USER_PROMPT
from app.response_validator import validate_synthesized_findings


class DeterministicFindingSynthesizer:
    """Safe fallback path when synthesis is disabled or unavailable."""

    def synthesize(self, request: SynthesisRequest) -> list[SynthesizedFinding]:
        findings: list[SynthesizedFinding] = []
        for item in request.evidence_items[:3]:
            findings.append(
                SynthesizedFinding(
                    answer=_fallback_answer(item),
                    supporting_evidence_ids=(item.evidence_id,),
                )
            )
        return findings


class OpenAIFindingSynthesizer:
    """LLM-backed synthesis path retained for architecture fidelity."""

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

    def synthesize(self, request: SynthesisRequest) -> list[SynthesizedFinding]:
        evidence_payload = json.dumps(
            [
                {
                    "evidence_id": item.evidence_id,
                    "customer": item.customer,
                    "source_type": item.source_type,
                    "transcript_date": item.transcript_date,
                    "quote_text": item.quote_text,
                }
                for item in request.evidence_items
            ],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        payload = self._llm_client.generate_json(
            system_prompt=SYNTHESIS_SYSTEM_PROMPT,
            user_prompt=SYNTHESIS_USER_PROMPT.format(
                query=request.query,
                audience=request.audience,
                evidence=evidence_payload,
            ),
            model=self._model,
            reasoning_effort=self._reasoning_effort,
        )
        findings_raw = payload.get("findings")
        if not isinstance(findings_raw, list):
            return []

        parsed: list[SynthesizedFinding] = []
        for item in findings_raw:
            if not isinstance(item, dict):
                continue
            answer = str(item.get("answer", "")).strip()
            evidence_ids = item.get("supporting_evidence_ids")
            if not answer or not isinstance(evidence_ids, list):
                continue
            parsed.append(
                SynthesizedFinding(
                    answer=answer,
                    supporting_evidence_ids=tuple(
                        str(value).strip() for value in evidence_ids if str(value).strip()
                    ),
                )
            )
        return validate_synthesized_findings(parsed, evidence_items=request.evidence_items)


def _fallback_answer(item: EvidenceItem) -> str:
    return f"{item.customer} mentioned a relevant signal related to the question."
