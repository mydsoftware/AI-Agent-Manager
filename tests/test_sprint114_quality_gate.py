from manager.quality_gate import QualityGate


def test_quality_gate_accepts_good_output():
    decision = QualityGate(minimum_score=0.8).check({"status": "success"})
    assert decision.accepted is True
    assert decision.score == 1.0


def test_quality_gate_rejects_failed_output():
    decision = QualityGate(minimum_score=0.8).check({"status": "failed"})
    assert decision.accepted is False
    assert decision.score == 0.0
