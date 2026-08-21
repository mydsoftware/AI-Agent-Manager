from __future__ import annotations

from dataclasses import dataclass

from agents.seo_action_policy import SeoActionPolicyAnalyzer
from agents.seo_health import SeoHealthAnalyzer
from agents.seo_priority import SeoPriorityAnalyzer
from agents.public_site_scanner import PageObservation


@dataclass(frozen=True)
class SeoExecutionResult:
    """نتیجه تصمیم‌گیری موتور اجرای SEO."""
    url: str
    issue: str
    mode: str
    executed: bool
    message: str


class SeoExecutionEngine:
    """موتور ایمن اجرای اقدامات SEO؛ فقط اقدامات صریحاً خودکار را اجرا می‌کند."""

    def __init__(self) -> None:
        self.health = SeoHealthAnalyzer()
        self.priority = SeoPriorityAnalyzer()
        self.policy = SeoActionPolicyAnalyzer()

    def plan(self, observations: list[PageObservation]) -> tuple[SeoExecutionResult, ...]:
        """برنامه اجرا را بدون تغییر در سایت تولید می‌کند."""
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
                        message="برای اجرای واقعی این اقدام ابتدا باید اتصال/Writer امن سایت فراهم شود. در حالت Audit هیچ تغییری اعمال نمی‌شود.",
                    )
                )
        return tuple(result)

    def execute(self, observations: list[PageObservation], apply: bool = False) -> tuple[SeoExecutionResult, ...]:
        """اقدامات را فقط در صورت فعال‌بودن صریح apply و وجود Writer اجرا می‌کند."""
        plan = self.plan(observations)
        if not apply:
            return plan
        # فعلاً Writer عمومی سایت عمداً پیاده‌سازی نشده تا Audit هرگز ناخواسته سایت را تغییر ندهد.
        return tuple(
            SeoExecutionResult(item.url, item.issue, item.mode, False,
                               "اجرای واقعی هنوز به Writer امن متصل نشده است؛ هیچ تغییری اعمال نشد.")
            for item in plan
        )
