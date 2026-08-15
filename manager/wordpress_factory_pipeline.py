from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import zipfile

from agents.wordpress_factory_agent import WordPressFactoryAgent
from agents.wordpress_requirements_agent import WordPressRequirementsAgent
from agents.wordpress_theme_builder import WordPressThemeBuilder
from agents.wordpress_plugin_builder import WordPressPluginBuilder
from agents.wordpress_package_validator import WordPressPackageValidator, PackageValidationResult
from agents.wordpress_delivery_agent import WordPressDeliveryAgent, WordPressDeliveryResult
from agents.wordpress_installer_agent import WordPressInstallerAgent, WordPressInstallerResult
from agents.wordpress_smoke_test_agent import WordPressSmokeTestAgent, WordPressSmokeTestResult
from agents.wordpress_ui_test_agent import WordPressUITestAgent, WordPressUITestResult
from agents.wordpress_browser_test_agent import WordPressBrowserTestAgent, WordPressBrowserTestResult
from agents.wordpress_runtime_browser_runner import WordPressRuntimeBrowserRunner
from agents.wordpress_security_test_agent import WordPressSecurityTestAgent, WordPressSecurityTestResult
from agents.wordpress_performance_test_agent import WordPressPerformanceTestAgent, WordPressPerformanceTestResult
from agents.wordpress_requirement_compliance_agent import WordPressRequirementComplianceAgent, WordPressRequirementComplianceResult
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
    smoke_test: WordPressSmokeTestResult
    ui_test: WordPressUITestResult
    browser_test: WordPressBrowserTestResult
    security_test: WordPressSecurityTestResult
    performance_test: WordPressPerformanceTestResult
    requirement_compliance: WordPressRequirementComplianceResult
    delivery: WordPressDeliveryResult | None
    installer: WordPressInstallerResult | None


class WordPressFactoryPipeline:
    """Request → Build → QA → Package → Smoke/UI → Browser → Security/Performance/Compliance → Delivery."""

    def __init__(self, max_quality_attempts: int = 3) -> None:
        self.requirements = WordPressRequirementsAgent()
        self.factory = WordPressFactoryAgent()
        self.builder = WordPressBuildExecutor()
        self.theme_builder = WordPressThemeBuilder()
        self.plugin_builder = WordPressPluginBuilder()
        self.quality = WordPressQualityLoop(max_quality_attempts)
        self.package_validator = WordPressPackageValidator()
        self.smoke_test_agent = WordPressSmokeTestAgent()
        self.ui_test_agent = WordPressUITestAgent()
        self.browser_test_agent = WordPressBrowserTestAgent()
        self.runtime_browser_runner = WordPressRuntimeBrowserRunner()
        self.security_test_agent = WordPressSecurityTestAgent()
        self.performance_test_agent = WordPressPerformanceTestAgent()
        self.requirement_compliance_agent = WordPressRequirementComplianceAgent()
        self.delivery_agent = WordPressDeliveryAgent()
        self.installer_agent = WordPressInstallerAgent()

    def _package(self, root: Path, zip_path: Path) -> None:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in root.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(root.parent))

    def run(self, request: str, output_dir: str, browser_url: str | None = None) -> WordPressFactoryResult:
        requirements = self.requirements.analyze(request)
        plan = self.factory.plan(request)
        build = self.builder.execute(plan, output_dir)
        self.theme_builder.build(requirements, build.root)
        plugins = self.plugin_builder.build(requirements, str(Path(build.root) / "wp-content" / "plugins"))

        quality = self.quality.run(build.root)
        package = PackageValidationResult(False, ("not-built",), ())
        smoke_test = WordPressSmokeTestResult(False, (), ("not-built",))
        ui_test = WordPressUITestResult(False, (), ("not-built",))
        browser_test = WordPressBrowserTestResult(False, False, (), ("not-built",))
        security_test = WordPressSecurityTestResult(False, (), ("not-built",))
        performance_test = WordPressPerformanceTestResult(False, (), ("not-built",), {})
        requirement_compliance = WordPressRequirementComplianceResult(False, (), ("not-built",))
        delivery = None
        installer = None

        if quality.passed:
            self._package(Path(build.root), Path(build.zip_path))
            package = self.package_validator.validate(build.zip_path)
            if package.passed:
                smoke_test = self.smoke_test_agent.run(build.zip_path)
                if smoke_test.passed:
                    ui_test = self.ui_test_agent.run(build.zip_path)
                if smoke_test.passed and ui_test.passed:
                    if browser_url:
                        browser_test = self.browser_test_agent.run(browser_url)
                    else:
                        browser_test = self.runtime_browser_runner.run(build.root).browser
                if smoke_test.passed and ui_test.passed and browser_test.passed:
                    security_test = self.security_test_agent.run(build.zip_path)
                    performance_test = self.performance_test_agent.run(build.zip_path)
                    requirement_compliance = self.requirement_compliance_agent.run(request, build.zip_path)
                if (
                    smoke_test.passed and ui_test.passed and browser_test.passed
                    and security_test.passed and performance_test.passed and requirement_compliance.passed
                ):
                    delivery_dir = Path(output_dir) / "delivery"
                    delivery = self.delivery_agent.deliver(build.zip_path, package, requirements.site_title, str(delivery_dir))
                    installer = self.installer_agent.prepare(build.zip_path, str(delivery_dir))

        passed = (
            quality.passed and package.passed and smoke_test.passed and ui_test.passed
            and browser_test.passed and security_test.passed and performance_test.passed
            and requirement_compliance.passed and delivery is not None and delivery.delivered
            and installer is not None and installer.prepared
        )
        findings = (
            quality.quality.findings + package.findings + smoke_test.findings + ui_test.findings
            + browser_test.findings + security_test.findings + performance_test.findings
            + requirement_compliance.findings
        )
        return WordPressFactoryResult(
            passed, plan, requirements, build, quality.attempts, findings,
            plugins, package, smoke_test, ui_test, browser_test, security_test,
            performance_test, requirement_compliance, delivery, installer,
        )
