"""Langfuse-style Observability — tracing, evals, prompt management.

Tracks every LLM call, agent action, and tool invocation with full context.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceSpan:
    """A single trace span (one LLM call, tool call, or agent action)."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    trace_id: str = ""
    parent_id: str | None = None
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    status: str = "pending"  # pending, completed, error
    input: Any = None
    output: Any = None
    metadata: dict = field(default_factory=dict)
    model: str | None = None
    token_usage: dict = field(default_factory=dict)
    cost: float = 0.0
    error: str | None = None

    def end(self, status: str = "completed") -> None:
        self.end_time = time.time()
        self.status = status

    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "trace_id": self.trace_id,
            "status": self.status,
            "duration_ms": round(self.duration_ms, 2),
            "model": self.model,
            "token_usage": self.token_usage,
            "cost": self.cost,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class Trace:
    """A complete trace (one user request through the system)."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    name: str = ""
    user_id: str | None = None
    session_id: str | None = None
    input: Any = None
    output: Any = None
    spans: list[TraceSpan] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    total_cost: float = 0.0
    total_tokens: int = 0

    def add_span(self, span: TraceSpan) -> None:
        span.trace_id = self.id
        self.spans.append(span)

    def end(self) -> None:
        self.end_time = time.time()
        self.total_cost = sum(s.cost for s in self.spans)
        self.total_tokens = sum(s.token_usage.get("total", 0) for s in self.spans)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "input": str(self.input)[:200] if self.input else None,
            "output": str(self.output)[:200] if self.output else None,
            "spans": [s.to_dict() for s in self.spans],
            "total_cost": round(self.total_cost, 6),
            "total_tokens": self.total_tokens,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class EvalResult:
    """Evaluation result for a trace."""

    name: str
    score: float  # 0.0 to 1.0
    comment: str = ""
    source: str = "auto"  # auto, llm_judge, human


class ObservabilityPlatform:
    """Langfuse-style observability platform.

    Features:
    - Trace recording and visualization
    - Cost tracking per trace
    - Token usage monitoring
    - Evaluation scoring
    - Prompt versioning
    - Session tracking
    """

    def __init__(self) -> None:
        self._traces: dict[str, Trace] = {}
        self._evals: dict[str, list[EvalResult]] = {}
        self._prompts: dict[str, list[dict]] = {}
        self._metrics: dict[str, list[float]] = {}

    def create_trace(self, name: str, **kwargs: Any) -> Trace:
        trace = Trace(name=name, **kwargs)
        self._traces[trace.id] = trace
        return trace

    def get_trace(self, trace_id: str) -> Trace | None:
        return self._traces.get(trace_id)

    def list_traces(self, limit: int = 50) -> list[dict]:
        traces = sorted(self._traces.values(),
                       key=lambda t: t.start_time, reverse=True)
        return [t.to_dict() for t in traces[:limit]]

    def score(self, trace_id: str, eval_result: EvalResult) -> None:
        if trace_id not in self._evals:
            self._evals[trace_id] = []
        self._evals[trace_id].append(eval_result)

    def get_scores(self, trace_id: str) -> list[dict]:
        return [
            {"name": e.name, "score": e.score, "comment": e.comment}
            for e in self._evals.get(trace_id, [])
        ]

    # ── Prompt Management ──────────────────────────────────

    def create_prompt(self, name: str, template: str, version: int = 1) -> None:
        if name not in self._prompts:
            self._prompts[name] = []
        self._prompts[name].append({
            "version": version,
            "template": template,
            "created_at": time.time(),
        })

    def get_prompt(self, name: str, version: int | None = None) -> str | None:
        prompts = self._prompts.get(name, [])
        if not prompts:
            return None
        if version:
            for p in prompts:
                if p["version"] == version:
                    return p["template"]
        return prompts[-1]["template"]

    # ── Metrics ────────────────────────────────────────────

    def record_metric(self, name: str, value: float) -> None:
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(value)

    def get_metric_stats(self, name: str) -> dict:
        values = self._metrics.get(name, [])
        if not values:
            return {"count": 0}
        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "p50": sorted(values)[len(values) // 2],
        }

    # ── Summary ────────────────────────────────────────────

    def summary(self) -> dict:
        total_cost = sum(t.total_cost for t in self._traces.values())
        total_tokens = sum(t.total_tokens for t in self._traces.values())
        return {
            "total_traces": len(self._traces),
            "total_cost": round(total_cost, 6),
            "total_tokens": total_tokens,
            "total_evals": sum(len(v) for v in self._evals.values()),
            "total_prompts": len(self._prompts),
        }
