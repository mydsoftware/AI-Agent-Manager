from pathlib import Path

from agents.public_site_scanner import PublicSiteScanner


def test_generate_html_report_writes_utf8_file(tmp_path: Path):
    scanner = PublicSiteScanner()
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/",
            status=200,
            title="صفحه اصلی",
        )
    )

    target = scanner.generate_html_report(tmp_path / "audit-report.html")

    assert target == tmp_path / "audit-report.html"
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert '<html lang="fa" dir="rtl">' in content
    assert "صفحه اصلی" in content
