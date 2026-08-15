from manager.recovery import ErrorRecovery, RecoveryPolicy


def test_recovery_exhausts_retry_budget():
    calls = 0

    def operation():
        nonlocal calls
        calls += 1
        raise TimeoutError("temporary")

    try:
        ErrorRecovery(RecoveryPolicy(max_retries=2)).run(operation)
        assert False
    except TimeoutError:
        pass

    assert calls == 3


def test_recovery_returns_first_success():
    calls = 0

    def operation():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ConnectionError("retry")
        return "success"

    assert ErrorRecovery(RecoveryPolicy(max_retries=2)).run(operation) == "success"
    assert calls == 2
