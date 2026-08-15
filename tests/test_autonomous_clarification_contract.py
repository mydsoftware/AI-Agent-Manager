from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class RuntimeStub:
    def run(self, request: str):
        return {"status": "completed", "request": request}


def test_agent_asks_for_missing_scope_before_execution(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    flow = SessionRuntime(sessions=sessions, runtime=RuntimeStub())

    state = flow.start("clarify-1", "بساز")

    assert state.status == "waiting_for_user"
    assert state.question
    assert state.stage == "clarification"
