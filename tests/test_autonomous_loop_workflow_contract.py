from pathlib import Path


def test_autonomous_loop_workflow_exists_and_accepts_request():
    workflow = Path(".github/workflows/autonomous-agent-loop.yml")
    assert workflow.exists()
    text = workflow.read_text(encoding="utf-8")
    assert "AGENT_REQUEST" in text
    assert "SessionRuntime" in text
    assert "workflow_dispatch" in text
