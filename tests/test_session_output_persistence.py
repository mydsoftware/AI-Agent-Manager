from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class RuntimeStub:
    def run(self, request: str):
        return {"status": "success", "request": request, "artifact": "result.txt"}


def test_completed_output_survives_reload(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    flow = SessionRuntime(sessions=sessions, runtime=RuntimeStub())

    state = flow.start("output-1", "یک پروژه مشخص بساز")
    assert state.status == "completed"
    assert state.output["report"]["status"] == "success"

    restored = sessions.load("output-1")
    assert restored.status == "completed"
    assert restored.stage == "delivery"
    assert restored.output["report"]["artifact"] == "result.txt"
    assert restored.output["agent"] == "developer"
