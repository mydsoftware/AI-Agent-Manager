from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class WordPressQualityResult:
    passed: bool
    findings: tuple[str, ...]


class WordPressQualityAgent:
    """خروجی واقعی WordPress را قبل از تحویل اعتبارسنجی می‌کند."""

    def validate(self, root: str) -> WordPressQualityResult:
        base = Path(root)
        findings: list[str] = []
        required = ("style.css", "functions.php", "front-page.php", "header.php", "footer.php")
        for name in required:
            if not (base / name).exists():
                findings.append(f"missing:{name}")

        php_files = list(base.rglob("*.php")) if base.exists() else []
        for path in php_files:
            text = path.read_text(encoding="utf-8", errors="replace")
            if not re.search(r"<\?php", text):
                findings.append(f"php-header:{path.name}")
            if "eval(" in text or "exec(" in text:
                findings.append(f"unsafe-code:{path.name}")

        return WordPressQualityResult(not findings, tuple(findings))
