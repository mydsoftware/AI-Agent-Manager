"""Vector Memory — LanceDB-style semantic memory for AI agents.

Provides long-term memory with vector similarity search.
Agents can store experiences and retrieve relevant memories.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryEntry:
    """A single memory entry."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:10])
    content: str = ""
    metadata: dict = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)  # placeholder
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    importance: float = 0.5  # 0.0 to 1.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content[:200],
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "access_count": self.access_count,
            "importance": self.importance,
        }


class VectorMemory:
    """Vector-based memory store for AI agents.

    Provides:
    - Store memories with metadata
    - Semantic search (simulated without real embeddings)
    - Keyword search
    - Importance-based retrieval
    - Memory consolidation
    """

    def __init__(self, max_entries: int = 10000) -> None:
        self.max_entries = max_entries
        self._entries: dict[str, MemoryEntry] = {}

    def store(
        self,
        content: str,
        metadata: dict | None = None,
        importance: float = 0.5,
    ) -> MemoryEntry:
        """Store a new memory."""
        entry = MemoryEntry(
            content=content,
            metadata=metadata or {},
            importance=importance,
        )

        # Evict low-importance entries if full
        if len(self._entries) >= self.max_entries:
            self._evict()

        self._entries[entry.id] = entry
        return entry

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_importance: float = 0.0,
    ) -> list[MemoryEntry]:
        """Search memories by keyword relevance."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored = []
        for entry in self._entries.values():
            if entry.importance < min_importance:
                continue

            # Simple keyword scoring
            content_lower = entry.content.lower()
            score = 0.0

            # Exact match bonus
            if query_lower in content_lower:
                score += 10.0

            # Word overlap
            content_words = set(content_lower.split())
            overlap = len(query_words & content_words)
            score += overlap * 2.0

            # Importance boost
            score += entry.importance * 3.0

            # Recency boost (newer = higher)
            age_hours = (time.time() - entry.timestamp) / 3600
            recency = max(0, 1.0 - age_hours / 168)  # decay over 1 week
            score += recency * 2.0

            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [entry for _, entry in scored[:top_k]]

        # Update access counts
        for entry in results:
            entry.access_count += 1

        return results

    def get(self, entry_id: str) -> MemoryEntry | None:
        return self._entries.get(entry_id)

    def update(self, entry_id: str, content: str | None = None, **kwargs: Any) -> bool:
        entry = self._entries.get(entry_id)
        if not entry:
            return False
        if content is not None:
            entry.content = content
        for k, v in kwargs.items():
            if hasattr(entry, k):
                setattr(entry, k, v)
        return True

    def delete(self, entry_id: str) -> bool:
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False

    def list_all(self, limit: int = 100) -> list[dict]:
        entries = sorted(self._entries.values(),
                        key=lambda e: e.timestamp, reverse=True)
        return [e.to_dict() for e in entries[:limit]]

    def count(self) -> int:
        return len(self._entries)

    def consolidate(self) -> int:
        """Remove duplicate and low-value memories. Returns number removed."""
        removed = 0
        seen_hashes: set[str] = set()

        to_delete = []
        for entry_id, entry in self._entries.items():
            content_hash = hashlib.md5(entry.content.lower().strip().encode()).hexdigest()

            # Remove exact duplicates
            if content_hash in seen_hashes:
                to_delete.append(entry_id)
                removed += 1
                continue
            seen_hashes.add(content_hash)

            # Remove very old, rarely accessed, low-importance entries
            age_days = (time.time() - entry.timestamp) / 86400
            if (age_days > 30 and entry.access_count < 2 and entry.importance < 0.3):
                to_delete.append(entry_id)
                removed += 1

        for entry_id in to_delete:
            del self._entries[entry_id]

        return removed

    def _evict(self) -> None:
        """Evict lowest-importance entries."""
        if not self._entries:
            return
        sorted_entries = sorted(
            self._entries.values(),
            key=lambda e: (e.importance, e.access_count, e.timestamp)
        )
        # Remove bottom 10%
        to_remove = max(1, len(sorted_entries) // 10)
        for entry in sorted_entries[:to_remove]:
            if entry.id in self._entries:
                del self._entries[entry.id]

    def stats(self) -> dict:
        entries = list(self._entries.values())
        if not entries:
            return {"count": 0}
        return {
            "count": len(entries),
            "avg_importance": sum(e.importance for e in entries) / len(entries),
            "avg_access_count": sum(e.access_count for e in entries) / len(entries),
            "total_content_chars": sum(len(e.content) for e in entries),
        }
