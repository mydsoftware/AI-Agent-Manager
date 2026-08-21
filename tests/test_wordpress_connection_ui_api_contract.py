from pathlib import Path


def test_ui_calls_connection_check_endpoint_and_has_status_states():
    html = Path("ui/wordpress_connection_setup.html").read_text(encoding="utf-8")
    assert "/api/wordpress/connection/check" in html
    assert "در حال بررسی..." in html
    assert "احراز هویت Agent ناموفق" in html
    assert "Endpoint اختصاصی Agent آماده نیست" in html
    assert "برای اجرای Audit آماده است" in html
    assert "application_password:appPassword" in html.replace(" ", "")
