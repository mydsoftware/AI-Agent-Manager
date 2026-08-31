"""Shared project memory with SQLite default and JSON fallback. Optional Chroma."""

from __future__ import annotations

import json
import logging
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .embeddings import EmbeddingProvider, HashingEmbedding, cosine

logger = logging.getLogger(__name__)

KINDS = (
    "code",
    "architecture",
    "requirement",
    "project_context",
    "task_result",
    "gdd",
    "asset_meta",
    "decision",
)


@dataclass
class MemoryRecord:
    id: str
    project_id: str
    kind: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def text(self) -> str:
        return f"{self.title}\n{self.content}"


class SharedMemory:
    """Persistent per-project memory with keyword + semantic retrieval."""

    def __init__(
        self,
        path: str = "data/shared_memory.db",
        backend: str = "sqlite",
        embedder: EmbeddingProvider | None = None,
    ) -> None:
        self.path = path
        self.backend = backend
        self.embedder = embedder or HashingEmbedding()
        self._json_docs: list[MemoryRecord] = []
        self._json_vecs: dict[str, list[float]] = {}
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        if backend == "chroma":
            if not self._try_chroma():
                logger.warning("ChromaDB unavailable; falling back to sqlite")
                self.backend = "sqlite"
        if self.backend == "sqlite":
            self._init_sqlite()
        elif self.backend == "json":
            self._load_json()

    def _try_chroma(self) -> bool:
        try:
            import chromadb  # type: ignore

            self._chroma = chromadb.PersistentClient(path=str(Path(self.path).parent / "chroma"))
            self._collection = self._chroma.get_or_create_collection("shared_memory")
            return True
        except Exception as exc:  # pragma: no cover
            logger.info("chroma init failed: %s", exc)
            return False

    def _init_sqlite(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    embedding TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_project ON memories(project_id, kind)"
            )

    def _load_json(self) -> None:
        p = Path(self.path)
        if p.exists():
            raw = json.loads(p.read_text(encoding="utf-8"))
            self._json_docs = [MemoryRecord(**d) for d in raw.get("docs", [])]
            self._json_vecs = raw.get("vecs", {})

    def _save_json(self) -> None:
        Path(self.path).write_text(
            json.dumps(
                {"docs": [asdict(d) for d in self._json_docs], "vecs": self._json_vecs},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def add(
        self,
        project_id: str,
        kind: str,
        title: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        if kind not in KINDS:
            kind = "project_context"
        rec = MemoryRecord(
            id=str(uuid.uuid4()),
            project_id=project_id,
            kind=kind,
            title=title,
            content=content,
            metadata=metadata or {},
        )
        vec = self.embedder.embed(rec.text())
        if self.backend == "sqlite":
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    "INSERT INTO memories VALUES (?,?,?,?,?,?,?,?)",
                    (
                        rec.id,
                        rec.project_id,
                        rec.kind,
                        rec.title,
                        rec.content,
                        json.dumps(rec.metadata, ensure_ascii=False),
                        rec.created_at,
                        json.dumps(vec),
                    ),
                )
        elif self.backend == "json":
            self._json_docs.append(rec)
            self._json_vecs[rec.id] = vec
            self._save_json()
        elif self.backend == "chroma":
            self._collection.add(
                ids=[rec.id],
                documents=[rec.text()],
                metadatas=[
                    {
                        "project_id": project_id,
                        "kind": kind,
                        "title": title,
                        **{k: str(v) for k, v in rec.metadata.items()},
                    }
                ],
            )
        logger.info("memory.add project=%s kind=%s id=%s", project_id, kind, rec.id)
        return rec

    def _iter_sqlite(self, project_id: str, kind: str | None) -> Iterable[tuple[MemoryRecord, list[float]]]:
        q = "SELECT id, project_id, kind, title, content, metadata, created_at, embedding FROM memories WHERE project_id=?"
        args: list[Any] = [project_id]
        if kind:
            q += " AND kind=?"
            args.append(kind)
        with sqlite3.connect(self.path) as conn:
            for row in conn.execute(q, args):
                rec = MemoryRecord(
                    id=row[0],
                    project_id=row[1],
                    kind=row[2],
                    title=row[3],
                    content=row[4],
                    metadata=json.loads(row[5] or "{}"),
                    created_at=row[6],
                )
                yield rec, json.loads(row[7])

    def search(
        self,
        project_id: str,
        query: str,
        kind: str | None = None,
        limit: int = 5,
    ) -> list[tuple[MemoryRecord, float]]:
        qvec = self.embedder.embed(query)
        scored: list[tuple[MemoryRecord, float]] = []
        if self.backend == "sqlite":
            for rec, vec in self._iter_sqlite(project_id, kind):
                kw = 1.0 if query.lower() in rec.text().lower() else 0.0
                scored.append((rec, cosine(qvec, vec) + kw))
        elif self.backend == "json":
            for rec in self._json_docs:
                if rec.project_id != project_id:
                    continue
                if kind and rec.kind != kind:
                    continue
                vec = self._json_vecs.get(rec.id, [])
                kw = 1.0 if query.lower() in rec.text().lower() else 0.0
                scored.append((rec, cosine(qvec, vec) + kw))
        elif self.backend == "chroma":
            where: dict[str, Any] = {"project_id": project_id}
            if kind:
                where = {"$and": [{"project_id": project_id}, {"kind": kind}]}
            res = self._collection.query(query_texts=[query], n_results=limit, where=where)
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            ids = res.get("ids", [[]])[0]
            dists = res.get("distances", [[]])[0] if res.get("distances") else [0.0] * len(ids)
            out: list[tuple[MemoryRecord, float]] = []
            for i, doc in enumerate(docs):
                meta = metas[i] if i < len(metas) else {}
                rec = MemoryRecord(
                    id=ids[i],
                    project_id=project_id,
                    kind=str(meta.get("kind", "project_context")),
                    title=str(meta.get("title", "")),
                    content=doc,
                    metadata=dict(meta),
                )
                out.append((rec, 1.0 - float(dists[i] if i < len(dists) else 0)))
            return out
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]

    def retrieve_context(self, project_id: str, query: str, limit: int = 8) -> str:
        hits = self.search(project_id, query, limit=limit)
        if not hits:
            return ""
        parts = [f"[{rec.kind}] {rec.title}: {rec.content[:800]}" for rec, _ in hits]
        return "\n---\n".join(parts)


def create_shared_memory(path: str, backend: str = "sqlite") -> SharedMemory:
    return SharedMemory(path=path, backend=backend)
