from agents.site_writer import DryRunSiteWriter


def test_dry_run_writer_never_changes_site():
    result = DryRunSiteWriter().set_canonical(
        "https://example.com/page",
        "https://example.com/page",
    )

    assert result.success is True
    assert result.changed is False
    assert "Dry Run" in result.message
