# Fast Lark Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace audit-grade post-publish readback with a fast write-response receipt and reduce the first publish to at most one Wiki lookup plus eight bounded-concurrent document writes.

**Architecture:** Keep `local` and `lark-ready` as the content gates. Make Phase 4 a delivery-only workflow that trusts successful Feishu document-write responses, then validate a schema v4 local receipt without making remote calls.

**Tech Stack:** Python 3.8+ standard library, `unittest`, Lark CLI workflow instructions, Markdown.

## Global Constraints

- Publish at most four independent nodes concurrently.
- Do not fetch documents before or after successful writes.
- Do not poll revisions, export Whiteboards, or compare remote content hashes.
- Retry transient network or rate-limit failures at most once; do not retry content, permission, warning, degradation, or count failures.
- Preserve local source/publish hash checks and Feishu write-response warning/degradation/count checks.
- Do not perform Git operations.

---

### Task 1: Define schema v4 receipt behavior with failing tests

**Files:**
- Modify: `tests/test_validate_onboarding.py`

**Interfaces:**
- Consumes: `valid_receipt(root: Path) -> dict` and the validator publish CLI.
- Produces: schema v4 fixture and regression tests for fast write-response validation.

- [x] **Step 1: Update the valid receipt fixture**

Set global fields to `schema_version=4`, `verification_level="write-response"`, `remote_readback_performed=false`, `write_ok=true`, and keep `whiteboard_import_ok=true`. For every node add `revision_id=1`, `warnings=[]`, and `write_ok=true`; remove `remote_content_sha256`, `remote_readback_ok`, `intro_present`, and `next_step_present`.

- [x] **Step 2: Replace schema v3 audit-field tests**

Add failing cases for schema v3, incorrect verification level, `remote_readback_performed=true`, global/node `write_ok=false`, invalid revision, non-empty warnings, non-empty degradation codes, Whiteboard count mismatch, and forbidden readback fields.

- [x] **Step 3: Run focused receipt tests and verify RED**

Run: `python3 -m unittest tests.test_validate_onboarding.ValidatorCliTests.test_valid_publish_receipt_passes tests.test_validate_onboarding.ValidatorCliTests.test_invalid_publish_receipt_fails`

Expected: FAIL because production validation still requires schema v3 and readback hashes.

### Task 2: Implement schema v4 receipt validation

**Files:**
- Modify: `scripts/validate_onboarding.py`
- Test: `tests/test_validate_onboarding.py`

**Interfaces:**
- Consumes: receipt JSON from `--publish-receipt`.
- Produces: `validate_publish_receipt(receipt, root, result)` enforcing write-response schema v4 without remote-readback fields.

- [x] **Step 1: Change global validation**

Require schema 4, verification level `write-response`, `remote_readback_performed is False`, `write_ok is True`, empty duplicate titles, and global Whiteboard success. Reject global `remote_readback_ok`.

- [x] **Step 2: Change node validation**

Require `obj_token`, `url`, source/publish paths and hashes; validate non-negative non-boolean `revision_id`; require `write_ok=true`, `warnings=[]`, `degrade_codes=[]`, and matching diagram/Whiteboard counts. Reject `remote_content_sha256`, `remote_readback_ok`, and readback revision fields. Remove intro/next-step receipt checks because they are already enforced by `lark-ready`.

- [x] **Step 3: Run focused tests and verify GREEN**

Run the two focused receipt tests. Expected: PASS.

### Task 3: Replace the publishing workflow with the fast path

**Files:**
- Modify: `SKILL.md`
- Modify: `references/lark-publishing.md`

**Interfaces:**
- Consumes: eight validated files in `docs/onboarding/.lark-publish/` and optional schema v4 receipt tokens.
- Produces: eight Feishu write responses and `docs/onboarding/.lark-publish-receipt.json` schema v4.

- [x] **Step 1: Rewrite Phase 4**

Specify token reuse, at most one Wiki lookup, four-way bounded concurrency, embedded Mermaid import, write-response inspection, one transient retry, and schema v4 receipt creation.

- [x] **Step 2: Delete audit-grade steps**

Remove mandatory pre-write fetch, post-write fetch, revision polling, Whiteboard export/update, remote Markdown hashes, and second remote verification language.

- [x] **Step 3: Align completion reporting**

Report write call count, retry count, elapsed publish time, failures, and the explicit statement that full remote content readback was skipped for speed.

- [x] **Step 4: Search for stale production requirements**

Run: `rg -n "schema v3|schema_version=3|remote_content_sha256|remote_readback_ok|发布后回读|逐图导入|逐图核验|回读正文" SKILL.md references scripts`

Expected: no schema v3 or mandatory remote-readback requirement remains in production workflow or validator.

### Task 4: Complete regression verification

**Files:**
- Verify: `scripts/validate_onboarding.py`
- Verify: `tests/test_validate_onboarding.py`
- Verify: `SKILL.md`
- Verify: `references/lark-publishing.md`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: fresh evidence that fast publishing preserves all local validation behavior.

- [x] **Step 1: Run the full suite**

Run: `python3 -m unittest discover -s tests`

Expected: all tests pass.

- [x] **Step 2: Compile Python sources**

Run: `python3 -m py_compile scripts/validate_onboarding.py scripts/lark_publish.py scripts/prepare_lark_publish.py tests/test_validate_onboarding.py`

Expected: exit code 0.

- [x] **Step 3: Check formatting and clean caches**

Run `git diff --check` only as a read-only formatting check. List exact generated `__pycache__/*.pyc` files and remove only those files.
