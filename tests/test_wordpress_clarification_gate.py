from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_ambiguous_request_stops_and_asks_question(tmp_path: Path):
    result = WordPressFactoryPipeline().run("یک سایت بساز", str(tmp_path))
    assert result.passed is False
    assert result.clarification is not None
    assert result.clarification.needs_clarification is True
    assert result.clarification.question
    assert result.build is None


def test_clear_request_runs_without_user_intervention(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.clarification is not None
    assert result.clarification.needs_clarification is False
    assert result.build is not None
