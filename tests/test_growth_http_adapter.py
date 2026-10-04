import json
from unittest.mock import patch

from manager.growth_actions import GrowthAction
from manager.growth_http_adapter import HTTPGrowthAdapter


class FakeResponse:
    status = 200

    def read(self):
        return json.dumps({"ok": True}).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_http_adapter_posts_action_payload():
    action = GrowthAction("create_lead", "lead_generation", {"name": "Mohammad"})

    with patch("manager.growth_http_adapter.urllib.request.urlopen", return_value=FakeResponse()) as call:
        result = HTTPGrowthAdapter("https://crm.example/api", "token").execute(action)

    request = call.call_args.args[0]
    assert request.full_url == "https://crm.example/api/create_lead"
    assert request.get_header("Authorization") == "Bearer token"
    assert result["status"] == "executed"
    assert result["external_execution"] is True
