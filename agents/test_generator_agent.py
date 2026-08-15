from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class GeneratedTest:
    name: str
    category: str
    scenario: str


class TestGeneratorAgent:
    """تولید Test Case از روی درخواست و تغییرات مهندسی."""

    def generate(self, request: str, diff: str | None = None) -> tuple[GeneratedTest, ...]:
        text = f"{request}\n{diff or ''}".lower()
        tests: list[GeneratedTest] = [
            GeneratedTest("test_happy_path", "functional", "مسیر اصلی قابلیت باید موفق شود."),
            GeneratedTest("test_invalid_input", "validation", "ورودی نامعتبر باید به شکل کنترل‌شده رد شود."),
        ]
        if re.search(r"api|endpoint|http|rest", text):
            tests.append(GeneratedTest("test_api_contract", "api", "قرارداد API و پاسخ خطا باید پایدار باشد."))
        if re.search(r"auth|login|permission|role", text):
            tests.append(GeneratedTest("test_authorization", "security", "کاربر بدون دسترسی نباید عملیات را انجام دهد."))
        if re.search(r"database|db|sql|model|order|payment", text):
            tests.append(GeneratedTest("test_persistence", "integration", "داده باید درست ذخیره و بازیابی شود."))
        if re.search(r"wordpress|wp-|theme|plugin", text):
            tests.append(GeneratedTest("test_wordpress_install", "wordpress", "قالب/افزونه باید بدون خطای PHP فعال شود."))
        return tuple(tests)
