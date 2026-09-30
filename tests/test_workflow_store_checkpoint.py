from services.workflow_store import WorkflowStore


def test_workflow_store_persists_and_resumes_checkpoint(tmp_path):
    store = WorkflowStore(str(tmp_path / "platform.db"))
    workflow = {"id": "wf-1", "tasks": [{"id": "t1", "status": "pending"}]}

    saved = store.save("p1", workflow)
    assert saved["state"] == "planned"
    assert saved["phase"] == "planned"

    checkpoint = store.transition(
        "p1",
        "running",
        attempts=2,
        phase="executing",
        current_task="t1",
        head_sha="abc123",
        preview_url="https://preview.example",
    )
    assert checkpoint["state"] == "running"
    assert checkpoint["attempts"] == 2
    assert checkpoint["phase"] == "executing"
    assert checkpoint["current_task"] == "t1"
    assert checkpoint["head_sha"] == "abc123"
    assert checkpoint["preview_url"] == "https://preview.example"

    resumed = store.get("p1")
    assert resumed == checkpoint


def test_checkpoint_transition_preserves_unspecified_fields(tmp_path):
    store = WorkflowStore(str(tmp_path / "platform.db"))
    store.save("p1", {"id": "wf-1", "tasks": []}, head_sha="abc", preview_url="https://preview.example")
    updated = store.transition("p1", "failed", phase="repairing", last_error="boom")
    assert updated["head_sha"] == "abc"
    assert updated["preview_url"] == "https://preview.example"
    assert updated["phase"] == "repairing"
    assert updated["last_error"] == "boom"
