from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TYPE_CHECKING

from agents.seo_action_policy import SeoActionPolicyAnalyzer
from agents.seo_health import SeoHealthAnalyzer
from agents.seo_priority import SeoPriorityAnalyzer
from agents.site_writer import DryRunSiteWriter, SiteWriter
from agents.wordpress_connection import WordPressConnectionCheck, WordPressConnectionConfig, WordPressConnectionTester

if TYPE_CHECKING:
    from agents.public_site_scanner import PageObservation

@dataclass(frozen=True)
class SeoExecutionResult:
    """نتیجه اجرای یک اقدام SEO."""
    url: str
    issue: str
    mode: str
    executed: bool
    changed: bool
    message: str

class ConnectionTester(Protocol):
    def test(self, config: WordPressConnectionConfig) -> WordPressConnectionCheck: ...

class SeoExecutionEngine:
    """موتور اجرای ایمن اقدامات SEO با بررسی اتصال قبل از Write."""
    def __init__(self, writer: SiteWriter | None = None, connection_tester: ConnectionTester | None = None) -> None:
        self.health = SeoHealthAnalyzer()
        self.priority = SeoPriorityAnalyzer()
        self.policy = SeoActionPolicyAnalyzer()
        self.writer = writer or DryRunSiteWriter()
        self.connection_tester = connection_tester or WordPressConnectionTester()

    def plan(self, observations: list[PageObservation]) -> tuple[SeoExecutionResult, ...]:
        result: list[SeoExecutionResult] = []
        for page in observations:
            health = self.health.analyze(page)
            for issue in self.priority.analyze(health):
                policy = self.policy.decide(issue)
                result.append(SeoExecutionResult(page.url, issue.issue, policy.mode, False, False, "اقدام آماده اجرا است؛ در حالت Plan هیچ تغییری اعمال نمی‌شود."))
        return tuple(result)

    def execute(self, observations: list[PageObservation], apply: bool = False, connection: WordPressConnectionConfig | None = None) -> tuple[SeoExecutionResult, ...]:
        """قبل از هر Write خودکار، اتصال WordPress را بررسی می‌کند."""
        planned = self.plan(observations)
        if not apply:
            return planned
        if connection is None:
            return tuple(SeoExecutionResult(i.url, i.issue, i.mode, False, False, "اتصال WordPress ارائه نشده است؛ اجرای Write متوقف شد.") for i in planned)
        check = self.connection_tester.test(connection)
        if not (check.reachable and check.authenticated and check.writer_endpoint_available):
            return tuple(SeoExecutionResult(i.url, i.issue, i.mode, False, False, f"اجرای Action متوقف شد: {check.message}") for i in planned)
        results: list[SeoExecutionResult] = []
        for item in planned:
            if item.mode != "قابل اصلاح خودکار":
                results.append(SeoExecutionResult(item.url, item.issue, item.mode, False, False, "این اقدام خودکار نیست و بدون تأیید اجرا نشد."))
                continue
            if item.issue == "Canonical وجود ندارد":
                writer_result = self.writer.set_canonical(item.url, item.url)
                results.append(SeoExecutionResult(item.url, item.issue, item.mode, writer_result.success, writer_result.changed, writer_result.message))
            else:
                results.append(SeoExecutionResult(item.url, item.issue, item.mode, False, False, "برای این اقدام Writer امن هنوز پیاده‌سازی نشده است."))
        return tuple(results)
