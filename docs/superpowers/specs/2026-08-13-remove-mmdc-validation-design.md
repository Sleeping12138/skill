# Remove `mmdc` Validation Design

## Problem

The onboarding workflow runs the validator in `local`, `lark-ready`, and `publish` modes. When `mmdc` is available, the validator launches a separate Mermaid CLI/Chromium process for every diagram during every run. A complex repository can therefore start Chromium dozens of times before and after publishing, making validation take tens of minutes.

## Decision

Remove `mmdc` detection and rendering from `validate_onboarding.py` completely. The workflow must never launch Mermaid CLI or Chromium.

Keep the deterministic Markdown checks that do not require rendering:

- Mermaid fences must be parseable by the existing block parser.
- Every diagram must have the required onboarding type and flow/subsystem markers.
- Only Feishu-safe root directives are allowed: `flowchart`, `graph`, and `sequenceDiagram`.
- `stateDiagram` and `stateDiagram-v2` remain hard failures with the `degrade_code=2107` explanation.
- Diagram density and profile coverage remain hard requirements.

For publish mode, Feishu Whiteboard import is the authoritative compatibility test. Every imported diagram must return no warning or non-zero degradation code, and the imported Whiteboard count must equal the source diagram count. Receipt validation remains unchanged.

## User-visible behavior

- No `mmdc` installation check, warning, success message, or rendering step.
- Completion reports describe deterministic Mermaid checks and Feishu Whiteboard results; they no longer report `mmdc` status.
- `local` mode is faster but cannot guarantee that a diagram renders in arbitrary Mermaid renderers. It guarantees only the documented Feishu-safe structural subset.

## Testing

- Replace the test that expects detected `mmdc` to run with a test proving an executable named `mmdc` is never invoked.
- Keep regression tests for unsupported roots and `stateDiagram-v2`.
- Run the complete unit-test suite and Python compilation checks.
