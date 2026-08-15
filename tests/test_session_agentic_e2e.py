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
    assert state.output["report"]["artifact"] == "final-output"
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
    assert state.output["report"]["artifact"] == "final-output"
    assert len(runtime.calls) == 1


def test_session_output_is_json_serializable_and_persistent(tmp_path):
    sessions = UserSessionManager(str(tmp_path / "sessions"))
    runtime = ReportRuntime()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    state = flow.start("e2e-3", "برای گیتهاب یک پروژه بساز")
    persisted = sessions.load("e2e-3")

    assert isinstance(state.output, dict)
    assert isinstance(persisted.output, dict)
    assert persisted.output["agent"] == "github"
    assert persisted.output["report"]["status"] == "completed"


def test_resume_completed_session_is_idempotent(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = ReportRuntime()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    first = flow.start("resume-1", "یک پروژه کامل برای گیتهاب بساز")
    second = flow.resume("resume-1")

    assert first.status == "completed"
    assert second.status == "completed"
    assert second.output == first.output
    assert len(runtime.calls) == 1


def test_resume_waiting_session_does_not_execute(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = ReportRuntime()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    state = flow.start("resume-2", "یک سایت بساز")
    resumed = flow.resume("resume-2")

    assert state.status == "waiting_for_user"
    assert resumed.status == "waiting_for_user"
    assert resumed.question
    assert runtime.calls == []
