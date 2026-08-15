from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class ReportRuntime:
    def __init__(self):
        self.calls = []

    def run(self, request: str):
        self.calls.append(request)
        return {"status": "completed", "artifact": "final-output", "request": request}


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
    assert len(runtime.calls) == 1


def test_complete_request_goes_directly_to_runtime(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = ReportRuntime()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    state = flow.start("e2e-2", "یک سایت خدمات ماهواره مرکزی با صفحه معرفی و تماس بساز")
    assert state.status == "completed"
    assert state.stage == "delivery"
    assert len(runtime.calls) == 1
