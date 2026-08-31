"""Tests for core integrations — MCP, Structured Output, SOP, Self-Healing,
Browser-Use, Tool Adapters, GameDev Skills, Playwright."""

import pytest


# ── MCP Tests ──────────────────────────────────────────────

class TestMCP:
    def test_tool_adapter_conversion(self):
        from core.mcp.tool_adapter import MCPToolAdapter

        class MockTool:
            name = "test_tool"
            description = "A test tool"
            input_schema = {"properties": {"path": {"type": "string"}}, "required": ["path"]}

        mcp = MCPToolAdapter.tool_to_mcp(MockTool())
        assert mcp["name"] == "test_tool"
        assert "path" in mcp["inputSchema"]["properties"]

    def test_mcp_result_format(self):
        from core.mcp.tool_adapter import MCPToolAdapter
        result = MCPToolAdapter.mcp_result("hello world")
        assert result["content"][0]["text"] == "hello world"
        assert result["isError"] is False

    def test_mcp_result_error(self):
        from core.mcp.tool_adapter import MCPToolAdapter
        result = MCPToolAdapter.mcp_result("fail", is_error=True)
        assert result["isError"] is True

    def test_mcp_server_list_tools(self):
        from core.mcp.server import MCPServer
        server = MCPServer()
        server.register_tool("test", lambda: "ok", "Test tool")
        tools = server.list_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "test"

    def test_mcp_server_call_tool(self):
        from core.mcp.server import MCPServer
        server = MCPServer()
        server.register_tool("add", lambda a, b: a + b, "Add numbers")
        result = server.call_tool("add", {"a": 2, "b": 3})
        assert "5" in result["content"][0]["text"]

    def test_mcp_server_call_missing_tool(self):
        from core.mcp.server import MCPServer
        server = MCPServer()
        result = server.call_tool("nonexistent", {})
        assert result["isError"] is True

    def test_mcp_jsonrpc_initialize(self):
        from core.mcp.server import MCPServer
        server = MCPServer()
        resp = server.handle_request({
            "method": "initialize",
            "params": {},
            "id": 1,
        })
        assert resp["result"]["serverInfo"]["name"] == "ai-agent-manager"


# ── Structured Output Tests ────────────────────────────────

class TestStructuredOutput:
    def test_valid_output(self):
        from core.structured_output import StructuredOutput, TASK_SCHEMA
        validator = StructuredOutput(TASK_SCHEMA)
        data, errors = validator.validate_and_repair({
            "id": "t1", "type": "create", "description": "Build feature"
        })
        assert data is not None
        assert errors == []

    def test_repair_missing_fields(self):
        from core.structured_output import StructuredOutput, TASK_SCHEMA
        validator = StructuredOutput(TASK_SCHEMA)
        data, errors = validator.validate_and_repair({})
        # Should be repaired with defaults
        assert data is not None

    def test_invalid_enum_repair(self):
        from core.structured_output import StructuredOutput, TASK_SCHEMA
        validator = StructuredOutput(TASK_SCHEMA)
        data, errors = validator.validate_and_repair({
            "id": "t1", "type": "INVALID", "description": "Test"
        })
        assert data["type"] in TASK_SCHEMA.fields["type"]["enum"]

    def test_game_design_schema(self):
        from core.structured_output import StructuredOutput, GAME_DESIGN_SCHEMA
        validator = StructuredOutput(GAME_DESIGN_SCHEMA)
        data, errors = validator.validate_and_repair({
            "genre": "platformer", "platform": "android", "engine": "godot",
            "mechanics": ["jump", "dash"], "art_style": "pixel"
        })
        assert errors == []


# ── SOP Tests ──────────────────────────────────────────────

class TestSOP:
    def test_sop_steps(self):
        from core.sop import SOFTWARE_DEV_SOP
        assert len(SOFTWARE_DEV_SOP.steps) > 0
        assert SOFTWARE_DEV_SOP.steps[0].name == "research"

    def test_sop_next_step(self):
        from core.sop import SOFTWARE_DEV_SOP
        step = SOFTWARE_DEV_SOP.next_step(set())
        assert step is not None
        assert step.name == "research"

    def test_sop_next_step_after_research(self):
        from core.sop import SOFTWARE_DEV_SOP
        step = SOFTWARE_DEV_SOP.next_step({"requirements"})
        assert step is not None
        assert step.name == "architecture"

    def test_sop_role_filter(self):
        from core.sop import SOFTWARE_DEV_SOP
        dev_steps = SOFTWARE_DEV_SOP.get_steps_for_role("developer")
        assert len(dev_steps) >= 1

    def test_sop_runner(self):
        from core.sop import SOPRunner, SOFTWARE_DEV_SOP
        runner = SOPRunner()
        result = runner.run(SOFTWARE_DEV_SOP)
        assert result["sop"] == "software_development"
        assert len(result["execution_log"]) == len(SOFTWARE_DEV_SOP.steps)

    def test_game_sop(self):
        from core.sop import GAME_DEV_SOP
        assert len(GAME_DEV_SOP.steps) == 12


# ── Self-Healing Tests ─────────────────────────────────────

class TestSelfHealing:
    def test_success_first_try(self):
        from core.self_healing import SelfHealingLoop
        loop = SelfHealingLoop()
        result = loop.run(lambda: "success")
        assert result.success is True
        assert result.final_output == "success"

    def test_repair_after_failure(self):
        from core.self_healing import SelfHealingLoop
        counter = {"n": 0}

        def flaky():
            counter["n"] += 1
            if counter["n"] < 3:
                raise RuntimeError("transient error")
            return "fixed"

        loop = SelfHealingLoop(max_retries=5, backoff_base=0.01)
        result = loop.run(flaky)
        assert result.success is True

    def test_max_retries(self):
        from core.self_healing import SelfHealingLoop
        loop = SelfHealingLoop(max_retries=2, backoff_base=0.01)
        result = loop.run(lambda: (_ for _ in ()).throw(RuntimeError("always fail")))
        assert result.success is False

    def test_loop_detection(self):
        from core.self_healing import SelfHealingLoop
        loop = SelfHealingLoop(max_retries=10, backoff_base=0.01, loop_threshold=3)

        def same_error():
            raise ValueError("same error every time")

        result = loop.run(same_error)
        assert result.success is False
        summary = loop.get_error_summary()
        assert summary["loop_detected"] is True


# ── Browser Use Tests ──────────────────────────────────────

class TestBrowserUse:
    def test_open_page(self):
        from core.browser_use import SmartBrowser, BrowserAction
        browser = SmartBrowser()
        result = browser.execute(BrowserAction(action="open", target="https://example.com"))
        assert result.success is True

    def test_action_sequence(self):
        from core.browser_use import SmartBrowser, BrowserAction
        browser = SmartBrowser()
        results = browser.execute_sequence([
            BrowserAction(action="open", target="https://example.com"),
            BrowserAction(action="click", target="button#submit"),
            BrowserAction(action="screenshot"),
        ])
        assert len(results) == 3
        assert all(r.success for r in results)

    def test_unknown_action(self):
        from core.browser_use import SmartBrowser, BrowserAction
        browser = SmartBrowser()
        result = browser.execute(BrowserAction(action="unknown"))
        assert result.success is False


# ── Tool Adapters Tests ────────────────────────────────────

class TestToolAdapters:
    def test_github_adapter_tools(self):
        from core.tool_adapters import GitHubAdapter
        adapter = GitHubAdapter()
        tools = adapter.list_tools()
        assert len(tools) >= 5
        assert tools[0].service == "github"

    def test_filesystem_adapter_read(self):
        from core.tool_adapters import FilesystemAdapter
        adapter = FilesystemAdapter(".")
        result = adapter.execute("fs_list", {"path": "."})
        assert "entries" in result

    def test_adapter_registry(self):
        from core.tool_adapters import AdapterRegistry, FilesystemAdapter, BrowserAdapter
        registry = AdapterRegistry()
        registry.register(FilesystemAdapter())
        registry.register(BrowserAdapter())
        tools = registry.list_all_tools()
        assert len(tools) >= 10

    def test_registry_status(self):
        from core.tool_adapters import create_default_registry
        registry = create_default_registry()
        status = registry.status()
        assert "github" in status
        assert "filesystem" in status
        assert "browser" in status


# ── GameDev Skills Tests ───────────────────────────────────

class TestGameDevSkills:
    def test_route_godot_platformer(self):
        from core.gamedev_skills import SkillRouter
        router = SkillRouter()
        skills = router.route("godot", "platformer mechanics with double jump")
        assert len(skills) >= 2
        engine_skills = [s for s in skills if s.engine == "godot"]
        assert len(engine_skills) >= 1

    def test_route_any_ai(self):
        from core.gamedev_skills import SkillRouter
        router = SkillRouter()
        skills = router.route("godot", "enemy AI patrol and chase")
        assert len(skills) >= 1

    def test_list_by_engine(self):
        from core.gamedev_skills import SkillRouter
        router = SkillRouter()
        godot_skills = router.list_by_engine("godot")
        assert len(godot_skills) >= 5

    def test_total_skills(self):
        from core.gamedev_skills import SkillRouter
        router = SkillRouter()
        assert len(router.list_all()) >= 25


# ── Playwright Adapter Tests ───────────────────────────────

class TestPlaywright:
    def test_adapter_init(self):
        from core.playwright_adapter import PlaywrightAdapter
        adapter = PlaywrightAdapter()
        # Playwright may or may not be installed
        assert isinstance(adapter.is_available(), bool)

    def test_verify_deployment_mock(self):
        from core.playwright_adapter import PlaywrightAdapter
        adapter = PlaywrightAdapter()
        result = adapter.verify_deployment("https://example.com")
        assert "tests" in result
        assert "all_passed" in result
