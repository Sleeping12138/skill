# Newcomer-Friendly Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Make every published Feishu onboarding node understandable to an experienced developer who is new to the project by requiring a plain-language summary and evidence-backed real project examples.

**Architecture:** Keep marker-rich Markdown as the validation source, extend the validator with deterministic newcomer-summary/example parsing and coverage checks, and strip only the new markers in the existing publish projection. Upgrade newcomer review references so every answer points to reader-visible content in a validated node.

**Tech Stack:** Python 3.8+ standard library, Markdown control markers, `unittest`, existing Feishu publish projection and receipt validation.

## Global Constraints

- Target readers have software-development experience but no prior project or business-domain knowledge.
- Preserve technical facts, evidence, diagrams, risks, and deep-dive detail.
- Use project-specific scenarios; never invent generic business stories to satisfy validation.
- Every example contains 场景、发生了什么、结果、先查哪里 and adjacent repository evidence.
- Keep `docs/onboarding/lark/` as validation sources and `docs/onboarding/.lark-publish/` as the only upload projection.
- Use Python standard library only and retain Python 3.8 compatibility.

---

### Task 1: Newcomer Summary and Example Validation

**Files:**
- Modify: `tests/test_validate_onboarding.py`
- Modify: `scripts/validate_onboarding.py`

**Interfaces:**
- Produces: `validate_newcomer_summary(markdown: str, label: str, result: ValidationResult) -> None`
- Produces: `validate_newcomer_examples(markdown: str, label: str, result: ValidationResult) -> List[str]`
- Consumes: existing `paragraph_is_effective`, `validate_evidence_lines`, profile `core_flows` and `subsystems`.

- [x] Add fixture helpers that generate one 60–180 CJK-character `<!-- newcomer-summary -->` paragraph and structured `<!-- newcomer-example: id -->` units with four labeled fields and an adjacent evidence line.
- [x] Add failing tests for missing, duplicate, too-short, and too-long summaries.
- [x] Add failing tests for invalid/duplicate example ids, missing fields, short/duplicated fields, missing adjacent evidence, and nonexistent evidence paths.
- [x] Run the focused tests and confirm failures name the missing newcomer contract.
- [x] Add summary/example regexes and validation functions. Count CJK characters for summary bounds; require exactly one of each example field; reuse existing effective-paragraph and evidence-path checks.
- [x] Validate `ARCHITECTURE_DEEP_DIVE.md` in local mode and return example ids for downstream coverage checks.
- [x] Run focused tests and confirm they pass.

### Task 2: Node and Profile Coverage

**Files:**
- Modify: `tests/test_validate_onboarding.py`
- Modify: `scripts/validate_onboarding.py`

**Interfaces:**
- Consumes: Task 1 `validate_newcomer_examples` returned ids.
- Produces: deterministic coverage errors containing node title and missing flow/subsystem id.

- [x] Add failing tests proving nodes 00, 03, and 05 require at least one example.
- [x] Add failing tests proving every profile `core_flow.id` occurs in node 02 and every `subsystems.id` occurs in nodes 01 and 07.
- [x] Run focused tests and confirm failures are caused by missing coverage logic.
- [x] Extend `validate_lark_node` to return example ids and enforce fixed-node minimums.
- [x] Pass profile into `validate_lark_ready`; enforce flow/subsystem coverage by exact id while allowing the same id in different files.
- [x] Enforce subsystem coverage in architecture deep dive during local validation.
- [x] Run focused tests and existing service/CLI/library/monorepo contract tests.

### Task 3: Publish Projection and Newcomer Review References

**Files:**
- Modify: `tests/test_validate_onboarding.py`
- Modify: `scripts/lark_publish.py`
- Modify: `scripts/validate_onboarding.py`

**Interfaces:**
- Extends: `sanitize_lark_markdown(markdown: str) -> str`
- Changes: newcomer review to `schema_version=2` with `source_refs: List[str]` formatted as `<node title>#summary` or `<node title>#example:<id>`.

- [x] Add a failing projection test showing `newcomer-summary` and `newcomer-example` markers are removed while their following paragraphs remain.
- [x] Add failing newcomer-review tests for missing, malformed, nonexistent, and node-mismatched `source_refs`.
- [x] Run focused tests and confirm failures.
- [x] Extend the publish sanitizer/control-marker detector for both new markers.
- [x] Build the available reference set from all eight validation sources and require every review question to cite at least one valid reader-visible reference.
- [x] Keep `source_nodes` for node-level reporting and require its set to match the titles encoded by `source_refs`.
- [x] Run focused tests and publish projection/receipt regressions.

### Task 4: Skill Guidance and Full Verification

**Files:**
- Modify: `SKILL.md`
- Modify: `references/output-contract.md`
- Modify: `references/lark-publishing.md`
- Modify: `references/architecture-guide.md`
- Test: `tests/test_validate_onboarding.py`

**Interfaces:**
- Documents the exact marker formats, reader-first order, project-specific example requirements, review schema v2, and sanitization behavior implemented in Tasks 1–3.

- [x] Update test fixtures for every supported repository kind so valid artifacts use plain summaries and project-specific examples rather than generic technical prose.
- [x] Update `SKILL.md` Phase 2, Phase 3, and Phase 3.6 instructions to require “30 秒看懂 → 真实例子 → 实际机制 → 代码证据 → 开发/排障”.
- [x] Add the summary/example contract and one complete example to `references/output-contract.md`; keep detailed validation rules there rather than duplicating them in `SKILL.md`.
- [x] Update `references/lark-publishing.md` with node coverage, review schema v2, and the new markers removed by publish preparation.
- [x] Update `references/architecture-guide.md` so diagram explanations start from a concrete reader question and connect diagrams to the relevant example.
- [x] Run `python3 -m unittest discover -s tests -v` and require zero failures.
- [x] Run `python3 -m py_compile scripts/lark_publish.py scripts/prepare_lark_publish.py scripts/validate_onboarding.py tests/test_validate_onboarding.py`.
- [x] Run `git diff --check`, inspect all changed files, and remove generated `__pycache__` files.
