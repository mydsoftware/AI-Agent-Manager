from manager.chat_intent import ChatIntentParser, build_task_from_chat


def test_manager_command_is_detected_case_insensitively():
    command = ChatIntentParser().parse(
        "Ai agent manager\nسایت germantechsat.com رو بصورت کامل بررسی کن"
    )
    assert command.فعال is True
    assert command.url == "https://germantechsat.com"


def test_non_manager_message_is_not_activated():
    command = ChatIntentParser().parse("سایت germantechsat.com را بررسی کن")
    assert command.فعال is False


def test_chat_command_becomes_website_audit_task():
    task = build_task_from_chat(
        "AI AGENT MANAGER سایت https://germantechsat.com را کامل بررسی کن"
    )
    assert task["agent"] == "website-audit"
    assert task["url"] == "https://germantechsat.com"
    assert "گزارش" in task["description"]
