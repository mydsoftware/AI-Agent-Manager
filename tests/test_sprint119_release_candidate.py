from manager.release_gate import ReleaseGate


def test_release_candidate_allows_only_fully_green_build():
    result = ReleaseGate().evaluate(tests=True, quality=True, security=True, health=True)
    assert result.ready
    assert all(result.checks.values())
