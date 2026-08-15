from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class WordPressLocalRuntimeResult:
    prepared: bool
    mode: str
    url: str | None
    command: tuple[str, ...] | None
    findings: tuple[str, ...]


class WordPressLocalRuntimeAgent:
    """Runtime سبک برای سرو فایل‌های خروجی جهت تست Browser؛ بدون ادعای نصب کامل WordPress."""

    def prepare(self, root: str, port: int = 8765) -> WordPressLocalRuntimeResult:
        base = Path(root)
        if not base.exists() or not base.is_dir():
            return WordPressLocalRuntimeResult(False, "none", None, None, ("missing:root",))
        python = shutil.which("python") or shutil.which("python3")
        if not python:
            return WordPressLocalRuntimeResult(False, "none", None, None, ("missing:python",))
        command = (python, "-m", "http.server", str(port), "--directory", str(base))
        return WordPressLocalRuntimeResult(True, "static-runtime", f"http://127.0.0.1:{port}", command, ())
