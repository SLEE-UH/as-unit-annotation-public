# AI AS-unit Suggestions from Text Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task after user approval. Steps use checkbox syntax for tracking. Do not commit, push, create a PR, merge, or change GitHub Actions without explicit authorization.

**Goal:** Add a small synthetic-text-to-AI AS-unit review flow while preserving the audio placeholder.

**Architecture:** Add a separate JSON text endpoint. Pydantic AI returns segments; pure rules enforce exact text preservation and derive UI offsets. The page displays results and browser-local edits, keeping original AI positions unchanged.

**Tech Stack:** Existing Python 3.13, FastAPI, Pydantic AI with OpenAI-compatible provider, pytest, HTML and JavaScript. No new runtime dependency expected.

**Spec:** `docs/superpowers/specs/2026-11-01-text-as-units-design.md`

## Global Constraints

- Synthetic data only; no private identifying information, credentials, or participant data in source, tests, logs, or documentation.
- Preserve POST /analyze, the audio UI and existing tests. No RAG, database, persistence, transcription or training.
- Transcript: nonblank, at most 5,000 Unicode code points; optional cues: at most 5,000 code points as a bounded minor implementation decision. Preserve original text rather than trimming it.
- Only manually supplied cues may be used; absence must be explicit. Do not claim English-language validation is guaranteed by a heuristic.
- Boundary positions are zero-based, end-exclusive Unicode code-point offsets, internal boundaries only. They are UI positions, never equivalent to research word-level positions.
- Review edits do not recalculate original AI positions; label this permanently and mark edited status on input.
- Server-only LLM_API_TOKEN, LLM_API_GATEWAY and LLM_MODEL. At most two model attempts for invalid output; one attempt for provider errors. Use a 30-second total annotation deadline and no SDK transport retries.
- Automated tests disable real model requests. Do not install dependencies or build until the user approves this plan.
- Use an isolated feature branch in the existing checkout after approval; no new worktree. No commits during implementation without authorization.

## Review Focus

- Unicode and repeated text: derive offsets from segment lengths, never substring search (Task 1).
- Whitespace, empty or rewritten segments: reject invalid reconstruction (Task 1).
- Absent cues and prompt-injection-like synthetic input: input remains data, no fabricated evidence (Task 2).
- Provider errors, timeout and invalid output: bounded execution and sanitized responses (Tasks 2–3).
- HTML-like input and edits: text-only rendering and unchanged original-position labeling (Task 4).

### Task 1: Exact reconstruction and UI boundary rules

**Files:** Modify `app/rules.py`; create `tests/test_annotation_rules.py`. Keep existing saved-field rules intact.

**Interfaces:** `boundary_offsets(transcript: str, segments: list[str]) -> list[int]`; raises ValueError for empty segments or non-exact reconstruction. Returns cumulative code-point lengths except the final end.

- [x] Write failing tests: `boundary_offsets('Hi. Bye.', ['Hi. ', 'Bye.']) == [4]`; one segment yields []; repeated segments count separately; synthetic emoji uses Python Unicode lengths; empty list, empty segment, changed whitespace, missing text and rewritten text raise ValueError.
- [x] Run `uv run --locked pytest tests/test_annotation_rules.py -q`; confirm the new tests fail for missing behavior.
- [x] Implement only the pure validation and offset function.
- [x] Rerun that test module; require all cases to pass.

### Task 2: Structured model integration

**Files:** Modify `app/agent.py`; create `tests/test_text_agent.py`. Preserve existing audio schemas.

**Interfaces:** `TextAnalysisRequest(transcript: str, prosodic_cues: str | None = None)`; `SegmentSuggestion(segments: list[str])`; `TextAnalysisResponse(transcript: str, segments: list[str], boundary_positions: list[int], prosody_status: str)`; async `suggest_as_units(request: TextAnalysisRequest) -> TextAnalysisResponse`. Explicit internal exceptions distinguish unavailable configuration, failed provider, deadline and invalid output. Route code consumes these without exposing their details.

- [x] Write failing tests for nonblank/5,000-code-point input, cue length limit, exact reconstruction, and absent/whitespace-only cues producing `prosody_status == 'not_supplied'`.
- [x] Add mocked-model tests for manually supplied cues (`prosody_status == 'user_supplied'`), synthetic instruction-like content as data, structured-output rejection followed by valid output, exhaustion after two attempts, no provider-error retry, timeout and absent configuration. Assert safe failures contain no configured synthetic secret or raw provider exception text. Disable live model requests with Pydantic AI's supported request guard in every model test.
- [x] Run `uv run --locked pytest tests/test_text_agent.py -q`; confirm missing-behavior failures.
- [x] Implement the schemas, explicit environment configuration and Pydantic AI agent using Task 1's validation. Configure transport retries off and the total deadline. Use one shared validation retry budget, including structured parsing failures, rather than stacked retry loops. No logging of payloads or responses.
- [x] Run the new agent tests; require all cases to pass. Use FunctionModel or equivalent local mock for controlled output and retry behavior; never a live provider.

### Task 3: Separate text API

**Files:** Modify `app/main.py`; create `tests/test_text_api.py`; preserve `tests/test_skeleton.py`.

**Interfaces:** `POST /analyze-text` accepts TextAnalysisRequest JSON and returns TextAnalysisResponse. An overridable FastAPI dependency supplies the annotation callable for tests. HTTP 422 means invalid input, 503 unavailable configuration, 504 deadline exceeded, and 502 provider failure/invalid model output. Error bodies use fixed safe messages.

- [x] Write failing TestClient tests for successful synthetic text, missing cues, input rejection before any model call, each sanitized error status, and the existing audio response retaining its exact three fields.
- [x] Run `uv run --locked pytest tests/test_text_api.py tests/test_skeleton.py -q`; confirm only new behavior fails.
- [x] Implement the route and dependency adapter, leaving business logic in agent.py/rules.py and preserving the existing endpoint.
- [x] Rerun those tests; require all cases to pass.

### Task 4: Web input and human review

**Files:** Modify `app/page.html`; extend `tests/test_text_api.py` with page contract tests.

**Interfaces:** A separate synthetic-text form sends transcript and optional cues as JSON to /analyze-text. Keep audio controls and their handler. New result elements show segments, original boundary positions, cue status and an editable review textarea.

- [x] Write failing page-contract tests for the text form, synthetic-only notice, separate endpoint, and exact copy: `UI character positions only; not research word-level boundary positions.` and `Original AI boundary positions remain unchanged after edits; they are not recalculated.`
- [x] Run the new page tests; confirm the expected missing elements fail.
- [x] Implement a bounded form with disabled submit during requests, safe failure messages and textContent/value rendering. Separate original results from editable annotation; compute displayed context using Array.from(transcript), matching server code-point offsets. Discard stale text results when submitting another request, and mark review edits without altering positions.
- [x] Run the page tests and perform one synthetic browser check with a mocked API: verify emoji context, literal HTML-like text, absent cues, edited-status labeling and unchanged positions. If no browser runner is available, report that gap explicitly; static HTML checks do not establish browser behavior. Do not add a browser toolchain solely for this small feature without need.

### Task 5: Specification alignment and final verification

**Files:** Modify `docs/proposal.md` sections 3–4, 6, 8–10, 14, 16 and 18–19 where relevant; modify `AGENTS.md` scope/layout; retain the design and plan documents. Preserve proposal author attribution and existing anonymization.

- [x] Describe the text-first increment, synthetic-only inputs, manual/absent prosody, provisional model suggestions, local review and UI-only offsets in the appropriate existing proposal sections. Clarify that audio processing, persistence and research evaluation remain future work; do not add dated logs.
- [x] Replace the placeholder-only restriction with permission for the approved text model path, while retaining the audio placeholder and all privacy/approval constraints. Update documented layout only as needed.
- [x] Run `uv run --locked ruff check`, `uv run --locked mypy`, `uv run --locked pytest`, and `git diff --check`. Report actual counts and any browser/live-model validation limitations. Do not repeat successful checks unless later edits affect them.
- [x] Review all proposed changes for privacy leaks and confirm no credentials, participant data, GitHub Actions changes, dependency churn or history rewriting. Present results for review without committing or publishing.

## Self-review and handoff

The tasks cover the approved design, preserve the audio flow, and explicitly separate UI character offsets from research measures and edited text. The custom workshop skill is separate work. Recommend inline execution to minimize overhead for this small, shared-interface change. The user approved inline implementation. Tasks 1–5 are implemented; final verification results are recorded in the implementation report. No commit or publication is authorized.
