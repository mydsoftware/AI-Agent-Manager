from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class RuntimeStub:
    def __init__(self):
        self.calls = []

    def run(self, request: str):
        self.calls.append(request)
        return {"status": "completed", "request": request}


def test_session_contract(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = RuntimeStub()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    state = flow.start("contract-1", "یک سایت بساز")
    assert state.status == "waiting_for_user"
    assert not runtime.calls

    state = flow.answer("contract-1", "سایت خدمات ماهواره مرکزی")
    assert state.status == "completed"
    assert runtime.calls
    assert "سایت خدمات ماهواره مرکزی" in runtime.calls[-1]
