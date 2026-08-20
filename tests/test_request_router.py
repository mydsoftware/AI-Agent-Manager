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
