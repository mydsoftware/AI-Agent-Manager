from manager.audit_log import AuditLog


def test_audit_log_records_and_exports_events():
    log = AuditLog()
    event = log.record("task.completed", "build", "success", {"artifact": "site.zip"})
    assert event.task_id == "build"
    exported = log.export()
    assert len(exported) == 1
    assert exported[0]["event"] == "task.completed"
    assert exported[0]["status"] == "success"
