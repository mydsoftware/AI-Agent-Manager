from __future__ import annotations

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
    try:
        manager.answer("site-2", "پاسخ")
    except ValueError as error:
        assert "در انتظار پاسخ" in str(error)
    else:
        raise AssertionError("پاسخ بدون سؤال فعال نباید پذیرفته شود")
