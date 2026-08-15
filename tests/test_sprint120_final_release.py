from manager.release_gate import ReleaseGate


def test_final_release_gate_is_green():
    result = ReleaseGate().evaluate(
        tests=True,
        quality=True,
        security=True,
        health=True,
    )
    assert result.ready is True
    assert result.checks == {
        "tests": True,
        "quality": True,
        "security": True,
        "health": True,
    }
