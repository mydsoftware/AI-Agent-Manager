from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import zipfile

from agents.wordpress_factory_agent import WordPressFactoryAgent
from agents.wordpress_requirements_agent import WordPressRequirementsAgent
from agents.wordpress_theme_builder import WordPressThemeBuilder
from agents.wordpress_plugin_builder import WordPressPluginBuilder
from agents.wordpress_package_validator import WordPressPackageValidator, PackageValidationResult
from manager.wordpress_build_executor import WordPressBuildExecutor, WordPressBuildResult
from manager.wordpress_quality_loop import WordPressQualityLoop


@dataclass(frozen=True)
class WordPressFactoryResult:
    passed: bool
    plan: object
    requirements: object
    build: WordPressBuildResult
    quality_attempts: int
    findings: tuple[str, ...]
    plugins_created: tuple[str, ...]
    package: PackageValidationResult


class WordPressFactoryPipeline:
    """Request → Requirements → Build → Quality/Repair → Package → Final Validation."""

    def __init__(self, max_quality_attempts: int = 3) -> None:
        self.requirements = WordPressRequirementsAgent()
        self.factory = WordPressFactoryAgent()
        self.builder = WordPressBuildExecutor()
        self.theme_builder = WordPressThemeBuilder()
        self.plugin_builder = WordPressPluginBuilder()
        self.quality = WordPressQualityLoop(max_quality_attempts)
        self.package_validator = WordPressPackageValidator()

    def _package(self, root: Path, zip_path: Path) -> None:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in root.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(root.parent))

    def run(self, request: str, output_dir: str) -> WordPressFactoryResult:
        requirements = self.requirements.analyze(request)
        plan = self.factory.plan(request)
        build = self.builder.execute(plan, output_dir)
        self.theme_builder.build(requirements, build.root)
        plugins = self.plugin_builder.build(
            requirements, str(Path(build.root) / "wp-content" / "plugins")
        )

        quality = self.quality.run(build.root)
        package = PackageValidationResult(False, ("not-built",), ())
        if quality.passed:
            self._package(Path(build.root), Path(build.zip_path))
            package = self.package_validator.validate(build.zip_path)

        passed = quality.passed and package.passed
        findings = quality.quality.findings + package.findings
        return WordPressFactoryResult(
            passed,
            plan,
            requirements,
            build,
            quality.attempts,
            findings,
            plugins,
            package,
        )
