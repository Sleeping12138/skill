# Remove `mmdc` Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure project-onboarding validation never launches `mmdc` or Chromium while preserving deterministic Mermaid and Feishu Whiteboard validation.

**Architecture:** Delete the optional renderer from the local validator instead of caching it. Keep structural Mermaid validation in every local mode and retain Feishu import/receipt validation as the publish-time compatibility authority.

**Tech Stack:** Python 3.8+ standard library, `unittest`, Markdown Skill instructions.

## Global Constraints

- Never discover or execute `mmdc`.
- Keep Feishu-safe root validation for `flowchart`, `graph`, and `sequenceDiagram`.
- Keep `stateDiagram` and `stateDiagram-v2` as hard failures.
- Keep publish receipt and Whiteboard count/degradation validation unchanged.
- Do not perform Git operations.

---

### Task 1: Remove Mermaid CLI execution

**Files:**
- Modify: `tests/test_validate_onboarding.py`
- Modify: `scripts/validate_onboarding.py`

**Interfaces:**
- Consumes: existing validator CLI and `validate_feishu_mermaid_compatibility()`.
- Produces: validator behavior that never invokes an executable named `mmdc`.

- [x] **Step 1: Replace the renderer test with a failing non-execution test**

Create a fake `mmdc` that writes a sentinel file and exits non-zero, run local validation with that binary at the front of `PATH`, assert validation succeeds, the sentinel does not exist, and output contains no `mmdc` text.

- [x] **Step 2: Run the focused test and verify RED**

Run: `python3 -m unittest tests.test_validate_onboarding.OnboardingValidatorTests.test_detected_mmdc_is_not_executed`

Expected: FAIL because the current validator invokes the fake executable.

- [x] **Step 3: Delete renderer implementation**

Remove `shutil`, `subprocess`, and `tempfile` imports from `scripts/validate_onboarding.py`, delete `render_mermaid_if_available()`, and delete its call from `validate_markdown()`.

- [x] **Step 4: Run focused test and Mermaid compatibility tests**

Run the non-execution test and existing `stateDiagram-v2` regression tests. Expected: PASS.

### Task 2: Align the Skill contract and documentation

**Files:**
- Modify: `SKILL.md`
- Modify: `references/architecture-guide.md`

**Interfaces:**
- Consumes: the validator behavior from Task 1.
- Produces: instructions that never request or report `mmdc`.

- [x] **Step 1: Remove all `mmdc` requirements**

State that validation is structural and deterministic, and that Feishu Whiteboard import is the final publish compatibility check.

- [x] **Step 2: Search for stale references**

Run: `rg -n "mmdc|Mermaid CLI|Chromium" SKILL.md references scripts tests`

Expected: only the regression test proving non-execution may mention `mmdc`; no production instruction or implementation reference remains.

### Task 3: Complete regression verification

**Files:**
- Verify: `scripts/validate_onboarding.py`
- Verify: `tests/test_validate_onboarding.py`

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: fresh evidence that the complete Skill test suite remains green.

- [x] **Step 1: Run the full suite**

Run: `python3 -m unittest discover -s tests`

Expected: all tests pass.

- [x] **Step 2: Compile Python sources**

Run: `python3 -m py_compile scripts/validate_onboarding.py scripts/lark_publish.py scripts/prepare_lark_publish.py tests/test_validate_onboarding.py`

Expected: exit code 0.

- [x] **Step 3: Check patch formatting and clean generated caches**

Run `git diff --check` only as a read-only formatting check, then remove only the generated `__pycache__/*.pyc` files after listing their exact paths.
