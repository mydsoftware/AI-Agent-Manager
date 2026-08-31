import pytest

from core.safety.budget import BudgetController, BudgetExceeded
from core.safety.circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState
from core.safety.sandbox import Sandbox


def test_circuit_opens() -> None:
    cb = CircuitBreaker("t", failure_threshold=2, recovery_seconds=10)
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    assert cb.state == CircuitState.OPEN
    with pytest.raises(CircuitOpenError):
        cb.before_call()


def test_budget_exhausted() -> None:
    b = BudgetController(default_token_budget=10, daily_token_budget=100)
    b.can_start("task-1")
    with pytest.raises(BudgetExceeded):
        b.record_tokens("task-1", 50)
    snap = b.snapshot()
    assert snap["tasks"]["task-1"]["stopped_reason"] == "token_budget"


def test_sandbox_timeout() -> None:
    sb = Sandbox(timeout_seconds=0.2)
    result = sb.run_python("import time\ntime.sleep(2)")
    assert result.timed_out or not result.success


def test_sandbox_blocks_dangerous() -> None:
    sb = Sandbox()
    result = sb.run_shell("rm -rf /")
    assert result.blocked
    assert result.success is False
