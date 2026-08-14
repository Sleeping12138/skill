# Medium-Length Lark Docs Implementation Plan

> **For agentic workers:** Execute inline; this documentation-only change does not need delegated work.

**Goal:** Increase the useful depth of the eight concise Lark onboarding documents without adding validation latency.

**Architecture:** Update the authoring contract in `SKILL.md` and `references/output-contract.md`. Keep the deterministic validator unchanged so length remains guidance rather than a hard gate.

**Tech Stack:** Markdown, Python unittest verification.

## Global Constraints

- 00–06: recommend 600–900 Chinese characters.
- 07: recommend 900–1400 Chinese characters.
- Do not add character-count, diagram-count, model-review, receipt, or remote-readback validation.
- Do not perform Git operations.

---

### Task 1: Expand the writing contract

**Files:**
- Modify: `SKILL.md`
- Modify: `references/output-contract.md`
- Modify: `references/lark-publishing.md`

- [x] Replace the old 300–500-character guidance with the approved ranges.
- [x] Require enough background, mechanism, one real example, and a next-step/troubleshooting entry.
- [x] Keep all ranges explicitly advisory.

### Task 2: Verify speed constraints remain intact

**Files:**
- Verify: `scripts/validate_onboarding.py`
- Test: `tests/test_validate_onboarding.py`

- [x] Confirm no character-count or diagram-count validation exists.
- [x] Run the complete unittest suite.
- [x] Run Python syntax and diff checks.
