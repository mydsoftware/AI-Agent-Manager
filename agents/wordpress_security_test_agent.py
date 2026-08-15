from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import zipfile


@dataclass(frozen=True)
class WordPressSecurityTestResult:
    passed: bool
    checks: tuple[str, ...]
    findings: tuple[str, ...]


class WordPressSecurityTestAgent:
    """Static security checks for generated WordPress PHP/theme/plugin packages."""

    DANGEROUS_PATTERNS = {
        "eval": r"\beval\s*\(",
        "shell-exec": r"\b(?:shell_exec|system|passthru|exec)\s*\(",
        "unsafe-include": r"\b(?:include|require)(?:_once)?\s*\([^)]*\$_(?:GET|POST|REQUEST|COOKIE)",
    }

    def run(self, package_path: str) -> WordPressSecurityTestResult:
        path = Path(package_path)
        if not path.exists() or not zipfile.is_zipfile(path):
            return WordPressSecurityTestResult(False, (), ("invalid:package",))
        checks: list[str] = ["package-readable"]
        findings: list[str] = []
        with zipfile.ZipFile(path) as archive:
            php_files = [n for n in archive.namelist() if n.lower().endswith(".php")]
            for name in php_files:
                text = archive.read(name).decode("utf-8", errors="replace")
                for label, pattern in self.DANGEROUS_PATTERNS.items():
                    if re.search(pattern, text, re.I):
                        findings.append(f"dangerous:{label}:{name}")
            checks.append("php-static-scan")
        return WordPressSecurityTestResult(not findings, tuple(checks), tuple(findings))
