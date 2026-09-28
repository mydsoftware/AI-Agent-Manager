from manager.growth_actions import DryRunAdapter, GrowthAction, GrowthActionRegistry
from manager.growth_kpis import DEFAULT_KPIS


def test_unknown_growth_action_is_safe_dry_run():
    result = GrowthActionRegistry().execute(
        GrowthAction("publish_campaign", "marketing", {"channel": "divar"})
    )
    assert result["status"] == "planned"
    assert result["external_execution"] is False


def test_default_growth_kpis_cover_funnel():
    names = {item.name for item in DEFAULT_KPIS}
    assert {"traffic", "leads", "qualified_leads", "conversion_rate", "customers", "revenue"} <= names
