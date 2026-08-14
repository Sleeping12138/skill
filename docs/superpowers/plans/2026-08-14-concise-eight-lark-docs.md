# Concise Eight-Document Lark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish eight concise Feishu summaries derived directly from the eight detailed outputs of `acquire-codebase-knowledge` and `doc-and-modernize`, with one lightweight validation pass.

**Architecture:** Replace profile/guide-driven validation with a fixed source-to-Lark mapping. Keep sanitizer projections and safe Mermaid/secret checks, remove model review and editorial metrics, and leave receipt recording outside the completion gate.

**Tech Stack:** Python 3.8+ standard library, `unittest`, Markdown Skill instructions.

## Global Constraints

- Preserve seven `docs/codebase/*.md` files and `docs/onboarding/ARCHITECTURE_DEEP_DIVE.md`.
- Generate and publish eight mapped concise Lark documents.
- Document length and diagram count are guidance only, never validators.
- Run one validation pass before publishing and none afterward.
- Do not perform Git operations.

---

### Task 1: Update fixed source and Lark mappings

**Files:**
- Modify: `scripts/lark_publish.py`
- Modify: `scripts/validate_onboarding.py`
- Modify: `tests/test_validate_onboarding.py`

**Interfaces:**
- Produces: `LARK_FILES`, `LARK_TITLES`, and `DETAILED_SOURCE_FILES` with eight aligned entries.

- [ ] Replace old project-guide node names with `00-stack.md` through `07-architecture-deep-dive.md` and the approved Chinese titles.
- [ ] Update fixtures to create concise derivatives from the matching detailed source.
- [ ] Add tests proving the eight mappings are required and clean projections are generated.

### Task 2: Finish the lightweight validator

**Files:**
- Modify: `scripts/validate_onboarding.py`
- Modify: `tests/test_validate_onboarding.py`

**Interfaces:**
- Produces: local validation requiring only eight detailed files; Lark-ready validation additionally requiring eight concise sources/projections, safe Mermaid, secrets, and projection freshness.

- [ ] Remove profile, guide, and deep-dive CLI requirements; keep legacy flags optional for compatibility.
- [ ] Remove summary length and marker requirements because concise prose shape is authoring guidance.
- [ ] Keep file, Mermaid, secret, sanitizer, and marker-leak failures.
- [ ] Make publish receipt optional and unused by the default workflow.
- [ ] Delete obsolete strict tests and run focused safety tests.

### Task 3: Rewrite the Skill workflow and references

**Files:**
- Modify: `SKILL.md`
- Modify: `references/output-contract.md`
- Modify: `references/lark-publishing.md`
- Modify: `references/architecture-guide.md`

**Interfaces:**
- Produces: a two-skill/eight-source workflow, concise one-to-one Lark summaries, one pre-publish validation, and fast concurrent publishing.

- [ ] Remove profile, project guide, newcomer review, repeated validation, and post-publish gate requirements.
- [ ] Document the approved source-to-title mapping and concise summary guidance.
- [ ] Keep diagrams as optional visual aids with Feishu-safe roots; do not enforce counts.
- [ ] Reduce completion reporting to artifact paths, links/failures, duration, and skipped-review disclosure.

### Task 4: Verify the final workflow

**Files:**
- Verify: `scripts/*.py`
- Verify: `tests/test_validate_onboarding.py`
- Verify: `SKILL.md`
- Verify: `references/*.md`

**Interfaces:**
- Produces: fresh regression and syntax evidence.

- [ ] Search for stale mandatory profile, project-guide, newcomer-review, Phase 4.5, length, and diagram-count gates.
- [ ] Run `python3 -m unittest discover -s tests`.
- [ ] Run Python compilation and `git diff --check`.
- [ ] List and remove only generated `__pycache__/*.pyc` files.
