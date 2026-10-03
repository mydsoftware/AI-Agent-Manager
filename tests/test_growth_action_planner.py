import json

from manager.growth_action_planner import GrowthActionPlanner


def test_plan_parses_actions_and_generates_stable_keys():
    raw = json.dumps({
        "actions": [
            {"name": "create_lead", "phase": "lead_generation", "payload": {"id": 7}},
            {"name": "send_follow_up", "payload": {"lead_id": 7}},
        ]
    })

    planned = GrowthActionPlanner().plan(raw, "analytics")

    assert [item.action.name for item in planned] == ["create_lead", "send_follow_up"]
    assert planned[0].action.phase == "lead_generation"
    assert planned[1].action.phase == "analytics"
    assert len(planned[0].key) == 64


def test_plan_deduplicates_identical_actions():
    raw = json.dumps({
        "actions": [
            {"name": "create_lead", "payload": {"id": 7}},
            {"name": "create_lead", "payload": {"id": 7}},
        ]
    })

    planned = GrowthActionPlanner().plan(raw, "lead_generation")

    assert len(planned) == 1


def test_plan_ignores_invalid_output():
    planner = GrowthActionPlanner()

    assert planner.plan("not-json", "analytics") == []
    assert planner.plan(json.dumps({"actions": "invalid"}), "analytics") == []
