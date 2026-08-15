import json

from bridge.worker import main


def test_bridge_request_contract(tmp_path, monkeypatch):
    request_file = tmp_path / "request.json"
    request_file.write_text(json.dumps({"request": "ساخت سایت فروشگاهی", "repository": "mydsoftware/demo", "branch": "ai-agent/demo"}), encoding="utf-8")

    class FakeRuntime:
        def run(self, request, agent):
            return None

    class FakeBuilder:
        def build(self, **kwargs):
            class Result:
                repository = kwargs["repository"]
                branch = kwargs["branch"]
                files = ["index.html"]
                pull_request = "https://github.com/mydsoftware/demo/pull/1"
            return Result()

    monkeypatch.setattr("bridge.worker.ManagerRuntime", FakeRuntime)
    monkeypatch.setattr("bridge.worker.ProjectBuilder", lambda: FakeBuilder())
    monkeypatch.chdir(tmp_path)
    assert main(str(request_file)) == 0
    result = json.loads((tmp_path / "agent_results/request.json").read_text(encoding="utf-8"))
    assert result["status"] == "completed"
    assert result["files"] == ["index.html"]
