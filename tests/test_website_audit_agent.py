from agents.website_audit import WebsiteAuditAgent


def test_pre_contract_audit_returns_structured_farsi_report():
    report = WebsiteAuditAgent().audit(
        "https://example.com",
        observations=[
            {
                "category": "SEO",
                "title": "عنوان صفحه مناسب نیست",
                "severity": "زیاد",
                "impact": "کاهش کیفیت نمایش در موتورهای جستجو",
                "evidence": "مشاهده عمومی صفحه اصلی",
                "recommendation": "عنوان صفحه اصلاح شود",
                "effort": "ساده",
            }
        ],
    )
    assert report.language == "fa"
    assert report.mode == "pre_contract"
    assert report.access is False
    assert len(report.findings) == 1
    assert report.findings[0].category == "SEO"


def test_unknown_category_is_not_reported():
    report = WebsiteAuditAgent().audit(
        "https://example.com",
        observations=[{"category": "Database", "title": "نباید وارد شود"}],
    )
    assert report.findings == []


def test_access_is_rejected_before_contract():
    try:
        WebsiteAuditAgent().audit("https://example.com", access=True)
    except PermissionError as error:
        assert "دسترسی" in str(error)
    else:
        raise AssertionError("دسترسی فعال باید رد شود")
