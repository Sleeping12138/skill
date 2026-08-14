# Ultrafast Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace repeated editorial and model-based validation with one lightweight pre-publish safety pass.

**Architecture:** Route the validator through small fast-path functions that check required files, profile JSON, secrets, Feishu-safe Mermaid, Lark summaries, and clean projection freshness. Remove newcomer review and strict editorial checks from the default workflow; keep publish mode compatible but receipt-optional and unused by the Skill.

**Tech Stack:** Python 3.8+ standard library, `unittest`, Markdown Skill instructions.

## Global Constraints

- Publish mode runs exactly one `lark-ready` validation before remote writes.
- Local mode runs exactly one `local` validation.
- No newcomer seven-question review or `.newcomer-review.json`.
- No post-publish validation command in the default workflow.
- Keep secret, unsafe Mermaid, required-file, summary, sanitizer, and projection-freshness failures.
- Do not perform Git operations.

---

### Task 1: Define the ultrafast validator behavior

**Files:**
- Modify: `tests/test_validate_onboarding.py`

**Interfaces:**
- Consumes: validator `local`, `lark-ready`, and `publish` modes.
- Produces: regression tests proving removed editorial constraints no longer block and essential safety checks still fail.

- [ ] **Step 1: Add relaxed behavior tests**

Add tests that remove `.newcomer-review.json`, remove explanation/example/term/reading markers, reduce diagram counts, and use a short but non-empty summary; expect `lark-ready` to pass. Add a test that publish mode passes without a receipt.

- [ ] **Step 2: Keep essential failure tests**

Retain tests for missing/empty summaries, missing Lark files, stale projections, leaked markers, secrets, unclosed Mermaid fences, and unsupported `stateDiagram-v2` roots.

- [ ] **Step 3: Run the new focused tests and verify RED**

Run the relaxed behavior, no-review, and receipt-optional tests. Expected: FAIL because the existing validator still enforces strict editorial rules and receipt presence.

### Task 2: Implement a lightweight validation entry path

**Files:**
- Modify: `scripts/validate_onboarding.py`
- Test: `tests/test_validate_onboarding.py`

**Interfaces:**
- Produces: `validate_fast_local(root, profile, guide, deep_dive, result)` and `validate_fast_lark_ready(root, result)`.

- [ ] **Step 1: Implement fast local checks**

Require the seven baseline files, profile, guide, and deep-dive; parse profile schema 1; parse Mermaid blocks and enforce Feishu-safe roots; scan baseline/guide/deep-dive text for secrets.

- [ ] **Step 2: Implement fast Lark checks**

Require all eight Lark sources and projections; require exactly one summary marker with non-empty visible content; scan Lark sources for secrets; require each projection to equal `sanitize_lark_markdown(source)` and contain no machine markers.

- [ ] **Step 3: Simplify mode routing**

Use fast local checks for every mode, add fast Lark checks for `lark-ready` and `publish`, and validate a receipt only when `--publish-receipt` is explicitly supplied. Do not require newcomer review.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the new focused tests plus essential safety tests. Expected: PASS.

### Task 3: Remove obsolete strict tests and workflow requirements

**Files:**
- Modify: `tests/test_validate_onboarding.py`
- Modify: `SKILL.md`
- Modify: `references/output-contract.md`
- Modify: `references/lark-publishing.md`
- Modify: `references/architecture-guide.md`

**Interfaces:**
- Consumes: the fast validator behavior from Task 2.
- Produces: one validation command per workflow and no model review/post-publish gate.

- [ ] **Step 1: Delete strict test cases**

Delete tests whose only purpose is enforcing bounded prose length, structured example lengths, fixed example coverage, profile evidence, diagram quotas, explanation slots, term markers, reading stages, conditional sections, newcomer review, and mandatory receipt validation.

- [ ] **Step 2: Rewrite the Skill phase sequence**

For publish/update, skip Phase 3.5 and run `lark-ready` once after projection preparation. Remove `.newcomer-review.json`, Phase 4.5, and the publish validation command. For local mode, keep one `local` command.

- [ ] **Step 3: Downgrade editorial rules to authoring guidance**

Keep plain-language summaries, examples, diagrams, evidence, terminology, and reading paths as writing recommendations, explicitly state they are not hard validation metrics, and remove repair-loop language.

- [ ] **Step 4: Simplify completion reporting**

Require only artifact paths, eight links or failed titles, total publish duration, and the note that strict editorial review and remote readback were skipped for speed.

### Task 4: Verify the reduced workflow

**Files:**
- Verify: `scripts/validate_onboarding.py`
- Verify: `tests/test_validate_onboarding.py`
- Verify: `SKILL.md`
- Verify: `references/*.md`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: fresh regression evidence for the ultrafast workflow.

- [ ] **Step 1: Search for stale hard gates**

Run targeted `rg` searches for newcomer review, Phase 4.5, mandatory publish receipt, three validation commands, strict diagram density, and explanation-slot hard failures.

- [ ] **Step 2: Run the complete test suite**

Run: `python3 -m unittest discover -s tests`

Expected: all remaining tests pass.

- [ ] **Step 3: Compile and format-check**

Run Python compilation and `git diff --check`, then list and remove only generated `__pycache__/*.pyc` files.
