# Ultrafast Validation Design

## Goal

Optimize project-onboarding for fast newcomer documentation. Validation protects only publication safety and basic readability; it must not perform model-based review or enforce editorial completeness through repeated rewrite loops.

## Root cause

The Python receipt check takes roughly one tenth of a second. The material cost comes from generating the newcomer seven-question review, rereading all eight Lark documents to produce source references, running overlapping `local`, `lark-ready`, and `publish` gates, repairing documents against detailed editorial metrics, and recounting the same content for the completion report.

## Workflow

### Local mode

Generate local artifacts and run one lightweight `local` validation command.

### Publish and update modes

Do not run the Phase 3.5 `local` gate. Generate all local and Lark artifacts, prepare the clean projections, and run one lightweight `lark-ready` validation command. If it passes, publish using the fast write-response workflow. Do not run a post-publish validator.

## Removed work

- Remove `docs/onboarding/.newcomer-review.json` from the artifact contract.
- Remove the newcomer seven-question model review and all `source_refs` generation and validation.
- Remove Phase 4.5 and the post-publish `--mode publish` command from the Skill workflow.
- Keep the schema v4 receipt only as a best-effort record of links and write results; it is not a hard gate.
- Remove completion-report requirements that force the model to recount paragraphs, diagrams, question results, check counts, or warnings after validation.
- Remove hard validation for explanation slots, minimum paragraph lengths, term markers, reading-stage markers, diagram-density quotas, evidence-line coverage, newcomer-example field lengths, and profile flow/subsystem example coverage.

## One lightweight validation pass

The remaining validation checks only:

- the required profile, guide, deep-dive, and seven baseline files exist and are non-empty;
- the profile JSON parses and uses a supported schema version;
- project guide and deep-dive contain only Feishu-safe Mermaid roots and reject `stateDiagram` / `stateDiagram-v2`;
- local Markdown does not contain secret-like values;
- in `lark-ready` mode, all eight fixed Lark source files and clean projections exist and are non-empty;
- each Lark source has exactly one `newcomer-summary` marker followed by non-empty visible text;
- each clean projection is the deterministic sanitizer output and contains no machine control markers.

The validator does not judge prose quality, completeness, evidence density, terminology, example coverage, or diagram quantity. Those are authoring guidance, not publication blockers.

## Publishing result

Publishing still checks each Feishu write response for command success. Warnings, degradation codes, and returned Whiteboard counts are recorded when available, but receipt validation is not run and receipt incompleteness does not trigger rewriting or re-uploading.

The final report includes only local artifact paths, eight Feishu links or failed titles, total publish duration, and a concise note that full remote readback and strict editorial review were skipped for speed.

## Compatibility

Keep the existing validator CLI modes for compatibility, but make `publish` perform the same lightweight local checks as `lark-ready` plus optional receipt parsing only when explicitly invoked outside the default workflow. The default Skill never invokes `--mode publish`.

## Testing

- Existing tests for removed editorial constraints are deleted or rewritten to assert they no longer block validation.
- Secret scanning, unsafe Mermaid roots, missing required files, stale clean projections, leaked machine markers, and missing/empty newcomer summaries remain hard failures.
- A valid `local` fixture and a valid `lark-ready` fixture pass.
- The complete test suite and Python compilation pass.
