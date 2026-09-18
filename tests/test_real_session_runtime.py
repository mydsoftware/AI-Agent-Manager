from manager.report import ManagerReport
from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class FakeRuntime:
    def __init__(self):
        self.requests = []

    def run(self, request: str):
        self.requests.append(request)
        return ManagerReport([])


def test_session_runtime_clarifies_and_resumes(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = FakeRuntime()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    waiting = flow.start("real-1", "یک سایت بساز")
    assert waiting.status == "waiting_for_user"
    assert runtime.requests == []

    completed = flow.answer("real-1", "سایت وردپرسی خدمات ماهواره مرکزی")
    assert completed.status == "completed"
    assert completed.stage == "delivery"
    assert len(runtime.requests) == 1
    assert "خدمات ماهواره مرکزی" in runtime.requests[0]


def test_session_runtime_runs_complete_request(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = FakeRuntime()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    result = flow.start("real-2", "یک سایت وردپرسی برای خدمات ماهواره مرکزی بساز")
    assert result.status == "completed"
    assert result.question is None
    assert len(runtime.requests) == 1
