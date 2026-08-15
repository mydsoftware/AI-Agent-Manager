from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WordPressRepairResult:
    changed: bool
    files_fixed: tuple[str, ...]


class WordPressRepairAgent:
    """Findingهای WordPress Quality را به اصلاحات محدود و قابل تکرار تبدیل می‌کند."""

    def repair(self, root: str, findings: tuple[str, ...]) -> WordPressRepairResult:
        base = Path(root)
        fixed: list[str] = []

        for finding in findings:
            if not finding.startswith("missing:"):
                continue
            name = finding.split(":", 1)[1]
            target = base / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if name == "style.css":
                content = "/* Theme Name: AI Manager Generated Theme */\n"
            elif name.endswith(".php"):
                content = "<?php\nif (!defined('ABSPATH')) exit;\n"
            else:
                content = ""
            target.write_text(content, encoding="utf-8")
            fixed.append(name)

        return WordPressRepairResult(bool(fixed), tuple(fixed))
