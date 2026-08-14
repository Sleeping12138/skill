#!/usr/bin/env python3
"""Generate clean reader-facing Markdown files for Lark publication."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from lark_publish import PUBLISH_DIRECTORY, prepare_lark_publish_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        print("repository root is not a directory: {}".format(root), file=sys.stderr)
        return 1
    try:
        written = prepare_lark_publish_files(root)
    except (OSError, UnicodeError) as exc:
        print("could not prepare Lark publish files: {}".format(exc), file=sys.stderr)
        return 1
    relative = [str(path.relative_to(root)) for path in written]
    if args.format == "json":
        print(json.dumps({"ok": True, "output_dir": str(PUBLISH_DIRECTORY), "files": relative}, ensure_ascii=False))
    else:
        print("prepared {} clean Lark publish files in {}".format(len(relative), PUBLISH_DIRECTORY))
    return 0


if __name__ == "__main__":
    sys.exit(main())
