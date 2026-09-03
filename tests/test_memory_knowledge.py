from __future__ import annotations

from services.memory_store import MemoryStore
from services.knowledge_store import KnowledgeStore


def test_memory_upsert_list_delete(tmp_path):
    store=MemoryStore(str(tmp_path/"db.sqlite"))
    item=store.upsert("project","p1","stack",{"framework":"Flask"},importance=9)
    assert item["value"]["framework"]=="Flask"
    updated=store.upsert("project","p1","stack",{"framework":"Next.js"},importance=8)
    assert updated["id"]==item["id"]
    assert store.list("project","p1")[0]["value"]["framework"]=="Next.js"
    assert store.delete(item["id"])
    assert store.get(item["id"]) is None


def test_knowledge_search_is_scoped(tmp_path):
    store=KnowledgeStore(str(tmp_path/"db.sqlite"))
    store.add("project","p1","Architecture","Flask API with SQLite")
    store.add("project","p2","Other","Flask but unrelated project")
    results=store.search("SQLite",scope="project",scope_id="p1")
    assert len(results)==1 and results[0]["title"]=="Architecture"
    assert store.search("SQLite",scope="project",scope_id="p2")==[]
