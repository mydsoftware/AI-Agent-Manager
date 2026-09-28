from manager.business_growth_runtime import BusinessGrowthRuntime
from manager.business_growth import BusinessGrowthPipeline


class FakeExecutor:
    def __init__(self):
        self.calls = []

    def run(self, tasks):
        self.calls.append(tasks[0])
        return [f'{{"type":"business_growth_result","phase":"{tasks[0].agent}"}}']


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
