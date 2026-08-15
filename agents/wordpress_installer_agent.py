from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class WordPressInstallerResult:
    prepared: bool
    install_script_path: str
    instructions_path: str


class WordPressInstallerAgent:
    """برای Package تأییدشده، بسته نصب و دستورالعمل Deployment تولید می‌کند."""

    def prepare(self, package_path: str, output_dir: str) -> WordPressInstallerResult:
        source = Path(package_path)
        if not source.exists():
            raise FileNotFoundError(package_path)

        target = Path(output_dir)
        target.mkdir(parents=True, exist_ok=True)

        script = target / "install-wordpress.sh"
        script.write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\n\n"
            "PACKAGE=\"${1:-site.zip}\"\n"
            "echo \"WordPress package ready: ${PACKAGE}\"\n"
            "echo \"Upload the package through WordPress Admin or your deployment system.\"\n",
            encoding="utf-8",
        )

        instructions = target / "installation.json"
        instructions.write_text(json.dumps({
            "package": source.name,
            "steps": [
                "Backup the existing WordPress installation.",
                "Upload and extract the generated package.",
                "Activate the generated theme.",
                "Activate generated plugins if present.",
                "Run the final WordPress smoke tests.",
            ],
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        return WordPressInstallerResult(True, str(script), str(instructions))
