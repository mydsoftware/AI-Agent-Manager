from manager.request_router import route_request


def test_website_audit_request_is_routed_to_farsi_pre_contract_audit():
    routed = route_request("AI Agent Manager سایت germantechsat.com رو بصورت کامل بررسی کن")
    assert routed.agent == "website-audit"
    assert routed.url == "https://germantechsat.com"
    assert routed.mode == "pre_contract"
    assert routed.access is False
    assert routed.language == "fa"


def test_explicit_url_is_preserved():
    routed = route_request("AI Agent Manager https://example.com را بررسی کن")
    assert routed.agent == "website-audit"
    assert routed.url == "https://example.com"


def test_non_audit_request_uses_developer_agent():
    routed = route_request("یک API برای پروژه بساز")
    assert routed.agent == "developer"
    assert routed.url is None
    assert routed.mode == "standard"


def test_audit_without_url_keeps_url_empty_for_api_validation():
    routed = route_request("AI Agent Manager سایت را بررسی کن")
    assert routed.agent == "website-audit"
    assert routed.url is None


def test_dual_file_and_fix_request_detects_access():
    routed = route_request(
        "ai agent manager سایت germantechsat.ir رو بررسی کن و تمام مشکلاتشو در یه فایل بگو "
        "و راههای اصلاحشو در فایل دیگه بگو. دسترسی دادم خودت اصلاحشون کن"
    )
    assert routed.agent == "website-audit"
    assert routed.url == "https://germantechsat.ir"
    assert routed.access is True
    assert routed.mode == "post_contract"
    assert routed.language == "fa"


def test_problems_and_solutions_phrase_routes_to_audit():
    routed = route_request("مشکلاتشو در یه فایل بگو و راههای اصلاحشو در فایل دیگه برای example.org")
    assert routed.agent == "website-audit"
    assert routed.url == "https://example.org"
