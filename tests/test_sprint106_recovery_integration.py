from manager.recovery import RecoveryExecutor
from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class FlakyRuntime:
    def __init__(self):
        self.calls = 0

    def run(self, request, agent="developer"):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary agent failure")
        return {"status": "success", "result": request}


def test_recovery_executor_can_wrap_agent_runtime(tmp_path):
    runtime = FlakyRuntime()
    recovery = RecoveryExecutor(retries=1)
    sessions = UserSessionManager(str(tmp_path))
    session = sessions.create("recovery-106", "یک سایت بسازید با صفحه اصلی")

    output = recovery.run(lambda: runtime.run(session.request))

    assert output["status"] == "success"
    assert runtime.calls == 2
