from __future__ import annotations

import json

from agents.github_project_agent import GitHubProjectAgent
from manager.autonomous_engineering import AutonomousEngineeringLoop


class FakeProjectAgent(GitHubProjectAgent):
    def __init__(self, responses):
        self.responses = list(responses)
        self.commands = []

    def run(self, task):
        command = json.loads(task.description)
        self.commands.append(command)
        return self.responses.pop(0)


def test_loop_creates_branch_and_pr_when_ci_is_not_failed():
    agent = FakeProjectAgent([
        '{"ref":"refs/heads/test-loop"}',
        '{"workflow_runs":[{"conclusion":"success"}]}',
        '{"number":1,"draft":true}',
    ])
    result = AutonomousEngineeringLoop(agent).execute(
        "mydsoftware/AI-Agent-Manager", "feature/manager-core", "test-loop"
    )
    assert result.success is True
    assert [item["operation"] for item in agent.commands] == ["create_branch", "workflow_status", "create_pr"]


def test_loop_stops_after_branch_failure():
    agent = FakeProjectAgent(["raise"])

    def broken_run(task):
        raise RuntimeError("خطای ساخت شاخه")

    agent.run = broken_run
    result = AutonomousEngineeringLoop(agent).execute(
        "repo", "main", "test-loop"
    )
    assert result.success is False
    assert result.attempts == 0
