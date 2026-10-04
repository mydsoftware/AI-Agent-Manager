from manager.application import ManagerApplication
from manager.task import Task


def test_application_detects_business_growth_intent():
    app = ManagerApplication()
    decision = app.intent_router.classify("کارثبت را از صفر تا صد بساز، سئو و بازاریابی را انجام بده")
    assert decision.intent == "business_growth"


def test_business_growth_task_has_explicit_target():
    app = ManagerApplication()
    task = Task(
        id="growth-test",
        title="رشد کارثبت",
        description="کارثبت را از صفر تا صد رشد بده",
        agent="business-strategy",
    )
    assert app.intent_router.classify(task.description).intent == "business_growth"



def test_application_accepts_growth_action_registry():
    from manager.growth_actions import GrowthActionRegistry

    registry = GrowthActionRegistry()
    app = ManagerApplication(growth_actions=registry)

    assert app.business_growth_runtime.action_registry is registry
