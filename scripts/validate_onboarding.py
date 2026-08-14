#!/usr/bin/env python3
"""Run the fast, deterministic checks needed before onboarding publication."""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from lark_publish import PUBLISH_DIRECTORY, contains_lark_control_markers, sanitize_lark_markdown


DETAILED_SOURCE_FILES = (
    "docs/codebase/STACK.md",
    "docs/codebase/STRUCTURE.md",
    "docs/codebase/ARCHITECTURE.md",
    "docs/codebase/CONVENTIONS.md",
    "docs/codebase/INTEGRATIONS.md",
    "docs/codebase/TESTING.md",
    "docs/codebase/CONCERNS.md",
    "docs/onboarding/ARCHITECTURE_DEEP_DIVE.md",
)
LARK_FILES = (
    "00-stack.md",
    "01-structure.md",
    "02-architecture.md",
    "03-conventions.md",
    "04-integrations.md",
    "05-testing.md",
    "06-concerns.md",
    "07-architecture-deep-dive.md",
)
FEISHU_MERMAID_ROOTS = {"flowchart", "graph", "sequencediagram"}
PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}")
CREDENTIAL_URL_RE = re.compile(r"https?://[^\s/:@]+:[^\s/@]+@", re.IGNORECASE)
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b[A-Z0-9_]*(?:API[_-]?KEY|ACCESS[_-]?TOKEN|TOKEN|SECRET|PASSWORD|PASSWD)[A-Z0-9_]*"
    r"\s*[:=]\s*([^\s#;,]+)"
)
PLACEHOLDER_VALUES = {
    "",
    "changeme",
    "example",
    "placeholder",
    "redacted",
    "replace_me",
    "todo",
    "unknown",
    "xxx",
    "your_value_here",
}


@dataclass
class ValidationResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)

    def check(self, message: str) -> None:
        self.checks.append(message)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "checks": self.checks,
        }


def require_nonempty_file(path: Path, label: str, result: ValidationResult) -> bool:
    if not path.is_file():
        result.error("{} is missing: {}".format(label, path))
        return False
    if path.stat().st_size == 0:
        result.error("{} is empty: {}".format(label, path))
        return False
    result.check("{} exists and is non-empty".format(label))
    return True


def read_text(path: Path, label: str, result: ValidationResult) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        result.error("could not read {}: {}".format(label, exc))
        return None


def parse_mermaid_blocks(markdown: str, label: str, result: ValidationResult) -> List[Tuple[int, str]]:
    blocks: List[Tuple[int, str]] = []
    start_line: Optional[int] = None
    lines: List[str] = []
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        stripped = line.strip()
        if start_line is None and stripped.lower() == "```mermaid":
            start_line = line_number
            lines = []
        elif start_line is not None and stripped == "```":
            blocks.append((start_line, "\n".join(lines)))
            start_line = None
            lines = []
        elif start_line is not None:
            lines.append(line)
    if start_line is not None:
        result.error("{} has an unclosed Mermaid fence starting at line {}".format(label, start_line))
    return blocks


def mermaid_root(block: str) -> str:
    for line in block.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("%%"):
            return stripped.split()[0]
    return ""


def validate_mermaid(blocks: List[Tuple[int, str]], label: str, result: ValidationResult) -> None:
    for index, (line_number, block) in enumerate(blocks, start=1):
        root = mermaid_root(block)
        normalized = root.lower()
        if normalized in {"statediagram", "statediagram-v2"}:
            result.error(
                "{} Mermaid block {} at line {} uses {}; rewrite it as flowchart "
                "because Feishu Whiteboard may return degrade_code=2107".format(
                    label, index, line_number, root
                )
            )
        elif normalized not in FEISHU_MERMAID_ROOTS:
            result.error(
                "{} Mermaid block {} at line {} uses unsupported root {}; use flowchart, graph, "
                "or sequenceDiagram".format(label, index, line_number, root or "<empty>")
            )


def is_placeholder(value: str) -> bool:
    normalized = value.strip().strip("'\"").lower()
    return (
        normalized in PLACEHOLDER_VALUES
        or normalized.startswith("${")
        or normalized.startswith("<") and normalized.endswith(">")
        or normalized.startswith("your_")
    )


def scan_secrets(text: str, label: str, result: ValidationResult) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if PRIVATE_KEY_RE.search(line):
            result.error("{} contains a private key marker at line {}".format(label, line_number))
        if BEARER_RE.search(line):
            result.error("{} contains a Bearer credential at line {}".format(label, line_number))
        if CREDENTIAL_URL_RE.search(line):
            result.error("{} contains a credential-bearing URL at line {}".format(label, line_number))
        assignment = SECRET_ASSIGNMENT_RE.search(line)
        if assignment is not None and not is_placeholder(assignment.group(1)):
            result.error("{} contains a secret-like assignment at line {}".format(label, line_number))


def validate_markdown_file(path: Path, label: str, result: ValidationResult) -> Optional[str]:
    if not require_nonempty_file(path, label, result):
        return None
    markdown = read_text(path, label, result)
    if markdown is None:
        return None
    validate_mermaid(parse_mermaid_blocks(markdown, label, result), label, result)
    scan_secrets(markdown, label, result)
    return markdown


def validate_local(root: Path, result: ValidationResult) -> None:
    for relative in DETAILED_SOURCE_FILES:
        validate_markdown_file(root / relative, relative, result)


def validate_lark_ready(root: Path, result: ValidationResult) -> None:
    source_root = root / "docs" / "onboarding" / "lark"
    publish_root = root / PUBLISH_DIRECTORY
    for filename in LARK_FILES:
        source_label = "Lark source {}".format(filename)
        publish_label = "Lark publish projection {}".format(filename)
        markdown = validate_markdown_file(source_root / filename, source_label, result)
        publish_path = publish_root / filename
        if not require_nonempty_file(publish_path, publish_label, result):
            continue
        published = read_text(publish_path, publish_label, result)
        if markdown is None or published is None:
            continue
        scan_secrets(published, publish_label, result)
        if published != sanitize_lark_markdown(markdown):
            result.error("Lark publish projection is stale for {}".format(filename))
        if contains_lark_control_markers(published):
            result.error("Lark publish projection contains machine control markers: {}".format(filename))


def validate(args: argparse.Namespace) -> ValidationResult:
    result = ValidationResult()
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        result.error("repository root is not a directory: {}".format(root))
        return result
    validate_local(root, result)
    if args.mode in {"lark-ready", "publish"}:
        validate_lark_ready(root, result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--mode", choices=("local", "lark-ready", "publish"), required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    # Accepted for backward compatibility; these inputs no longer trigger expensive validation.
    parser.add_argument("--profile", help=argparse.SUPPRESS)
    parser.add_argument("--guide", help=argparse.SUPPRESS)
    parser.add_argument("--deep-dive", help=argparse.SUPPRESS)
    parser.add_argument("--publish-receipt", help=argparse.SUPPRESS)
    return parser


def render_text(result: ValidationResult) -> str:
    lines = ["PASS" if result.ok else "FAIL"]
    lines.extend("CHECK: {}".format(message) for message in result.checks)
    lines.extend("ERROR: {}".format(message) for message in result.errors)
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate(args)
    if args.format == "json":
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
