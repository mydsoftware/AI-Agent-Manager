from services.activity_store import ActivityStore


def test_approval_is_persisted_with_fingerprint(tmp_path):
    store = ActivityStore(str(tmp_path / "manager.db"))
    approval = store.create_approval("project-1", "workflow.sensitive-run", "Deploy", fingerprint="abc123")
    assert approval["fingerprint"] == "abc123"
    assert approval["status"] == "pending"


def test_approved_action_is_one_time_consumable(tmp_path):
    store = ActivityStore(str(tmp_path / "manager.db"))
    approval = store.create_approval("project-1", "workflow.sensitive-run", "Deploy", fingerprint="abc123")
    approved = store.resolve_approval(approval["id"], "approved")
    assert approved is not None
    assert approved["status"] == "approved"

    consumed = store.consume_approval(approval["id"])
    assert consumed is not None
    assert consumed["status"] == "consumed"
    assert store.consume_approval(approval["id"]) is None


def test_pending_approval_cannot_be_consumed(tmp_path):
    store = ActivityStore(str(tmp_path / "manager.db"))
    approval = store.create_approval("project-1", "workflow.sensitive-run", "Deploy", fingerprint="abc123")
    assert store.consume_approval(approval["id"]) is None
