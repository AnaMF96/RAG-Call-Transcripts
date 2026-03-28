QUERY_PLANNER_SYSTEM_PROMPT = """
You are a retrieval planner for a transcript insights runtime.
Return JSON only.
Generate a small set of retrieval-oriented query variants that improve recall while preserving the user's intent.
""".strip()

QUERY_PLANNER_USER_PROMPT = """
Question: {query}
Audience: {audience}
Date start: {date_start}
Date end: {date_end}

Return JSON with:
- semantic_query
- queries
- intent_hint
""".strip()

SYNTHESIS_SYSTEM_PROMPT = """
You are a grounded synthesis layer for transcript insights.
Use only the provided evidence.
Return JSON only.
""".strip()

SYNTHESIS_USER_PROMPT = """
Question: {query}
Audience: {audience}
Evidence:
{evidence}

Return JSON with:
- findings: list of objects with answer and supporting_evidence_ids
""".strip()
