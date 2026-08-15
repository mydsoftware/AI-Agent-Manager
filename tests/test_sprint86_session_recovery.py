from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class RuntimeStub:
    def __init__(self):
        self.calls = 0

    def run(self, request: str, agent: str = "developer"):
        self.calls += 1
        return {"status": "success", "artifact": "recovered.txt", "agent": agent}


def test_answer_persists_context_and_output_after_recovery(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = RuntimeStub()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    waiting = flow.start("s86", "یک سایت بساز")
    assert waiting.status == "waiting_for_user"

    completed = flow.answer("s86", "فروشگاه اینترنتی بساز")
    assert completed.status == "completed"
    assert completed.answers == ["فروشگاه اینترنتی بساز"]

    restored = sessions.load("s86")
    assert restored.status == "completed"
    assert restored.answers == ["فروشگاه اینترنتی بساز"]
    assert restored.output["report"]["artifact"] == "recovered.txt"
    assert runtime.calls == 1
