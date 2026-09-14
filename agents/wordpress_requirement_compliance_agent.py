from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
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

    TEXT_EXTENSIONS = {".php", ".css", ".js", ".html", ".htm", ".md", ".txt", ".json", ".xml"}

    def run(self, request: str, package_path: str) -> WordPressRequirementComplianceResult:
        path = Path(package_path)
        if not path.exists() or not zipfile.is_zipfile(path):
            return WordPressRequirementComplianceResult(False, (), ("invalid:package",))

        text = request.lower()
        checks: list[str] = []
        findings: list[str] = []
        with zipfile.ZipFile(path) as archive:
            names = " ".join(archive.namelist()).lower()
            contents: list[str] = []
            for name in archive.namelist():
                if Path(name).suffix.lower() not in self.TEXT_EXTENSIONS:
                    continue
                contents.append(archive.read(name).decode("utf-8", errors="replace"))

            evidence = names + " " + "\n".join(contents).lower()
            for feature, keywords in self.KEYWORDS.items():
                requested = any(k in text for k in keywords)
                if not requested:
                    continue
                if any(k in evidence for k in keywords):
                    checks.append(f"requirement:{feature}")
                else:
                    findings.append(f"missing:requirement:{feature}")
            if contents:
                checks.append("text-evidence-scanned")

        return WordPressRequirementComplianceResult(not findings, tuple(checks), tuple(findings))
