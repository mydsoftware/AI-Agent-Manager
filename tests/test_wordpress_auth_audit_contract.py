from pathlib import Path


def test_wordpress_auth_and_audit_contract():
    plugin_root = Path("wordpress-plugin/ai-agent-manager-seo/includes")
    auth = (plugin_root / "class-ai-agent-auth.php").read_text(encoding="utf-8")
    log = (plugin_root / "class-ai-agent-audit-log.php").read_text(encoding="utf-8")

    assert "X-AI-Agent-Token" in auth
    assert "hash_equals" in auth
    assert "ai_agent_manager_audit_log" in log
    assert "application_password" not in log
    assert "ai_agent_manager_token" not in log
