from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import zipfile


@dataclass(frozen=True)
class PackageValidationResult:
    passed: bool
    findings: tuple[str, ...]
    files: tuple[str, ...]


class WordPressPackageValidator:
    """ZIP نهایی WordPress را مستقل از Build Directory اعتبارسنجی می‌کند."""

    def validate(self, zip_path: str) -> PackageValidationResult:
        findings: list[str] = []
        files: list[str] = []
        path = Path(zip_path)
        if not path.exists() or not path.is_file():
            return PackageValidationResult(False, ("missing:zip",), ())
        if not zipfile.is_zipfile(path):
            return PackageValidationResult(False, ("invalid:zip",), ())

        with zipfile.ZipFile(path) as archive:
            files = archive.namelist()
            normalized = {name.rstrip("/") for name in files}
            if not any(name.endswith("/style.css") or name == "style.css" for name in normalized):
                findings.append("missing:theme-style")
            if not any(name.endswith("/functions.php") or name == "functions.php" for name in normalized):
                findings.append("missing:theme-functions")

            for name in files:
                if not name.lower().endswith(".php"):
                    continue
                text = archive.read(name).decode("utf-8", errors="replace")
                if "eval(" in text or "shell_exec(" in text or "exec(" in text:
                    findings.append(f"unsafe-code:{name}")

        return PackageValidationResult(not findings, tuple(findings), tuple(files))
