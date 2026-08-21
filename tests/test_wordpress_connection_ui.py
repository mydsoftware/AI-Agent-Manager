from pathlib import Path


def test_wordpress_connection_ui_contains_persian_five_step_flow():
    html = Path("ui/wordpress_connection_setup.html").read_text(encoding="utf-8")
    for text in ("آدرس سایت", "کاربر مدیر", "Application Password", "Agent Token", "تست اتصال"):
        assert text in html
    assert 'dir="rtl"' in html
    assert "اجرای Write تا تأیید کامل اتصال مسدود" in html
