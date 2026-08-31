from pathlib import Path

from core.memory.store import SharedMemory


def test_store_and_retrieve(tmp_path: Path) -> None:
    mem = SharedMemory(path=str(tmp_path / "m.db"), backend="sqlite")
    mem.add("p1", "requirement", "login", "users must sign in with email")
    mem.add("p1", "code", "auth.py", "def login(): pass")
    hits = mem.search("p1", "email login")
    assert hits
    assert any("login" in r.title or "login" in r.content for r, _ in hits)
    ctx = mem.retrieve_context("p1", "auth")
    assert "login" in ctx.lower() or "auth" in ctx.lower()


def test_json_backend(tmp_path: Path) -> None:
    mem = SharedMemory(path=str(tmp_path / "m.json"), backend="json")
    mem.add("p2", "decision", "db", "use sqlite")
    mem2 = SharedMemory(path=str(tmp_path / "m.json"), backend="json")
    hits = mem2.search("p2", "sqlite")
    assert hits
    assert hits[0][0].kind == "decision"
