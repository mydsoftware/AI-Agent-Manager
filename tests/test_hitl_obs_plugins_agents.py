from pathlib import Path

from agents.database_agent import DatabaseAgent
from agents.documentation_agent import DocumentationAgent
from core.hitl.approvals import ApprovalGateway, RiskLevel
from core.observability.tracer import Tracer
from core.plugins.manager import PluginManager
from multimodal.pipeline import AssetManager, AssetRequest


def test_hitl_flow_and_expiry() -> None:
    gw = ApprovalGateway(expiry_seconds=0.05, auto_approve_low=True)
    low = gw.request("read file", risk=RiskLevel.LOW)
    assert low.status == "auto_approved"
    high = gw.request("deploy", {"target": "prod"})
    assert high.risk == RiskLevel.CRITICAL
    assert high.status == "pending"
    gw.decide(high.id, True, "ok", "alice")
    assert gw.is_allowed(high)
    stale = gw.request("git push", {})
    stale.created_at -= 10
    gw.expire_stale()
    assert stale.status == "expired"


def test_mock_assets(tmp_path: Path) -> None:
    mgr = AssetManager(str(tmp_path))
    res = mgr.generate(AssetRequest(kind="image", prompt="forest tile", project_id="game1"))
    assert Path(res.path).exists()
    assert res.provider == "mock"


def test_database_and_docs_agents() -> None:
    db = DatabaseAgent()
    docs = DocumentationAgent()

    class T:
        description = "design schema for inventory"

    class T2:
        description = "generate README for inventory api"

    schema = db.run(T())
    assert "CREATE TABLE" in schema
    readme = docs.run(T2())
    assert "README" in readme


def test_tracer(tmp_path: Path) -> None:
    tr = Tracer(str(tmp_path / "t.db"))
    tr.emit(project_id="p", task_id="t1", agent="developer", event="run", tokens=12)
    tr.emit(project_id="p", task_id="t1", agent="developer", event="error", error="boom", tokens=0)
    summary = tr.task_summary("t1")
    assert summary["tokens"] == 12
    assert summary["errors"] == 1


def test_plugin_load_and_reject(tmp_path: Path) -> None:
    good = tmp_path / "good"
    good.mkdir()
    (good / "plugin.json").write_text(
        '{"name":"echo","version":"1","description":"d","type":"tool","entrypoint":"echo.py","permissions":["tools.register"]}',
        encoding="utf-8",
    )
    (good / "echo.py").write_text("PLUGIN_NAME='echo'\n", encoding="utf-8")
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "plugin.json").write_text(
        '{"name":"evil","type":"virus","entrypoint":"x.py","permissions":["root"]}',
        encoding="utf-8",
    )
    pm = PluginManager(str(tmp_path))
    pm.load_all()
    assert "echo" in pm.loaded
    assert pm.errors
