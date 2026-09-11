from services.activity_store import ActivityStore


def test_approval_is_persisted_with_fingerprint(tmp_path):
    store = ActivityStore(str(tmp_path / "manager.db"))
    approval = store.create_approval("project-1", "workflow.sensitive-run", "Deploy", fingerprint="abc123")
    assert approval["fingerprint"] == "abc123"
    assert approval["status"] == "pending"


def test_approved_action_is_atomically_claimed_and_consumed(tmp_path):
    store = ActivityStore(str(tmp_path / "manager.db"))
    approval = store.create_approval("project-1", "workflow.sensitive-run", "Deploy", fingerprint="abc123")
    approved = store.resolve_approval(approval["id"], "approved")
    assert approved is not None
    assert approved["status"] == "approved"

    claimed = store.claim_approval(approval["id"], "abc123")
    assert claimed is not None
    assert claimed["status"] == "claimed"
    assert store.claim_approval(approval["id"], "abc123") is None

    consumed = store.consume_approval(approval["id"])
    assert consumed is not None
    assert consumed["status"] == "consumed"
    assert store.consume_approval(approval["id"]) is None


def test_pending_approval_cannot_be_consumed_or_claimed(tmp_path):
    store = ActivityStore(str(tmp_path / "manager.db"))
    approval = store.create_approval("project-1", "workflow.sensitive-run", "Deploy", fingerprint="abc123")
    assert store.consume_approval(approval["id"]) is None
    assert store.claim_approval(approval["id"], "abc123") is None


def test_claimed_approval_can_be_released_after_failure(tmp_path):
    store = ActivityStore(str(tmp_path / "manager.db"))
    approval = store.create_approval("project-1", "workflow.sensitive-run", "Deploy", fingerprint="abc123")
    store.resolve_approval(approval["id"], "approved")
    store.claim_approval(approval["id"], "abc123")
    released = store.release_approval(approval["id"], "abc123")
    assert released is not None
    assert released["status"] == "approved"
