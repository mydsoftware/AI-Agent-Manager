"""Embedding abstraction. Default is a local hashing embedder (no paid API)."""

from __future__ import annotations

import hashlib
import math
from abc import ABC, abstractmethod
from typing import Sequence


class EmbeddingProvider(ABC):
    """Abstract embedding backend."""

    dim: int

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class HashingEmbedding(EmbeddingProvider):
    """Deterministic local bag-of-tokens embedding. No network, no paid APIs."""

    def __init__(self, dim: int = 128) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        tokens = [t for t in text.lower().replace("\n", " ").split(" ") if t]
        if not tokens:
            return vec
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "little") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return float(sum(x * y for x, y in zip(a, b)))
