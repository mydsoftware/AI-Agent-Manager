from manager.release_gate import ReleaseGate


def test_release_gate_requires_all_checks():
    gate = ReleaseGate()
    assert gate.evaluate(tests=True, quality=True, security=True, health=True).ready is True
    assert gate.evaluate(tests=True, quality=True, security=False, health=True).ready is False
