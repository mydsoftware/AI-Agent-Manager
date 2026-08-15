from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from agents.wordpress_package_validator import PackageValidationResult


@dataclass(frozen=True)
class WordPressDeliveryResult:
    delivered: bool
    package_path: str
    manifest_path: str
    manifest: dict[str, object]


class WordPressDeliveryAgent:
    """پس از PASS، بسته و Manifest قابل تحویل WordPress تولید می‌کند."""

    def deliver(
        self,
        package_path: str,
        validation: PackageValidationResult,
        project_name: str,
        output_dir: str,
    ) -> WordPressDeliveryResult:
        if not validation.passed:
            raise ValueError("Package validation باید PASS باشد.")
        source = Path(package_path)
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        final_package = destination / source.name
        if source.resolve() != final_package.resolve():
            final_package.write_bytes(source.read_bytes())

        manifest = {
            "project": project_name,
            "package": final_package.name,
            "files": list(validation.files),
            "validation": "PASS",
            "installation": [
                "WordPress Admin → Plugins → Add New → Upload Plugin برای ZIP افزونه در صورت نیاز",
                "ZIP قالب را در Appearance → Themes → Add New → Upload Theme نصب کنید.",
                "Theme را فعال کنید.",
            ],
        }
        manifest_path = destination / "delivery-manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return WordPressDeliveryResult(True, str(final_package), str(manifest_path), manifest)
