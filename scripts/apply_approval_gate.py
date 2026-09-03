from __future__ import annotations

from pathlib import Path

HTTP = Path("api/http.py")


def patch() -> None:
    text = HTTP.read_text(encoding="utf-8")
    if "from manager.approval_policy import sensitive_tasks" not in text:
        text = text.replace(
            "from manager.workflow_engine import WorkflowEngine\n",
            "from manager.workflow_engine import WorkflowEngine\nfrom manager.approval_policy import sensitive_tasks\n",
            1,
        )

    marker = "\ndef _merge_report_into_workflow"
    helper = '''\ndef _approval_gate(project_id: str, tasks: list, activity: ActivityStore) -> tuple[bool, dict | None]:\n    """برای Taskهای حساس، اجرای Workflow را تا تأیید کاربر متوقف می‌کند."""\n    sensitive = sensitive_tasks(tasks)\n    if not sensitive:\n        return True, None\n    approvals = activity.approvals(project_id)\n    action = "workflow.sensitive-run"\n    pending = next((item for item in approvals if item.get("action") == action and item.get("status") == "pending"), None)\n    if pending:\n        return False, {"approval_required": True, "approval": pending}\n    approved = next((item for item in approvals if item.get("action") == action and item.get("status") == "approved"), None)\n    if approved:\n        return True, None\n    approval = activity.create_approval(\n        project_id,\n        action,\n        "اجرای Workflow شامل عملیات حساس است: " + ", ".join(task.title for task in sensitive),\n    )\n    activity.add(project_id, "approval.required", "اجرای Workflow تا تأیید عملیات حساس متوقف شد.")\n    return False, {"approval_required": True, "approval": approval}\n'''
    if "def _approval_gate(" not in text:
        text = text.replace(marker, helper + marker, 1)

    old = '''        projects.set_status(project_id, "running"); activity.add(project_id, "workflow.running", "Workflow ویرایش‌شده در حال اجراست.")\n        try:\n'''
    new = '''        allowed, gate = _approval_gate(project_id, tasks, activity)\n        if not allowed:\n            return jsonify(gate), 409\n        projects.set_status(project_id, "running"); activity.add(project_id, "workflow.running", "Workflow ویرایش‌شده در حال اجراست.")\n        try:\n'''
    if old in text and "_approval_gate(project_id, tasks, activity)" not in text:
        text = text.replace(old, new, 1)

    old_project = '''            projects.set_status(project_id, "planning"); activity.add(project_id, "workflow.planning", "برنامه Workflow ساخته شد."); execution = workflow.execute(text, agent); report = execution["report"]; final = "completed" if report.get("status") in {"success", "completed"} else "failed"; projects.set_status(project_id, final)\n'''
    new_project = '''            projects.set_status(project_id, "planning"); activity.add(project_id, "workflow.planning", "برنامه Workflow ساخته شد."); plan = workflow.plan(text, agent); gate_tasks = plan.tasks; allowed, gate = _approval_gate(project_id, gate_tasks, activity)\n            if not allowed:\n                projects.set_status(project_id, "paused"); return jsonify(gate), 409\n            execution = workflow.execute(text, agent); report = execution["report"]; final = "completed" if report.get("status") in {"success", "completed"} else "failed"; projects.set_status(project_id, final)\n'''
    if old_project in text and "gate_tasks = plan.tasks" not in text:
        text = text.replace(old_project, new_project, 1)

    HTTP.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    patch()
