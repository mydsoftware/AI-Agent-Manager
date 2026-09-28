from manager.business_growth_runtime import BusinessGrowthRuntime


class FakeExecutor:
    def __init__(self):
        self.calls = []

    def run(self, tasks):
        task = tasks[0]
        self.calls.append(task)
        if task.agent == "website-builder":
            return ['{"type":"business_growth_result","phase":"website","engineering_plan":{"repository":"mydsoftware/karsabt","branch":"feature/website-foundation","changes":[{"path":"README.md","content":"# کارثبت","message":"feat: website foundation"}]}}']
        if task.agent == "github-project":
            return ['{"state":"completed","ci_status":"success"}']
        return [f'{{"type":"business_growth_result","phase":"{task.agent}"}}']


def test_website_plan_is_forwarded_to_engineering_loop():
    executor = FakeExecutor()
    history = BusinessGrowthRuntime(executor).run("کارثبت را از صفر بساز")

    github_calls = [task for task in executor.calls if task.agent == "github-project"]
    assert github_calls
    assert history[1]["agent"] == "website-builder"
    assert "engineering_execution" in history[1]["result"]
