from __future__ import annotations

from dataclasses import dataclass

from agents.public_site_scanner import PageObservation
from agents.seo_action_policy import SeoActionPolicyAnalyzer
from agents.seo_health import SeoHealthAnalyzer
from agents.seo_priority import SeoPriorityAnalyzer
from agents.site_writer import DryRunSiteWriter, SiteWriter


@dataclass(frozen=True)
class SeoExecutionResult:
    """نتیجه اجرای یک اقدام SEO."""
    url: str
    issue: str
    mode: str
    executed: bool
    changed: bool
    message: str


class SeoExecutionEngine:
    """موتور اجرای ایمن اقدامات SEO از طریق قرارداد SiteWriter."""

    def __init__(self, writer: SiteWriter | None = None) -> None:
        self.health = SeoHealthAnalyzer()
        self.priority = SeoPriorityAnalyzer()
        self.policy = SeoActionPolicyAnalyzer()
        self.writer = writer or DryRunSiteWriter()

    def plan(self, observations: list[PageObservation]) -> tuple[SeoExecutionResult, ...]:
        result: list[SeoExecutionResult] = []
        for page in observations:
            health = self.health.analyze(page)
            for issue in self.priority.analyze(health):
                policy = self.policy.decide(issue)
                result.append(
                    SeoExecutionResult(
                        url=page.url,
                        issue=issue.issue,
                        mode=policy.mode,
                        executed=False,
                        changed=False,
                        message="اقدام آماده اجرا است؛ در حالت Plan هیچ تغییری اعمال نمی‌شود.",
                    )
                )
        return tuple(result)

    def execute(self, observations: list[PageObservation], apply: bool = False) -> tuple[SeoExecutionResult, ...]:
        """فقط اقداماتی را اجرا می‌کند که Policy آن‌ها را خودکار اعلام کرده باشد."""
        planned = self.plan(observations)
        if not apply:
            return planned

        results: list[SeoExecutionResult] = []
        for item in planned:
            if item.mode != "قابل اصلاح خودکار":
                results.append(
                    SeoExecutionResult(item.url, item.issue, item.mode, False, False,
                                       "این اقدام خودکار نیست و بدون تأیید اجرا نشد.")
                )
                continue

            if item.issue == "Canonical وجود ندارد":
                writer_result = self.writer.set_canonical(item.url, item.url)
                results.append(
                    SeoExecutionResult(
                        item.url,
                        item.issue,
                        item.mode,
                        writer_result.success,
                        writer_result.changed,
                        writer_result.message,
                    )
                )
            else:
                results.append(
                    SeoExecutionResult(item.url, item.issue, item.mode, False, False,
                                       "برای این اقدام Writer امن هنوز پیاده‌سازی نشده است.")
                )
        return tuple(results)
