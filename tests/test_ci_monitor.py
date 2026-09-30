from services.ci_monitor import CIMonitor


class FakeGitHub:
    def workflow_runs(self, owner, repository, branch, limit=10):
        return {"workflow_runs": [{"id": 7, "conclusion": "success", "head_sha": "abc"}]}


def test_latest_success():
    result = CIMonitor(FakeGitHub()).latest("o", "r", "feature/x")
    assert result == {"status": "passed", "run_id": 7, "head_sha": "abc"}


def test_latest_pending():
    class Pending(FakeGitHub):
        def workflow_runs(self, *args, **kwargs):
            return {"workflow_runs": [{"id": 8, "status": "in_progress", "conclusion": None}]}

    result = CIMonitor(Pending()).latest("o", "r", "feature/x")
    assert result["status"] == "pending"
