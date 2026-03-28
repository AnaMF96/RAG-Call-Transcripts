# Transcript Insights Runtime

> 📘 **Full case study & system design**  
> This repository is part of a broader automation system.  
> For full context, problem framing, and decisions see the case study:  
> 👉 *[Making Transcript Knowledge Searchable with RAG](https://kaput-elm-8c7.notion.site/Making-Transcript-Knowledge-Searchable-with-RAG-33153feedf9f8050af5ed054464e2862)* (Notion)

---

## What This Repository Is

This repository is a sanitized reference implementation of an internal workflow used to answer questions over call transcripts.

It is designed to show:

- how a transcript question is interpreted
- when an LLM is used
- how transcript evidence is retrieved
- how synthesized answers stay grounded
- when the runtime falls back to deterministic behavior

The code is intentionally shaped like a production service:

- explicit data models
- wiring through a service layer
- separate planner, retrieval, and synthesis components
- provider adapters for database, embeddings, and LLM calls
- runtime flags for optional features

---

## What This Repository Is Not

This is **not** a public clone of the real internal system.

To keep it portfolio-safe:

- transcript data is not included
- customer names are removed
- provider credentials are not included
- internal endpoints are replaced with placeholders
- the repo is not expected to run end-to-end without external configuration

That trade-off is intentional. The goal here is to show architecture, reasoning, and design choices without exposing sensitive operational details.

---

## The Problem

Call transcripts contained valuable signals across product discovery, objections, pain points, and feature requests, but that knowledge was difficult to reuse.

Typical internal questions included:

- Which customers asked for an embedded AI assistant?
- What objections came up in recent sales calls?
- What themes are recurring across conversations?
- What happened in a specific call with a specific company or person?

Simple search was not enough for these questions. The system needed to support:

- broad and narrow questions
- evidence traceability
- reusable internal answers
- graceful fallback when evidence was weak

---

## High-Level Architecture

```text
User question
  ->
Normalize + classify
  ->
Optional LLM query planning
  ->
Embeddings retrieval over transcript chunks
  ->
Evidence selection and ranking
  ->
Optional LLM synthesis over retrieved evidence
  ->
Citation validation
  ->
Structured response
```

---

## Design Principles

### 1. Retrieval and synthesis are separate

The system does not ask an LLM to answer from scratch.

Instead:

- retrieval finds candidate evidence
- synthesis improves readability and reasoning over the retrieved evidence
- validation preserves grounding

This separation keeps the workflow more reliable and easier to debug.

### 2. Deterministic fallback is explicit

The runtime supports both:

- an LLM-assisted synthesis path
- a deterministic fallback path

That matters because internal teams need usable outputs even when synthesis is disabled, unavailable, or not sufficiently grounded.

### 3. Evidence remains the source of truth

Answers are structured around transcript evidence units, not around abstract summaries without traceability.

Each finding is expected to remain tied to source evidence through citations and stable identifiers.

### 4. The runtime is shaped for operability

The architecture is designed so that:

- planner behavior can be turned on or off
- synthesis can be enabled or disabled
- providers can be swapped
- external systems remain behind interfaces

---

## Repository Structure

```text
├── app/
│   ├── config.py
│   ├── db_client.py
│   ├── embedding_adapter.py
│   ├── llm_client.py
│   ├── main.py
│   ├── models.py
│   ├── planner.py
│   ├── prompt_templates.py
│   ├── query_normalizer.py
│   ├── response_validator.py
│   ├── retrieval_pipeline.py
│   ├── service.py
│   └── synthesizer.py
├── scripts/
│   └── ask_insights.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Key Components

### Query planner

The planner is responsible for deciding whether the original user question should be expanded into multiple retrieval queries.

In the real system, this was useful for:

- broad topic questions
- entity-specific questions
- questions that required better recall than a single phrasing would provide

This repo includes:

- an LLM-backed planner path
- a deterministic fallback planner path

### Retrieval pipeline

Retrieval is structured around transcript chunks as evidence units.

The retrieval layer is represented here as:

- an embeddings adapter
- a database client
- a pgvector-style SQL builder
- a retrieval pipeline that produces ranked chunks

The repo keeps the architecture visible even though no private transcript store is shipped with it.

### Synthesis layer

The synthesis layer is modeled as a separate stage over retrieved evidence.

It is responsible for:

- producing clearer user-facing findings
- preserving evidence links
- falling back cleanly when needed

This repo includes both:

- an LLM synthesis path
- a deterministic fallback synthesizer

### Validation

The runtime includes a lightweight validation layer to make the intended guardrails visible:

- findings should map back to retrieved evidence
- the final response contract should stay stable

---

## Public Execute Contract

The runtime returns:

- `orientation`
- `findings`
- `gaps`
- `method`

That contract is designed to balance readability and traceability:

- `orientation` explains what was found
- `findings` contain user-facing insights plus citations
- `gaps` make uncertainty explicit
- `method` explains how the answer was produced

---

## Example Runtime Modes

This repo preserves the idea of multiple runtime modes:

### LLM-assisted path

Used when:

- query planning is enabled
- synthesis is enabled
- the required providers are configured

Behavior:

- question is normalized
- planner may generate multiple retrieval queries
- retrieval collects transcript evidence
- synthesizer produces findings over the evidence pack
- validator checks that findings remain grounded

### Deterministic fallback path

Used when:

- synthesis is disabled
- providers are unavailable
- a grounded answer cannot be produced safely

Behavior:

- retrieval still runs
- findings are composed from evidence more conservatively
- the method/gaps fields can expose that fallback behavior happened

---

## Why This Repo Is Useful in a Portfolio

The point of this repository is not to prove that I can make a small mock chatbot run locally.

The point is to show that I can:

- structure ambiguous internal problems into clear system boundaries
- design workflows that balance usefulness and reliability
- introduce LLM reasoning without giving up operational control
- build internal tools that make knowledge more reusable

That is the part of the work I want the portfolio to reflect.

---

## Running Locally

You can inspect the code and the request/response flow directly.

The repository may require external configuration to run end-to-end because all real providers and data sources are intentionally removed.

The CLI entrypoint remains useful as an illustration of the public execute contract:

```bash
python3 scripts/ask_insights.py "Which customers asked for an embedded AI assistant?"
```

If no providers are configured, the runtime is expected to fail safely rather than pretending to be complete.

---

## Notes

- This repository is intentionally architecture-first.
- All company-specific details have been removed or replaced.
- External calls are represented through explicit adapters rather than hidden inside the business logic.
