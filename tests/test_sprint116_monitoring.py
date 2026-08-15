from manager.monitoring import Monitor


def test_monitor_health_tracks_execution():
    monitor = Monitor()
    monitor.task_started()
    monitor.task_completed()
    monitor.task_started()
    monitor.task_failed()
    health = monitor.health()
    assert health["status"] == "degraded"
    assert health["active_tasks"] == 0
    assert health["completed_tasks"] == 1
    assert health["failed_tasks"] == 1
