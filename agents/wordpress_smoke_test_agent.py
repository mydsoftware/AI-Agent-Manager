from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import zipfile


@dataclass(frozen=True)
class WordPressSmokeTestResult:
    passed: bool
    checks: tuple[str, ...]
    findings: tuple[str, ...]


class WordPressSmokeTestAgent:
    """نصب فرضی را بدون نیاز به سایت زنده شبیه‌سازی و فایل‌های قابل‌اجرا را بررسی می‌کند."""

    def run(self, package_path: str) -> WordPressSmokeTestResult:
        checks: list[str] = []
        findings: list[str] = []
        path = Path(package_path)
        if not path.exists() or not zipfile.is_zipfile(path):
            return WordPressSmokeTestResult(False, (), ("invalid:package",))

        with zipfile.ZipFile(path) as archive:
            files = archive.namelist()
            php = [name for name in files if name.lower().endswith(".php")]
            checks.append("package-readable")
            if not any(name.endswith("style.css") for name in files):
                findings.append("missing:style.css")
            else:
                checks.append("theme-style-present")
            if not any(name.endswith("functions.php") for name in files):
                findings.append("missing:functions.php")
            else:
                checks.append("theme-functions-present")
            for name in php:
                text = archive.read(name).decode("utf-8", errors="replace")
                if not re.search(r"<\?php", text):
                    findings.append(f"invalid-php:{name}")
                if "get_header(" in text and not "get_footer(" in text:
                    findings.append(f"template-incomplete:{name}")
            if php:
                checks.append("php-files-readable")

        return WordPressSmokeTestResult(not findings, tuple(checks), tuple(findings))
