from manager.growth_actions import (
    DryRunAdapter,
    GrowthAction,
    GrowthActionRegistry,
)


def test_unknown_action_uses_safe_dry_run():
    action = GrowthAction("collect_analytics", "analytics", {"date": "today"})
    result = GrowthActionRegistry().execute(action)

    assert result["status"] == "planned"
    assert result["external_execution"] is False
    assert result["action"] == "collect_analytics"


def test_registered_adapter_executes():
    class Adapter:
        def execute(self, action):
            return {"status": "executed", "external_execution": True, "action": action.name}

    registry = GrowthActionRegistry({"create_lead": Adapter()})
    result = registry.execute(GrowthAction("create_lead", "lead_generation", {"name": "test"}))

    assert result["status"] == "executed"
    assert result["external_execution"] is True


def test_execute_many_preserves_order():
    registry = GrowthActionRegistry()
    actions = [
        GrowthAction("create_lead", "lead_generation", {}),
        GrowthAction("send_follow_up", "sales", {}),
    ]

    results = registry.execute_many(actions)

    assert [item["action"] for item in results] == ["create_lead", "send_follow_up"]
    assert all(item["external_execution"] is False for item in results)
