from manager.feedback_engine import FeedbackEngine


def test_feedback_accepts_valid_output():
    decision = FeedbackEngine().evaluate({"status": "success"})
    assert decision.accepted is True
    assert decision.score == 1.0


def test_feedback_rejects_failed_output():
    decision = FeedbackEngine().evaluate({"status": "failed"})
    assert decision.accepted is False
    assert decision.score == 0.0
