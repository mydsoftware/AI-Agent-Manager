"""رابط عمومی API برای Manager."""

from runtime import ManagerRuntime


def execute(request: str, agent: str = "developer") -> dict:
    """اجرای عمومی Manager و بازگرداندن گزارش ساختاریافته."""
    if not request.strip():
        raise ValueError("درخواست نمی‌تواند خالی باشد.")
    return ManagerRuntime().run(request, agent).to_dict()
