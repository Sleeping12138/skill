import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_onboarding.py"
PREPARER = SKILL_ROOT / "scripts" / "prepare_lark_publish.py"
CODEBASE_DOCS = (
    "STACK.md",
    "STRUCTURE.md",
    "ARCHITECTURE.md",
    "CONVENTIONS.md",
    "INTEGRATIONS.md",
    "TESTING.md",
    "CONCERNS.md",
)
LARK_TITLES = (
    "00 技术栈",
    "01 代码结构",
    "02 系统架构",
    "03 开发规范",
    "04 外部集成",
    "05 测试指南",
    "06 风险与关注",
    "07 架构深读",
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


def write_text(root: Path, relative: str, content: str = "fixture\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validator_env() -> dict:
    env = dict(os.environ)
    env["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin"
    return env


def run_validator(root: Path, mode: str, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--repo-root",
            str(root),
            "--mode",
            mode,
            "--format",
            "json",
            *extra,
        ],
        text=True,
        capture_output=True,
        check=False,
        env=validator_env(),
    )


def run_preparer(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PREPARER), "--repo-root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )


def mermaid() -> str:
    return """```mermaid
flowchart LR
    A[\"入口\"] --> B[\"结果\"]
```
"""


def create_local_artifacts(root: Path) -> None:
    for name in CODEBASE_DOCS:
        write_text(root, "docs/codebase/" + name, "# {}\n\n项目事实摘要。\n".format(name))
    write_text(
        root,
        "docs/onboarding/ARCHITECTURE_DEEP_DIVE.md",
        "# 架构深读\n\n这份文档保留完整架构事实。\n\n" + mermaid(),
    )


def lark_markdown(title: str, with_diagram: bool = False) -> str:
    body = "# {}\n\n这是面向新人的精炼说明，只保留主要职责、关键入口和下一步阅读方向。\n".format(title)
    if with_diagram:
        body += "\n<!-- diagram-context: before -->\n从入口沿箭头看到结果。\n\n" + mermaid()
    return body


def create_lark_artifacts(root: Path, diagrams=(2, 7)) -> None:
    for index, (title, filename) in enumerate(zip(LARK_TITLES, LARK_FILES)):
        write_text(
            root,
            "docs/onboarding/lark/" + filename,
            lark_markdown(title, with_diagram=index in diagrams),
        )
    completed = run_preparer(root)
    if completed.returncode:
        raise AssertionError(completed.stdout + completed.stderr)


class FastValidatorTests(unittest.TestCase):
    def test_local_accepts_eight_nonempty_detailed_sources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            completed = run_validator(root, "local")
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_local_requires_each_detailed_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            (root / "docs/codebase/TESTING.md").unlink()
            completed = run_validator(root, "local")
            self.assertEqual(completed.returncode, 1)
            self.assertIn("TESTING.md is missing", completed.stdout)

    def test_unclosed_mermaid_fence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            write_text(root, "docs/codebase/STACK.md", "# Stack\n\n```mermaid\nflowchart LR\nA --> B\n")
            completed = run_validator(root, "local")
            self.assertEqual(completed.returncode, 1)
            self.assertIn("unclosed Mermaid fence", completed.stdout)

    def test_state_diagram_fails_feishu_compatibility(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            write_text(root, "docs/codebase/ARCHITECTURE.md", "```mermaid\nstateDiagram-v2\nA --> B\n```\n")
            completed = run_validator(root, "local")
            self.assertEqual(completed.returncode, 1)
            self.assertIn("uses stateDiagram-v2", completed.stdout)

    def test_secret_is_rejected_without_echoing_value(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            secret = "super-sensitive-value"
            write_text(root, "docs/codebase/INTEGRATIONS.md", "API_KEY={}\n".format(secret))
            completed = run_validator(root, "local")
            self.assertEqual(completed.returncode, 1)
            self.assertIn("secret-like assignment", completed.stdout)
            self.assertNotIn(secret, completed.stdout + completed.stderr)

    def test_lark_ready_accepts_concise_docs_without_length_or_diagram_quota(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            create_lark_artifacts(root, diagrams=())
            write_text(root, "docs/onboarding/lark/00-stack.md", "# 技术栈\n\n精炼。\n")
            self.assertEqual(run_preparer(root).returncode, 0)
            completed = run_validator(root, "lark-ready")
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_lark_ready_requires_all_sources_and_projections(self) -> None:
        for relative in (
            "docs/onboarding/lark/03-conventions.md",
            "docs/onboarding/.lark-publish/05-testing.md",
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                create_local_artifacts(root)
                create_lark_artifacts(root)
                (root / relative).unlink()
                completed = run_validator(root, "lark-ready")
                self.assertEqual(completed.returncode, 1)
                self.assertIn("is missing", completed.stdout)

    def test_lark_ready_rejects_stale_projection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            create_lark_artifacts(root)
            write_text(root, "docs/onboarding/.lark-publish/01-structure.md", "# 旧内容\n")
            completed = run_validator(root, "lark-ready")
            self.assertEqual(completed.returncode, 1)
            self.assertIn("projection is stale", completed.stdout)

    def test_lark_source_rejects_state_diagram(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            create_lark_artifacts(root)
            write_text(root, "docs/onboarding/lark/02-architecture.md", "```mermaid\nstateDiagram-v2\nA --> B\n```\n")
            self.assertEqual(run_preparer(root).returncode, 0)
            completed = run_validator(root, "lark-ready")
            self.assertEqual(completed.returncode, 1)
            self.assertIn("uses stateDiagram-v2", completed.stdout)

    def test_preparer_removes_only_control_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            create_lark_artifacts(root)
            source = """# 技术栈

<!-- diagram-context: before -->
这是用户需要看到的读图提示。

```mermaid
%% onboarding-diagram: core-component
flowchart LR
    A --> B
```

<!-- keep-this-human-comment -->
"""
            write_text(root, "docs/onboarding/lark/00-stack.md", source)
            completed = run_preparer(root)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            published = (root / "docs/onboarding/.lark-publish/00-stack.md").read_text(encoding="utf-8")
            self.assertNotIn("diagram-context", published)
            self.assertNotIn("%% onboarding-", published)
            self.assertIn("这是用户需要看到的读图提示。", published)
            self.assertIn("<!-- keep-this-human-comment -->", published)
            self.assertIn("flowchart LR", published)

    def test_publish_mode_does_not_require_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            create_lark_artifacts(root)
            completed = run_validator(root, "publish")
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_receipt_is_not_a_publish_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_local_artifacts(root)
            create_lark_artifacts(root)
            write_text(root, "receipt.json", "{not valid json")
            completed = run_validator(root, "publish", "--publish-receipt", "receipt.json")
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
