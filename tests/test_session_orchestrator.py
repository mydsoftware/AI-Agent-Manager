from pathlib import Path

from manager.session_orchestrator import SessionOrchestrator
from manager.session_store import SessionStore


def test_session_orchestrator_start_ask_answer_resume(tmp_path: Path):
    store = SessionStore(str(tmp_path / "sessions"))
    orchestrator = SessionOrchestrator(store)

    started = orchestrator.start("site-1", "یک سایت وردپرسی بساز")
    assert started.status == "running"
    assert started.stage == "requirements"

    asked = orchestrator.ask("site-1", "موضوع سایت چیست؟")
    assert asked.status == "waiting_for_user"
    assert asked.question == "موضوع سایت چیست؟"

    resumed = orchestrator.answer("site-1", "خدمات ماهواره مرکزی", next_stage="planning")
    assert resumed.status == "running"
    assert resumed.stage == "planning"
    assert resumed.question is None

    restored = SessionOrchestrator(store).context("site-1")
    assert any(value == "خدمات ماهواره مرکزی" for value in restored.values.values())
