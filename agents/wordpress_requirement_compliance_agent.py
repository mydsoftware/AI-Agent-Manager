from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import zipfile


@dataclass(frozen=True)
class WordPressRequirementComplianceResult:
    passed: bool
    checks: tuple[str, ...]
    findings: tuple[str, ...]


class WordPressRequirementComplianceAgent:
    """Checks whether requested features have recognizable implementation evidence."""

    KEYWORDS = {
        "satellite": ("satellite", "ماهواره"),
        "contact-form": ("form", "contact", "تماس", "مشاوره"),
        "woocommerce": ("woocommerce", "محصول", "فروشگاه"),
        "blog": ("blog", "وبلاگ", "post"),
    }

    def run(self, request: str, package_path: str) -> WordPressRequirementComplianceResult:
        path = Path(package_path)
        if not path.exists() or not zipfile.is_zipfile(path):
            return WordPressRequirementComplianceResult(False, (), ("invalid:package",))
        text = request.lower()
        checks: list[str] = []
        findings: list[str] = []
        with zipfile.ZipFile(path) as archive:
            names = " ".join(archive.namelist()).lower()
            php = "\n".join(
                archive.read(n).decode("utf-8", errors="replace")
                for n in archive.namelist() if n.lower().endswith((".php", ".css", ".js", ".html"))
            ).lower()
            evidence = names + " " + php
            for feature, keywords in self.KEYWORDS.items():
                requested = any(k in text for k in keywords)
                if not requested:
                    continue
                if any(k in evidence for k in keywords):
                    checks.append(f"requirement:{feature}")
                else:
                    findings.append(f"missing:requirement:{feature}")
        return WordPressRequirementComplianceResult(not findings, tuple(checks), tuple(findings))
