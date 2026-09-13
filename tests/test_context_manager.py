from manager.context_manager import ContextManager


def test_context_manager_keeps_context_under_budget() -> None:
    manager = ContextManager(max_tokens=100, reserve_tokens=10)
    messages = [{"role": "system", "content": "system"}, {"role": "user", "content": "hello"}]
    result = manager.prepare(messages)
    assert result.estimated_tokens <= 90
    assert result.compacted is False


def test_context_manager_compacts_old_messages() -> None:
    manager = ContextManager(max_tokens=80, reserve_tokens=10)
    messages = [{"role": "system", "content": "rules"}] + [
        {"role": "user", "content": "x" * 120} for _ in range(4)
    ]
    result = manager.prepare(messages)
    assert result.compacted is True
    assert result.messages[0]["role"] == "system"
    assert result.estimated_tokens <= 70


def test_context_manager_bounds_oversized_system_message() -> None:
    manager = ContextManager(max_tokens=80, reserve_tokens=10)
    messages = [
        {"role": "system", "content": "system-rules " * 200},
        {"role": "user", "content": "latest request"},
    ]
    result = manager.prepare(messages)
    assert result.compacted is True
    assert result.estimated_tokens <= 70
    assert "context truncated" in result.messages[0]["content"]
