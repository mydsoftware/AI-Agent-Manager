from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class ReportRuntime:
    def __init__(self):
        self.calls = []

    def run(self, request: str, agent: str = "developer"):
        self.calls.append((request, agent))
        return {"status": "completed", "artifact": "final-output", "request": request, "agent": agent}


def test_ambiguous_request_resumes_into_agent_runtime(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = ReportRuntime()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    state = flow.start("e2e-1", "یک سایت بساز")
    assert state.status == "waiting_for_user"
    assert runtime.calls == []

    state = flow.answer("e2e-1", "یک سایت خدمات ماهواره مرکزی بساز")
    assert state.status == "completed"
    assert state.stage == "delivery"
    assert state.output["artifact"] == "final-output"
    assert state.output["agent"] == "developer"
    assert len(runtime.calls) == 1


def test_complete_request_goes_directly_to_runtime(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = ReportRuntime()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    state = flow.start("e2e-2", "برای گیتهاب یک پروژه بساز")
    assert state.status == "completed"
    assert state.stage == "delivery"
    assert state.output["agent"] == "github"
    assert len(runtime.calls) == 1


def test_session_uses_real_manager_runtime(tmp_path):
    from runtime import ManagerRuntime

    sessions = UserSessionManager(str(tmp_path / "sessions"))
    runtime = ManagerRuntime(
        database_path=str(tmp_path / "manager.db"),
        registry_path=str(tmp_path / "agents.json"),
    )
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    state = flow.start("real-runtime-1", "یک برنامه ساده برای مدیریت پروژه بساز")

    assert state.status == "completed"
    assert state.stage == "delivery"
    assert state.output is not None
    assert state.output.status.value in {"success", "موفق"}
    assert state.output.successful == state.output.total
    assert state.output.failed == 0
    assert state.output.blocked == 0

    persisted = sessions.load("real-runtime-1")
    assert persisted.status == "completed"
    assert persisted.stage == "delivery"
    assert "موفق" in str(persisted.output) or "success" in str(persisted.output)
