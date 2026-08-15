from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class RuntimeStub:
    def __init__(self):
        self.calls = []

    def run(self, request: str, agent: str = "developer"):
        self.calls.append((request, agent))
        return {"status": "success", "artifact": "output.txt", "agent": agent}


def test_user_only_answers_ambiguity_then_agent_finishes(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = RuntimeStub()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    state = flow.start("s85", "یک سایت بساز")
    assert state.status == "waiting_for_user"
    assert state.question
    assert runtime.calls == []

    state = flow.answer("s85", "فروشگاه اینترنتی بساز")
    assert state.status == "completed"
    assert state.stage == "delivery"
    assert state.output["report"]["status"] == "success"
    assert len(runtime.calls) == 1


def test_specific_request_needs_no_user_intervention(tmp_path):
    sessions = UserSessionManager(str(tmp_path))
    runtime = RuntimeStub()
    flow = SessionRuntime(sessions=sessions, runtime=runtime)

    state = flow.start("s85-direct", "برای گیتهاب یک پروژه بساز")
    assert state.status == "completed"
    assert state.question is None
    assert len(runtime.calls) == 1
