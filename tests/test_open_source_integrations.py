"""Tests for open-source project integrations:
CrewAI, Langfuse, LanceDB, OpenHands patterns."""

import pytest


# ── CrewAI Tests ───────────────────────────────────────────

class TestCrew:
    def test_crew_creation(self):
        from core.crew import Crew, AgentConfig
        crew = Crew()
        crew.add_agent(AgentConfig(role="Dev", goal="code"))
        assert "Dev" in crew.agents

    def test_crew_kickoff(self):
        from core.crew import Crew, AgentConfig, TaskConfig
        crew = Crew()
        crew.add_agent(AgentConfig(role="Dev", goal="code"))
        crew.add_task(TaskConfig(
            description="Write feature", expected_output="code",
            agent_role="Dev"
        ))
        result = crew.kickoff()
        assert result.success is True
        assert len(result.agent_logs) == 1

    def test_crew_missing_agent(self):
        from core.crew import Crew, TaskConfig
        crew = Crew()
        crew.add_task(TaskConfig(
            description="Do something", expected_output="result",
            agent_role="Nonexistent"
        ))
        result = crew.kickoff()
        assert result.success is False

    def test_software_team(self):
        from core.crew import create_software_team
        crew = create_software_team()
        assert len(crew.agents) == 5
        assert "Developer" in crew.agents
        assert "QA Engineer" in crew.agents

    def test_game_team(self):
        from core.crew import create_game_team
        crew = create_game_team()
        assert len(crew.agents) == 5
        assert "Game Developer" in crew.agents

    def test_flow(self):
        from core.crew import Flow
        flow = Flow()
        flow.set_state("x", 10)
        flow.add_step("double", handler=lambda s: s["x"] * 2)
        result = flow.kickoff()
        assert result["final_state"]["double"] == 20


# ── Langfuse-style Observability Tests ────────────────────

class TestObservability:
    def test_trace_creation(self):
        from core.langfuse_platform import ObservabilityPlatform
        obs = ObservabilityPlatform()
        trace = obs.create_trace("test_trace")
        assert trace.id is not None
        assert trace.name == "test_trace"

    def test_trace_spans(self):
        from core.langfuse_platform import ObservabilityPlatform, TraceSpan
        obs = ObservabilityPlatform()
        trace = obs.create_trace("test")
        span = TraceSpan(name="llm_call", model="gpt-4")
        span.end()
        trace.add_span(span)
        assert len(trace.spans) == 1
        assert trace.spans[0].duration_ms >= 0

    def test_trace_cost(self):
        from core.langfuse_platform import ObservabilityPlatform, TraceSpan
        obs = ObservabilityPlatform()
        trace = obs.create_trace("cost_test")
        span = TraceSpan(name="call", token_usage={"total": 1000}, cost=0.01)
        span.end()
        trace.add_span(span)
        trace.end()
        assert trace.total_cost == 0.01
        assert trace.total_tokens == 1000

    def test_scoring(self):
        from core.langfuse_platform import ObservabilityPlatform, EvalResult
        obs = ObservabilityPlatform()
        trace = obs.create_trace("eval_test")
        obs.score(trace.id, EvalResult(name="quality", score=0.9, comment="good"))
        scores = obs.get_scores(trace.id)
        assert len(scores) == 1
        assert scores[0]["score"] == 0.9

    def test_prompt_management(self):
        from core.langfuse_platform import ObservabilityPlatform
        obs = ObservabilityPlatform()
        obs.create_prompt("planner", "You are a planner v1", version=1)
        obs.create_prompt("planner", "You are a planner v2", version=2)
        assert obs.get_prompt("planner", version=1) == "You are a planner v1"
        assert obs.get_prompt("planner") == "You are a planner v2"

    def test_metrics(self):
        from core.langfuse_platform import ObservabilityPlatform
        obs = ObservabilityPlatform()
        for v in [100, 200, 300, 400, 500]:
            obs.record_metric("latency", v)
        stats = obs.get_metric_stats("latency")
        assert stats["count"] == 5
        assert stats["mean"] == 300

    def test_summary(self):
        from core.langfuse_platform import ObservabilityPlatform
        obs = ObservabilityPlatform()
        obs.create_trace("t1")
        obs.create_prompt("p1", "template")
        summary = obs.summary()
        assert summary["total_traces"] == 1
        assert summary["total_prompts"] == 1


# ── LanceDB-style Vector Memory Tests ─────────────────────

class TestVectorMemory:
    def test_store_and_get(self):
        from core.vector_memory import VectorMemory
        mem = VectorMemory()
        entry = mem.store("I learned Python today", importance=0.8)
        assert mem.get(entry.id) is not None
        assert mem.count() == 1

    def test_search(self):
        from core.vector_memory import VectorMemory
        mem = VectorMemory()
        mem.store("Python is great for AI", importance=0.9)
        mem.store("JavaScript for web", importance=0.7)
        mem.store("Python ML libraries", importance=0.8)
        results = mem.search("Python AI")
        assert len(results) >= 1
        assert any("Python" in r.content for r in results)

    def test_search_empty(self):
        from core.vector_memory import VectorMemory
        mem = VectorMemory()
        results = mem.search("nonexistent")
        assert len(results) == 0

    def test_delete(self):
        from core.vector_memory import VectorMemory
        mem = VectorMemory()
        entry = mem.store("test")
        assert mem.delete(entry.id) is True
        assert mem.get(entry.id) is None

    def test_update(self):
        from core.vector_memory import VectorMemory
        mem = VectorMemory()
        entry = mem.store("old content")
        assert mem.update(entry.id, content="new content") is True
        assert mem.get(entry.id).content == "new content"

    def test_consolidate(self):
        from core.vector_memory import VectorMemory
        mem = VectorMemory()
        mem.store("duplicate content")
        mem.store("duplicate content")
        mem.store("unique content")
        removed = mem.consolidate()
        assert removed >= 1

    def test_stats(self):
        from core.vector_memory import VectorMemory
        mem = VectorMemory()
        mem.store("test1", importance=0.5)
        mem.store("test2", importance=0.8)
        stats = mem.stats()
        assert stats["count"] == 2
        assert stats["avg_importance"] == 0.65


# ── OpenHands Agent Canvas Tests ───────────────────────────

class TestAgentCanvas:
    def test_conversation(self):
        from core.agent_canvas import AgentCanvas
        canvas = AgentCanvas()
        conv = canvas.create_conversation(title="Test Chat")
        assert conv.id is not None
        assert conv.title == "Test Chat"

    def test_send_message(self):
        from core.agent_canvas import AgentCanvas
        canvas = AgentCanvas()
        conv = canvas.create_conversation()
        msg = canvas.send_message(conv.id, "Hello!")
        assert msg is not None
        assert len(conv.messages) == 2  # user + assistant

    def test_automation(self):
        from core.agent_canvas import AgentCanvas
        canvas = AgentCanvas()
        auto = canvas.create_automation(
            name="Daily Build", trigger="schedule", task="Run build"
        )
        assert auto.name == "Daily Build"
        result = canvas.trigger_automation(auto.id)
        assert result["status"] == "triggered"

    def test_backends(self):
        from core.agent_canvas import AgentCanvas
        canvas = AgentCanvas()
        canvas.register_backend("local", {"type": "local"})
        backends = canvas.list_backends()
        assert len(backends) == 1

    def test_tasks(self):
        from core.agent_canvas import AgentCanvas
        canvas = AgentCanvas()
        canvas.add_task("Fix bug #123")
        canvas.add_task("Add feature")
        tasks = canvas.list_tasks()
        assert len(tasks) == 2

    def test_summary(self):
        from core.agent_canvas import AgentCanvas
        canvas = AgentCanvas()
        canvas.create_conversation()
        canvas.create_automation(name="test")
        canvas.add_task("task")
        s = canvas.summary()
        assert s["conversations"] == 1
        assert s["automations"] == 1
        assert s["tasks"] == 1
