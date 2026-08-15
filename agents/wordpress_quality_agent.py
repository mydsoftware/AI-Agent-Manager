from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class WordPressQualityResult:
    passed: bool
    findings: tuple[str, ...]


class WordPressQualityAgent:
    """اعتبارسنجی ساختار Theme و Plugin خروجی WordPress قبل از تحویل."""

    def validate(self, root: str) -> WordPressQualityResult:
        base = Path(root)
        findings: list[str] = []
        required = ("style.css", "functions.php", "front-page.php", "header.php", "footer.php")
        for name in required:
            if not (base / name).exists():
                findings.append(f"missing:{name}")

        if (base / "style.css").exists():
            css = (base / "style.css").read_text(encoding="utf-8", errors="replace")
            if not re.search(r"Theme Name\s*:", css, re.I):
                findings.append("theme-header:style.css")

        php_files = list(base.rglob("*.php")) if base.exists() else []
        for path in php_files:
            text = path.read_text(encoding="utf-8", errors="replace")
            if not re.search(r"<\?php", text):
                findings.append(f"php-header:{path.relative_to(base)}")
            if re.search(r"\b(eval|exec|shell_exec|system|passthru)\s*\(", text):
                findings.append(f"unsafe-code:{path.relative_to(base)}")

        plugin_root = base / "wp-content" / "plugins"
        if plugin_root.exists():
            for plugin_file in plugin_root.rglob("*.php"):
                text = plugin_file.read_text(encoding="utf-8", errors="replace")
                if not re.search(r"Plugin Name\s*:", text, re.I):
                    findings.append(f"plugin-header:{plugin_file.relative_to(base)}")

        return WordPressQualityResult(not findings, tuple(findings))
