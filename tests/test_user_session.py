from __future__ import annotations

import pytest

from manager.user_session import UserSessionManager


def test_user_session_question_answer_resume_and_complete(tmp_path):
    manager = UserSessionManager(str(tmp_path))
    started = manager.start("site-1", "یک سایت وردپرسی بساز")
    assert started.status == "running"

    waiting = manager.ask("site-1", "موضوع سایت چیست؟")
    assert waiting.status == "waiting_for_user"
    assert waiting.question == "موضوع سایت چیست؟"

    resumed = manager.answer("site-1", "خدمات ماهواره مرکزی")
    assert resumed.status == "running"
    assert resumed.stage == "planning"
    assert resumed.context["user_answers"][0]["answer"] == "خدمات ماهواره مرکزی"

    completed = manager.complete("site-1", {"package": "site.zip"})
    assert completed.status == "completed"
    assert completed.output == {"package": "site.zip"}

    restored = manager.get("site-1")
    assert restored.status == "completed"
    assert restored.context["user_answers"][0]["question"] == "موضوع سایت چیست؟"


def test_answer_without_active_question_is_rejected(tmp_path):
    manager = UserSessionManager(str(tmp_path))
    manager.start("site-2", "سایت بساز")
    with pytest.raises(ValueError, match="در انتظار پاسخ"):
        manager.answer("site-2", "پاسخ")


def test_session_id_rejects_path_and_invalid_characters(tmp_path):
    manager = UserSessionManager(str(tmp_path))
    with pytest.raises(ValueError):
        manager.start("../escape", "درخواست معتبر")
    with pytest.raises(ValueError):
        manager.start("session space", "درخواست معتبر")


def test_failed_session_is_persisted(tmp_path):
    manager = UserSessionManager(str(tmp_path))
    manager.start("site-fail", "درخواست معتبر")
    failed = manager.fail("site-fail", "اجرای Agent شکست خورد")
    assert failed.status == "failed"
    assert failed.stage == "execution"
    restored = manager.get("site-fail")
    assert restored.status == "failed"
    assert restored.output == {"error": "اجرای Agent شکست خورد"}


def test_session_save_is_recoverable_after_replacement(tmp_path):
    manager = UserSessionManager(str(tmp_path))
    manager.start("site-atomic", "درخواست معتبر")
    manager.complete("site-atomic", {"ok": True})
    assert manager.get("site-atomic").output == {"ok": True}
