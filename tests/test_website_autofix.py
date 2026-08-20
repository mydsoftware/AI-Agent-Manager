from agents.registry import create_default_registry
from manager.task import Task
from manager.task_router import IntelligentTaskRouter
from website_audit.autofix import UserStepGuide, WebsiteAutoFixManager
from website_audit.models import AuditFinding


def test_autofix_requires_explicit_approval():
    finding = AuditFinding("سئو-001", "سئو", "عنوان صفحه وجود ندارد", "زیاد", "شواهد", "اثر", ["عنوان اضافه کنید"], True)
    called = []
    result = WebsiteAutoFixManager().apply(finding, False, lambda: called.append(True))
    assert result.status == "در انتظار تأیید"
    assert called == []


def test_autofix_runs_after_approval_and_requests_reaudit():
    finding = AuditFinding("سئو-001", "سئو", "عنوان صفحه وجود ندارد", "زیاد", "شواهد", "اثر", ["عنوان اضافه کنید"], True)
    called = []
    result = WebsiteAutoFixManager().apply(finding, True, lambda: called.append(True))
    assert result.status == "اصلاح شد"
    assert called == [True]
    assert result.نیازمند_ممیزی_مجدد is True


def test_manual_fix_is_not_executed_automatically():
    finding = AuditFinding("امنیت-001", "امنیت", "CSP تنظیم نشده", "متوسط", "شواهد", "اثر", ["CSP طراحی کنید"], False)
    called = []
    result = WebsiteAutoFixManager().apply(finding, True, lambda: called.append(True))
    assert result.status == "نیازمند اقدام کاربر"
    assert called == []


def test_user_step_guide_does_not_request_secret_in_chat():
    guide = UserStepGuide().build("Google Search Console", "https://search.google.com/search-console", ["وارد سرویس شوید.", "دسترسی لازم را فعال کنید."])
    assert guide["مرحله_فعلی"] == 1
    assert "کلید API" in guide["هشدار"]


def test_website_request_still_routes_to_website_audit():
    decision = IntelligentTaskRouter(create_default_registry()).select(
        Task("site-1", "ممیزی سایت", "سئو و ریسپانسیو سایت را بررسی کن", "")
    )
    assert decision.agent == "website-audit"
