# Concise Eight-Document Lark Design

## Goal

Keep the complete outputs from the two repository-analysis skills while publishing eight concise, newcomer-facing summaries to Feishu. A reader should understand what the project is and where its main parts live without reading the detailed local research.

## Detailed source artifacts

Preserve these eight detailed local files as the factual source of truth:

1. `docs/codebase/STACK.md`
2. `docs/codebase/STRUCTURE.md`
3. `docs/codebase/ARCHITECTURE.md`
4. `docs/codebase/CONVENTIONS.md`
5. `docs/codebase/INTEGRATIONS.md`
6. `docs/codebase/TESTING.md`
7. `docs/codebase/CONCERNS.md`
8. `docs/onboarding/ARCHITECTURE_DEEP_DIVE.md`

Do not require `PROJECT_GUIDE.md` or `.onboarding-profile.json`.

## Concise Lark artifacts

Generate one concise derivative for each detailed source:

| Detailed source | Lark title | Lark source file |
|---|---|---|
| `STACK.md` | `00 技术栈` | `docs/onboarding/lark/00-stack.md` |
| `STRUCTURE.md` | `01 代码结构` | `docs/onboarding/lark/01-structure.md` |
| `ARCHITECTURE.md` | `02 系统架构` | `docs/onboarding/lark/02-architecture.md` |
| `CONVENTIONS.md` | `03 开发规范` | `docs/onboarding/lark/03-conventions.md` |
| `INTEGRATIONS.md` | `04 外部集成` | `docs/onboarding/lark/04-integrations.md` |
| `TESTING.md` | `05 测试指南` | `docs/onboarding/lark/05-testing.md` |
| `CONCERNS.md` | `06 风险与关注` | `docs/onboarding/lark/06-concerns.md` |
| `ARCHITECTURE_DEEP_DIVE.md` | `07 架构深读` | `docs/onboarding/lark/07-architecture-deep-dive.md` |

Each derivative is a summary, not a comprehensive rewrite. It should explain what the topic means for a newcomer, list three to five important takeaways, and point to no more than a few useful code locations. Roughly 300–500 Chinese characters per document is authoring guidance only and is never validated.

Flowcharts and sequence diagrams may be retained when they make the project easier to understand. Prefer a small number of simple diagrams, but diagram count is authoring guidance only and is never validated. Mermaid roots remain limited to `flowchart`, `graph`, and `sequenceDiagram` for Feishu compatibility.

## Removed artifacts and work

- Do not generate `PROJECT_GUIDE.md`.
- Do not generate `.onboarding-profile.json`.
- Do not generate `.newcomer-review.json` or perform the newcomer seven-question review.
- Do not enforce explanation slots, terminology markers, reading stages, example schemas, evidence density, prose length, or diagram quantity.
- Do not run separate `local`, `lark-ready`, and `publish` validation passes in one publish workflow.
- Do not run post-publish remote readback or a receipt hard gate.

## Single validation pass

Local mode runs one lightweight validation after the eight detailed files exist. Publish/update mode generates the eight concise Lark sources and clean projections, then runs one lightweight validation before publishing.

The validation checks only:

- all eight detailed source files exist and are non-empty;
- all eight concise Lark sources and clean projections exist and are non-empty in publish/update mode;
- Mermaid blocks use Feishu-safe roots and have closed fences;
- generated Markdown does not contain secret-like values;
- clean projections exactly equal the deterministic sanitizer output;
- clean projections contain no machine control markers.

It does not validate document length or total diagram count.

## Publishing

Publish the eight clean projections using the existing four-way bounded-concurrency write-response workflow. The schema v4 receipt is a best-effort link and write-result record, not a completion gate. Do not run a second validator after remote writes.

The final report contains the eight local detailed paths, eight Feishu links or failed titles, total publish duration, and a short note that strict editorial review and remote readback were skipped for speed.
