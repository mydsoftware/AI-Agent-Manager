import json

from agents.android_build_agent import AndroidBuildAgent
from adapters.github_adapter import GitHubAdapter
from manager.task import Task


class FakeClient:
    def __init__(self):
        self.dispatched = []
        self.runs = {}

    def dispatch_workflow(self, repository, workflow, branch, inputs=None):
        self.dispatched.append((repository, workflow, branch, inputs or {}))
        return {"accepted": True}

    def workflow_runs(self, repository, branch=None, workflow=None):
        key = workflow
        return {"workflow_runs": self.runs.get(key, [{"head_branch": branch, "status": "completed", "conclusion": "failure"}])}


def test_android_build_uses_native_then_action_fallback():
    client = FakeClient()
    agent = AndroidBuildAgent(GitHubAdapter(client), poll_interval=0, timeout=1)
    task = Task(
        "android-build-1",
        "بیلد",
        json.dumps({
            "repository": "mydsoftware/AI-Agent-Manager",
            "branch": "feature/manager-core",
            "workflows": ["android-build-automated.yml", "android-build.yml"],
            "timeout": 1,
        }),
        "android-build",
    )

    result = json.loads(agent.run(task))

    assert result["status"] == "failed"
    assert [item[1] for item in client.dispatched] == ["android-build-automated.yml", "android-build.yml"]
