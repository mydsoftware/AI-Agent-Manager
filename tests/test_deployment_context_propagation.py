from manager.task_status import TaskStatus
from services.deployment_orchestrator import DeploymentOrchestrator
from services.vercel_deployment import VercelConfig, VercelDeploymentService


class CommitReportingExecutor:
    def run(self, tasks):
        tasks[0].complete({"commit_sha": "sha-fixed"})
        return [{"commit_sha": "sha-fixed"}]


def test_fix_task_reports_new_commit_sha():
    orchestrator = DeploymentOrchestrator(
        CommitReportingExecutor(),
        VercelDeploymentService(VercelConfig(token="")),
        browser_qa=object(),
    )

    result = orchestrator._execute_fix_task({
        "project_id": "project-1",
        "branch": "feature/fix",
        "commit_sha": "sha-old",
        "preview_url": "https://preview.example.com",
        "qa": {"status": "failed"},
    })

    assert result["status"] == "committed"
    assert result["commit_sha"] == "sha-fixed"
