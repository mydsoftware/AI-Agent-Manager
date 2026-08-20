import json
from pathlib import Path


def test_germantechsat_request_has_execution_contract():
    path = Path("agent_requests/20260820-germantechsat.json")
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["agent"] == "website-audit"
    assert data["url"].startswith("https://")
    assert data["description"]


def test_result_contract_fields_are_documented():
    text = Path("docs/chatgpt-execution-bridge.md").read_text(encoding="utf-8")
    for field in ("status", "request_id", "agent", "url", "report", "error"):
        assert field in text
