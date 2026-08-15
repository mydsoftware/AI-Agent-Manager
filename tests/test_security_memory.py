from __future__ import annotations

from manager.auth import APIAuthenticator
from manager.persistent_memory import PersistentMemory


def test_api_authenticator() -> None:
    """کلید معتبر باید پذیرفته و کلید نامعتبر رد شود."""
    import os

    os.environ["TEST_MANAGER_KEY"] = "کلید-آزمایشی"
    authenticator = APIAuthenticator("TEST_MANAGER_KEY")

    assert authenticator.enabled
    assert authenticator.validate("کلید-آزمایشی")
    assert not authenticator.validate("کلید-اشتباه")


def test_persistent_memory(tmp_path) -> None:
    """حافظه باید رویدادها را بین اتصال‌ها نگهداری کند."""
    database = tmp_path / "manager.db"
    first = PersistentMemory(str(database))
    first.add("آزمایش", {"ok": True})

    second = PersistentMemory(str(database))
    events = second.all()

    assert len(events) == 1
    assert events[0]["event"] == "آزمایش"
    assert events[0]["data"] == {"ok": True}
