# Fast Lark Publishing Design

## Goal

Publish project-onboarding documents quickly enough for a newcomer workflow. The publishing stage is a delivery operation, not an audit-grade remote consistency check.

## Publishing model

Local validation remains the content-quality gate. After `local` and `lark-ready` validation pass, publishing trusts successful Feishu write responses.

The workflow must:

1. Reuse node and document tokens from an existing receipt when available.
2. Query Wiki nodes at most once when tokens are missing or invalid.
3. Publish the eight fixed nodes with bounded concurrency of four.
4. Import Mermaid diagrams as part of the document write instead of issuing separate Whiteboard update or export calls.
5. Inspect only the document write response: command success, warnings, degradation codes, returned Whiteboard blocks, document token, URL, and revision.
6. Retry a transient network or rate-limit failure at most once. Content, permission, or compatibility errors are not retried.
7. Build and validate a lightweight receipt locally after all write calls finish.

The workflow must not:

- fetch a document before overwriting it;
- fetch document content after a successful write;
- poll document revisions;
- export or read back Whiteboards;
- compare remote Markdown hashes with local Markdown;
- perform a second remote verification after receipt creation;
- upload the same node repeatedly in an attempt to make verification pass.

## Receipt schema v4

The receipt is a delivery record based on write responses, not a remote-readback attestation.

Global fields:

- `schema_version`: `4`
- `verification_level`: `write-response`
- `space_id`: non-empty string
- `published_at`: non-empty string
- `remote_readback_performed`: `false`
- `duplicate_titles`: empty list
- `write_ok`: `true`
- `whiteboard_import_ok`: `true`

Each of the eight nodes records:

- fixed `title`, `source_file`, and `publish_file`;
- local `source_sha256` and `publish_sha256`;
- `obj_token`, `url`, and non-negative integer `revision_id` from the write response;
- local `paragraph_count` and `diagram_count`;
- `whiteboard_count` derived from returned Whiteboard blocks;
- `degrade_codes`, which must be empty;
- `warnings`, which must be empty;
- `write_ok`, which must be `true`;
- `whiteboard_import_ok`, which is true only when the returned Whiteboard count equals the local Mermaid count and there are no warnings or degradation codes.

The receipt does not contain `remote_content_sha256`, `remote_readback_ok`, or readback revision fields.

## Failure behavior

- If a node write fails, preserve successful node results and report the failed title.
- Retry only transient network and rate-limit failures, once, using the same idempotency token where supported.
- Do not retry authorization, invalid content, non-zero degradation, warning, or Whiteboard-count mismatch failures.
- Do not claim complete publication unless all eight write responses satisfy schema v4.

## Performance and reporting

The expected first-run remote work is zero or one Wiki lookup plus eight document writes in two waves of at most four. No remote calls are made by receipt validation.

The completion report states that success is based on Feishu write responses and that full remote content readback was intentionally skipped for speed. It reports the write-call count, retry count, elapsed publish time, and failed node titles if any.

## Testing

- Schema v3 receipts fail validation.
- A valid schema v4 receipt passes.
- Readback-only fields are rejected or ignored according to a single explicit policy: reject them to prevent misleading audit claims.
- Missing/invalid revision, warning, degradation, write status, and Whiteboard-count fields fail.
- Local source and publish hashes remain deterministic and required.
- Existing local and `lark-ready` validation tests remain green.
- Skill and publishing references contain no mandatory post-write fetch, revision polling, Whiteboard export, or remote content hash comparison.
