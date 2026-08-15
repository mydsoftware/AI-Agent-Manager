from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import zipfile


@dataclass(frozen=True)
class WordPressPerformanceTestResult:
    passed: bool
    checks: tuple[str, ...]
    findings: tuple[str, ...]
    metrics: dict[str, int]


class WordPressPerformanceTestAgent:
    """Lightweight package-size and asset-count checks; not a Core Web Vitals measurement."""

    def __init__(self, max_package_bytes: int = 10_000_000, max_assets: int = 120) -> None:
        self.max_package_bytes = max_package_bytes
        self.max_assets = max_assets

    def run(self, package_path: str) -> WordPressPerformanceTestResult:
        path = Path(package_path)
        if not path.exists() or not zipfile.is_zipfile(path):
            return WordPressPerformanceTestResult(False, (), ("invalid:package",), {})
        checks = ["package-readable"]
        findings: list[str] = []
        with zipfile.ZipFile(path) as archive:
            entries = [n for n in archive.namelist() if not n.endswith("/")]
            assets = [n for n in entries if Path(n).suffix.lower() in {".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".woff", ".woff2"}]
            total_uncompressed = sum(info.file_size for info in archive.infolist())
            if total_uncompressed > self.max_package_bytes:
                findings.append(f"package-too-large:{total_uncompressed}")
            else:
                checks.append("package-size")
            if len(assets) > self.max_assets:
                findings.append(f"too-many-assets:{len(assets)}")
            else:
                checks.append("asset-count")
        return WordPressPerformanceTestResult(
            not findings, tuple(checks), tuple(findings),
            {"files": len(entries), "assets": len(assets), "uncompressed_bytes": total_uncompressed},
        )
