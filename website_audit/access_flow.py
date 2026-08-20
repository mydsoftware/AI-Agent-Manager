from __future__ import annotations

from dataclasses import dataclass

from .access import build_access_requests


@dataclass
class AccessFlowState:
    """وضعیت راهنمای اتصال؛ در هر مرحله فقط یک اقدام به کاربر نشان داده می‌شود."""

    service_index: int = 0
    step_index: int = 0
    completed: bool = False


class WebsiteAccessWizard:
    """راهنمای کاربر برای دادن دسترسی‌ها بدون درخواست رمز در متن گفتگو."""

    def __init__(self) -> None:
        self.requests = build_access_requests()

    def current(self, state: AccessFlowState) -> dict[str, object]:
        if state.completed or state.service_index >= len(self.requests):
            return {"وضعیت": "کامل شد", "پیام": "همه دسترسی‌های انتخاب‌شده بررسی شدند."}
        item = self.requests[state.service_index]
        step = item.steps[state.step_index]
        return {
            "وضعیت": "در انتظار اقدام کاربر",
            "سرویس": item.title,
            "دلیل": item.reason,
            "مرحله": state.step_index + 1,
            "تعداد مراحل": len(item.steps),
            "اقدام فعلی": step,
            "محل انجام": item.url,
            "نکته امنیتی": "رمز عبور، API Key یا Application Password را داخل متن گفتگو ارسال نکنید؛ آن را فقط در بخش امن اتصال Manager ثبت کنید.",
        }

    def advance(self, state: AccessFlowState, success: bool = True) -> AccessFlowState:
        if not success or state.completed:
            return state
        item = self.requests[state.service_index]
        if state.step_index + 1 < len(item.steps):
            return AccessFlowState(state.service_index, state.step_index + 1)
        if state.service_index + 1 < len(self.requests):
            return AccessFlowState(state.service_index + 1, 0)
        return AccessFlowState(completed=True)
