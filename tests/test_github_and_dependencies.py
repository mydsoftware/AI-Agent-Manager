from __future__ import annotations

from adapters.github_adapter import GitHubAdapter
from manager.executor import TaskExecutor
from manager.loop import AgenticLoop
from manager.memory import Memory
from manager.router import Router
from manager.task import Task
from manager.task_status import TaskStatus


class FakeGitHubClient:
    """کلاینت ساختگی برای آزمایش Adapter بدون اتصال شبکه."""

    def get_repository(self, repository: str):
        return {"repository": repository}

    def get_file(self, repository: str, path: str, ref: str | None = None):
        return {"repository": repository, "path": path, "ref": ref}

    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None):
        return {"repository": repository, "path": path, "branch": branch, "sha": sha}


def test_github_adapter_delegates_operations() -> None:
    """Adapter باید عملیات را بدون تغییر به کلاینت واگذار کند."""
    adapter = GitHubAdapter(FakeGitHubClient())
    assert adapter.repository("mydsoftware/AI-Agent-Manager")["repository"] == "mydsoftware/AI-Agent-Manager"
    assert adapter.file("repo", "README.md")["path"] == "README.md"
    assert adapter.put_file("repo", "a.txt", "متن", "آزمون", "main")["branch"] == "main"


def test_failed_dependency_blocks_next_task() -> None:
    """اگر وابستگی شکست بخورد، وظیفه بعدی نباید اجرا شود."""
    class FailingAgent:
        def run(self, task: Task) -> str:
            if task.id == "a":
                raise RuntimeError("شکست عمدی")
            return task.id

    class FakeRegistry:
        def get(self, name: str):
            return FailingAgent()

    tasks = [
        Task("a", "اول", "اول", "developer"),
        Task("b", "دوم", "دوم", "developer", depends_on=["a"]),
    ]
    loop = AgenticLoop(Router(FakeRegistry()), Memory())
    TaskExecutor(loop).run(tasks)

    assert tasks[0].status == TaskStatus.FAILED
    assert tasks[1].status == TaskStatus.BLOCKED
