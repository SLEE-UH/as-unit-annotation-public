# Instructions for coding agents

This project is an Automatic AS-unit Annotation Application for linguists and speech researchers. It will transcribe spontaneous English speech and suggest AS-unit boundaries informed by transcript and prosody. The complete, authoritative project proposal is in `docs/proposal.md`; do not substitute a generic speech-to-text proposal.

## Layout
- `app/main.py`: FastAPI routes, page delivery, request/response handling. Keep business rules out of this file.
- `app/page.html`: UI modeled on the upload, transcript/AS-unit review, and result download areas in the proposal.
- `app/agent.py`: future Pydantic AI model and structured output definitions; no live model calls in the skeleton.
- `app/rules.py`: plain Python rules, without FastAPI or LLM imports.
- `tests/`: tests for the skeleton and later rules.

## Commands
```bash
uv run fastapi dev app/main.py
uv run ruff check
uv run mypy
uv run pytest
```

## Rules
- Workshop skeleton first: page/form/endpoint and a fixed placeholder response only. No transcription, audio analysis, LLM calls, persistent storage, or account features yet.
- Tests must not make real model requests or incur API charges. Later use Pydantic AI `TestModel` with `override_allow_model_requests(False)` where relevant.
- Read `LLM_API_TOKEN` and `LLM_API_GATEWAY` only from the environment when needed. Never put secrets in source files or commit `.env`.
- Do not use actual human-participant research recordings. Project audio must be self-recorded and nonsensitive as the proposal specifies.
- Do not store original uploaded audio as a persistent record; the proposal limits retained records to transcript, prosody and annotations.
- Run `uv run ruff check`, `uv run mypy`, and `uv run pytest` after changes and report actual outcomes. Do not report success if any check failed.
- Do not weaken checks merely to pass: no increasing complexity limits, no blanket ignores, and no skipped tests without a justified reason.
- Use the proposal's actual rules and acceptance criteria; do not invent stricter requirements.
## Changes

- Never commit to main. Make each change on its own branch and open a pull request with gh pr create. The description has a ## Summary (what changed and why, citing docs/proposal.md) and a ## Test plan checklist (checked items were run; unchecked items are left for the reviewer).
- After pushing, run gh pr checks --watch and report the result.
- Never merge a pull request. The person merges after reviewing it.