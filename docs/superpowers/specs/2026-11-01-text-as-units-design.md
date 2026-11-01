# AI AS-unit suggestions from text

Approved design, including the user's offset and editing clarifications.

## Goal and scope
Accept synthetic English text and optional manually supplied prosodic cues in the web interface. Use an actual configured AI model to suggest AS-units, display segmentation and original boundary positions, and allow browser-local review edits. Preserve the existing audio form and POST /analyze placeholder behavior.

No RAG, database, persistence, audio transcription, model training, research participant data, or live model calls in automated tests. Do not log input text, cues, model responses, credentials, or raw provider errors.

## Approaches and trade-offs
The user chose text-based AS-unit suggestions over synthetic-audio transcription and AI-assisted review of pre-existing annotations. This delivers a small complete UI-to-model integration without an audio pipeline. Return text segments rather than trusting model-generated character counts; validate exact reconstruction, then calculate offsets on the server. Keep edits browser-local rather than adding persistence or a second model request.

## Behavior
Require a nonblank transcript of at most 5,000 Unicode code points. Optional cues are manually supplied evidence; absent cues are explicitly marked not supplied, never inferred. Use text-based independent-clause/subclausal-unit and associated-subordinate-clause criteria, with supplied cues as supporting evidence. These are provisional suggestions for human review, not validated research annotations. Treat input as data, not instructions.

Use Pydantic AI and the existing OpenAI-compatible dependency. Read LLM_API_TOKEN, LLM_API_GATEWAY and LLM_MODEL on the server only. No default credentials or silent model selection. One retry is allowed for invalid structured output; do not automatically retry provider/network failures. Validate nonempty segments whose concatenation exactly equals the original transcript, including whitespace and punctuation.

Boundary positions are zero-based, end-exclusive Unicode code-point offsets for internal segment ends; omit the final transcript end. They are UI positions only, not the word-level positions used in research evaluation. Show both the rendered segmentation and positions with context. JavaScript must handle Unicode consistently with Python.

The review textarea holds editable segmented text. Original AI boundary positions remain unchanged after edits and must be clearly labeled as such. There is no recalculation, persistence, or download. Missing configuration, timeouts, provider failures, and invalid output produce safe user-facing messages without sensitive details.

## Structure and verification
Routes stay in app/main.py; model schemas, provider configuration and calls in app/agent.py; pure text validation and offset derivation in app/rules.py; browser interaction in app/page.html. Existing application code and tests remain functional.

Automated tests use synthetic inputs, mocked model responses, and disabled real model requests. Cover missing cues, exact reconstruction, Unicode offsets, input limits, safe failures, UI labels and the unchanged audio endpoint. Run Ruff, mypy, pytest and a synthetic browser check. A live model demonstration is a separate, authorized operation requiring secure configuration.
