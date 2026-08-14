from __future__ import annotations

from dataclasses import asdict

from runtime import ManagerRuntime


class ManagerAPI:
    """رابط ساده برای اجرای Manager از برنامه‌های دیگر."""

    def __init__(self, runtime: ManagerRuntime | None = None) -> None:
        self.runtime = runtime or ManagerRuntime()

    def execute(self, request: str, agent: str = "developer") -> dict:
        """درخواست را اجرا می‌کند و گزارش ساختاریافته برمی‌گرداند."""
        if not request.strip():
            raise ValueError("درخواست نمی‌تواند خالی باشد.")

        report = self.runtime.run(request, agent)
        return report.to_dict()


_manager_api = ManagerAPI()


def execute(request: str, agent: str = "developer") -> dict:
    """تابع عمومی اجرای Manager."""
    return _manager_api.execute(request, agent)
