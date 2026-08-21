from __future__ import annotations

from dataclasses import dataclass

from agents.wordpress_connection import WordPressConnectionCheck, WordPressConnectionConfig, WordPressConnectionTester


@dataclass(frozen=True)
class ConnectionSetupState:
    """وضعیت مرحله‌ای اتصال WordPress."""
    step: int
    total_steps: int
    title: str
    instruction: str
    complete: bool = False


class WordPressConnectionSetup:
    """فرآیند مرحله‌ای اتصال سایت مشتری بدون ذخیره Credential در کد."""

    steps = (
        ("آدرس سایت", "آدرس کامل سایت WordPress را وارد کنید."),
        ("کاربر مدیر", "نام کاربری مدیریتی با دسترسی لازم را وارد کنید."),
        ("Application Password", "Application Password وردپرس را وارد کنید."),
        ("Agent Token", "توکن اختصاصی AI Agent را وارد کنید."),
        ("تست اتصال", "اتصال و Endpoint اختصاصی را آزمایش کنید."),
    )

    def state(self, step: int, complete: bool = False) -> ConnectionSetupState:
        index = max(1, min(step, len(self.steps))) - 1
        title, instruction = self.steps[index]
        return ConnectionSetupState(index + 1, len(self.steps), title, instruction, complete)

    def test(self, config: WordPressConnectionConfig) -> WordPressConnectionCheck:
        """اتصال را تست می‌کند و Credential را در این کلاس ذخیره نمی‌کند."""
        return WordPressConnectionTester().test(config)
