from __future__ import annotations

from app.models import EvidenceItem, SynthesizedFinding


def validate_synthesized_findings(
    findings: list[SynthesizedFinding],
    *,
    evidence_items: tuple[EvidenceItem, ...],
) -> list[SynthesizedFinding]:
    valid_ids = {item.evidence_id for item in evidence_items}
    accepted: list[SynthesizedFinding] = []
    for finding in findings:
        if not finding.answer.strip():
            continue
        if not finding.supporting_evidence_ids:
            continue
        if not all(evidence_id in valid_ids for evidence_id in finding.supporting_evidence_ids):
            continue
        accepted.append(finding)
    return accepted
