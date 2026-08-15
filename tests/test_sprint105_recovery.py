from manager.recovery import RecoveryExecutor


def test_recovery_retries_then_succeeds():
    calls = []

    def operation():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("temporary")
        return "ok"

    executor = RecoveryExecutor(retries=2)
    assert executor.run(operation) == "ok"
    assert len(calls) == 3


def test_recovery_raises_after_retry_budget():
    calls = []

    def operation():
        calls.append(1)
        raise RuntimeError("fatal")

    executor = RecoveryExecutor(retries=2)
    try:
        executor.run(operation)
        assert False
    except RuntimeError as error:
        assert str(error) == "fatal"
    assert len(calls) == 3
