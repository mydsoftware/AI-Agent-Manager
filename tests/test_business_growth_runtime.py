from manager.business_growth_runtime import BusinessGrowthRuntime
from manager.business_growth import BusinessGrowthPipeline
from manager.growth_actions import GrowthActionRegistry


class FakeExecutor:
    def __init__(self, results=None):
        self.calls = []
        self.results = results or {}

    def run(self, tasks):
        self.calls.append(tasks[0])
        return [self.results.get(
            tasks[0].agent,
            f'{{"type":"business_growth_result","phase":"{tasks[0].agent}"}}'
        )]


def test_growth_runtime_executes_all_stages_in_order():
    executor = FakeExecutor()
    history = BusinessGrowthRuntime(executor).run(
        "از صفر تا صد رشد کارثبت",
        target="کارثبت / karsabt.ir",
    )

    assert len(history) == len(BusinessGrowthPipeline.STAGES)
    assert [item["agent"] for item in history] == [
        stage.agent for stage in BusinessGrowthPipeline.STAGES
    ]
    assert len(executor.calls) == len(BusinessGrowthPipeline.STAGES)
    assert "خروجی مرحله قبلی" in executor.calls[1].description


def test_growth_runtime_executes_planned_action_once():
    class Adapter:
        def __init__(self):
            self.calls = 0

        def execute(self, action):
            self.calls += 1
            return {"status": "executed", "action": action.name, "external_execution": True}

    adapter = Adapter()
    registry = GrowthActionRegistry({"create_lead": adapter})
    executor = FakeExecutor({
        "lead-generation": '{"actions":[{"name":"create_lead","payload":{"lead_id":"L1"}}]}'
    })

    history = BusinessGrowthRuntime(executor, registry).run("lead test")
    result = history[5]["result"]

    assert adapter.calls == 1
    assert result.count('"action": "create_lead"') == 1
    assert '"external_execution": true' in result
