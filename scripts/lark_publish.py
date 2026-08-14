#!/usr/bin/env python3
"""Build reader-facing Lark Markdown from marker-rich onboarding sources."""

import re
from pathlib import Path
from typing import List


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
SOURCE_DIRECTORY = Path("docs/onboarding/lark")
PUBLISH_DIRECTORY = Path("docs/onboarding/.lark-publish")
HTML_CONTROL_MARKER_RE = re.compile(
    r"^\s*<!--\s*(?:"
    r"explanation:\s*[a-z-]+|"
    r"diagram-context:\s*(?:before|after)|"
    r"reading-stage:\s*[a-z0-9-]+|"
    r"term:\s*[a-z0-9-]+|"
    r"lark-node:\s*(?:intro|next-step)|"
    r"newcomer-summary|"
    r"newcomer-example:\s*[a-z0-9-]+"
    r")\s*-->\s*$",
    re.IGNORECASE,
)
MERMAID_CONTROL_MARKER_RE = re.compile(
    r"^\s*%%\s*onboarding-(?:diagram|flow-id|subsystem-id):\s*[^\s]+\s*$",
    re.IGNORECASE,
)


def sanitize_lark_markdown(markdown: str) -> str:
    """Remove only onboarding control markers, preserving reader content."""
    lines: List[str] = []
    in_mermaid = False
    normalized = markdown.replace("\r\n", "\n").replace("\r", "\n")
    for line in normalized.split("\n"):
        stripped = line.strip()
        if stripped.lower() == "```mermaid":
            in_mermaid = True
            lines.append(line)
        elif in_mermaid and stripped == "```":
            in_mermaid = False
            lines.append(line)
        elif HTML_CONTROL_MARKER_RE.fullmatch(line):
            continue
        elif in_mermaid and MERMAID_CONTROL_MARKER_RE.fullmatch(line):
            continue
        else:
            lines.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def contains_lark_control_markers(markdown: str) -> bool:
    in_mermaid = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.lower() == "```mermaid":
            in_mermaid = True
        elif in_mermaid and stripped == "```":
            in_mermaid = False
        elif HTML_CONTROL_MARKER_RE.fullmatch(line):
            return True
        elif in_mermaid and MERMAID_CONTROL_MARKER_RE.fullmatch(line):
            return True
    return False


def prepare_lark_publish_files(repo_root: Path) -> List[Path]:
    source_root = repo_root / SOURCE_DIRECTORY
    publish_root = repo_root / PUBLISH_DIRECTORY
    missing = [filename for filename in LARK_FILES if not (source_root / filename).is_file()]
    if missing:
        raise FileNotFoundError("missing Lark source files: {}".format(", ".join(missing)))
    publish_root.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for filename in LARK_FILES:
        source = source_root / filename
        destination = publish_root / filename
        markdown = source.read_text(encoding="utf-8")
        destination.write_text(sanitize_lark_markdown(markdown), encoding="utf-8")
        written.append(destination)
    return written
