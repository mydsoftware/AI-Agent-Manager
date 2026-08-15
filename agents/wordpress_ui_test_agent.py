from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import zipfile


@dataclass(frozen=True)
class WordPressUITestResult:
    passed: bool
    checks: tuple[str, ...]
    findings: tuple[str, ...]


class WordPressUITestAgent:
    """بدون مرورگر واقعی، خروجی Template را برای عناصر پایه UI و navigation بررسی می‌کند."""

    def run(self, package_path: str) -> WordPressUITestResult:
        checks: list[str] = []
        findings: list[str] = []
        path = Path(package_path)
        if not path.exists() or not zipfile.is_zipfile(path):
            return WordPressUITestResult(False, (), ("invalid:package",))

        with zipfile.ZipFile(path) as archive:
            files = archive.namelist()
            php_files = [name for name in files if name.endswith(".php")]
            html = "\n".join(archive.read(name).decode("utf-8", errors="replace") for name in php_files)

            if re.search(r"<nav\b", html, re.I):
                checks.append("navigation-present")
            else:
                findings.append("missing:navigation")

            if re.search(r"<main\b", html, re.I):
                checks.append("main-present")
            else:
                findings.append("missing:main")

            if re.search(r"<meta[^>]+viewport", html, re.I):
                checks.append("responsive-viewport")
            else:
                findings.append("missing:viewport")

            if re.search(r"<h1\b", html, re.I):
                checks.append("heading-present")
            else:
                findings.append("missing:h1")

        return WordPressUITestResult(not findings, tuple(checks), tuple(findings))
