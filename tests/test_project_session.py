from pathlib import Path

import pytest

from manager.project_session import ProjectSession, ProjectSessionStore


def test_session_persists_question_and_resumes(tmp_path: Path):
    store = ProjectSessionStore(str(tmp_path))
    session = ProjectSession("demo-1", "یک سایت بساز")
    session.stage("requirements")
    session.ask("موضوع سایت چیست؟", "site_topic")
    store.save(session)

    loaded = store.load("demo-1")
    assert loaded.status == "waiting_for_user"
    assert loaded.pending_question == "موضوع سایت چیست؟"

    loaded.answer("خدمات ماهواره مرکزی", "site_topic")
    loaded.stage("planning")
    store.save(loaded)

    resumed = store.load("demo-1")
    assert resumed.status == "running"
    assert resumed.current_stage == "planning"
    assert resumed.answers["site_topic"] == "خدمات ماهواره مرکزی"


def test_answer_requires_waiting_state():
    session = ProjectSession("demo-2", "test")
    with pytest.raises(RuntimeError, match="session-not-waiting"):
        session.answer("answer")
