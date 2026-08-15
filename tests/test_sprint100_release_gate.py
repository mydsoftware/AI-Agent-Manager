from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class RuntimeStub:
    def run(self, request: str, agent: str = "developer"):
        return {"status": "success", "artifact": "release.txt", "agent": agent}


def test_release_gate_complete_autonomous_flow(tmp_path):
    runtime = SessionRuntime(
        sessions=UserSessionManager(str(tmp_path)),
        runtime=RuntimeStub(),
    )

    state = runtime.start("release-100", "یک سایت بساز")
    assert state.status == "waiting_for_user"

    state = runtime.answer("release-100", "یک سایت فروشگاهی بساز")
    assert state.status == "completed"
    assert state.stage == "delivery"
    assert state.output["report"]["status"] == "success"
    assert state.answers == ["یک سایت فروشگاهی بساز"]
