from __future__ import annotations

from flask import Flask, jsonify, request

from api.agent_team_api import AgentTeamAPI
from agents.wordpress_connection_http_api import WordPressConnectionHttpApi
from manager.request_router import route_request
from manager.workflow_engine import WorkflowEngine
from manager.approval_policy import sensitive_tasks
from services.activity_store import ActivityStore
from services.project_store import ProjectStore
from services.workflow_store import WorkflowStore
from runtime import ManagerRuntime


def _has_cycle(tasks: list[dict]) -> bool:
    """وجود چرخه در Dependencyهای Workflow را بررسی می‌کند."""
    graph = {str(task["id"]): [str(dep) for dep in task.get("depends_on", [])] for task in tasks}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting: return True
        if node in visited: return False
        visiting.add(node)
        for dependency in graph.get(node, []):
            if visit(dependency): return True
        visiting.remove(node); visited.add(node); return False

    return any(visit(node) for node in graph)


def _approval_gate(project_id: str, tasks: list, activity: ActivityStore) -> tuple[bool, dict | None]:
    """برای Taskهای حساس، اجرای Workflow را تا تأیید کاربر متوقف می‌کند."""
    sensitive = sensitive_tasks(tasks)
    if not sensitive:
        return True, None
    approvals = activity.approvals(project_id)
    action = "workflow.sensitive-run"
    pending = next((item for item in approvals if item.get("action") == action and item.get("status") == "pending"), None)
    if pending:
        return False, {"approval_required": True, "approval": pending}
    approved = next((item for item in approvals if item.get("action") == action and item.get("status") == "approved"), None)
    if approved:
        return True, None
    approval = activity.create_approval(
        project_id,
        action,
        "اجرای Workflow شامل عملیات حساس است: " + ", ".join(task.title for task in sensitive),
    )
    activity.add(project_id, "approval.required", "اجرای Workflow تا تأیید عملیات حساس متوقف شد.")
    return False, {"approval_required": True, "approval": approval}

def _merge_report_into_workflow(workflow_data: dict, report: dict) -> dict:
    """وضعیت واقعی اجرای Taskها را داخل Snapshot ذخیره‌شده Workflow می‌نشاند."""
    by_id = {str(item.get("id")): item for item in report.get("tasks", [])}
    for task in workflow_data.get("tasks", []):
        runtime_task = by_id.get(str(task.get("id")))
        if runtime_task is None: continue
        task["status"] = runtime_task.get("status", task.get("status", "pending"))
        task["result"] = runtime_task.get("result")
        task["error"] = runtime_task.get("error")
        task["attempts"] = runtime_task.get("attempts", task.get("attempts", 0))
    return workflow_data


def create_app(team_api: AgentTeamAPI, runtime: ManagerRuntime | None = None,
               wordpress_connection_api: WordPressConnectionHttpApi | None = None,
               project_store: ProjectStore | None = None,
               activity_store: ActivityStore | None = None,
               workflow_store: WorkflowStore | None = None) -> Flask:
    """برنامه HTTP مدیریتی، پروژه، Workflow، Activity و Approval را می‌سازد."""
    app = Flask(__name__)
    manager_runtime = runtime or ManagerRuntime()
    runtime_for_project = manager_runtime
    connection_api = wordpress_connection_api or WordPressConnectionHttpApi()
    projects = project_store or ProjectStore()
    activity = activity_store or ActivityStore(projects.database_path)
    workflows = workflow_store or WorkflowStore(projects.database_path)
    workflow = WorkflowEngine(manager_runtime)

    @app.get("/api/agents")
    def list_agents(): return jsonify(team_api.list_agents())

    @app.post("/api/agents/create")
    def create_agent():
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip(); description = str(payload.get("description", "")).strip(); system_prompt = str(payload.get("system_prompt", "")).strip(); capabilities = payload.get("capabilities", [])
        if not name or not description or not system_prompt: return jsonify({"error": "name، description و system_prompt الزامی هستند."}), 400
        if not isinstance(capabilities, list): return jsonify({"error": "capabilities باید آرایه باشد."}), 400
        capabilities = [str(item).strip() for item in capabilities if str(item).strip()]
        if len(name) > 80 or len(description) > 500 or len(system_prompt) > 12000: return jsonify({"error": "طول یکی از فیلدها بیش از حد مجاز است."}), 400
        try: record = manager_runtime.create_custom_agent(name, description, system_prompt, capabilities)
        except ValueError as error: return jsonify({"error": str(error)}), 400
        return jsonify(record), 201

    @app.get("/api/agents/custom")
    def list_custom_agents(): return jsonify(manager_runtime.agent_store.list())

    @app.delete("/api/agents/custom/<name>")
    def delete_custom_agent(name: str):
        if name in {"developer", "research", "qa", "security", "github", "github-project", "website-audit-runner"}: return jsonify({"error": "ایجنت‌های هسته قابل حذف نیستند."}), 400
        return (jsonify({"deleted": True, "name": name}) if manager_runtime.delete_custom_agent(name) else (jsonify({"error": "ایجنت سفارشی پیدا نشد."}), 404))

    @app.post("/api/agents/<name>/enable")
    def enable_agent(name: str): return jsonify(team_api.enable(name))

    @app.post("/api/agents/<name>/disable")
    def disable_agent(name: str): return jsonify(team_api.disable(name))

    @app.post("/api/run")
    def run_request():
        payload = request.get_json(silent=True) or {}; text = str(payload.get("request", "")).strip(); agent = str(payload.get("agent", "developer")).strip() or "developer"
        if not text: return jsonify({"error": "فیلد request الزامی است."}), 400
        return jsonify(manager_runtime.run(text, agent).to_dict())

    @app.post("/api/route")
    def route_request_api():
        payload = request.get_json(silent=True) or {}; text = str(payload.get("request", "")).strip()
        if not text: return jsonify({"error": "فیلد request الزامی است."}), 400
        return jsonify(route_request(text).__dict__)

    @app.post("/api/workflow/plan")
    def plan_workflow():
        payload = request.get_json(silent=True) or {}; text = str(payload.get("request", "")).strip(); agent = str(payload.get("agent", "")).strip() or None
        if not text: return jsonify({"error": "فیلد request الزامی است."}), 400
        try: return jsonify(workflow.plan(text, agent).to_dict())
        except (KeyError, PermissionError, ValueError) as error: return jsonify({"error": str(error)}), 400

    @app.post("/api/workflow/run")
    def run_workflow():
        payload = request.get_json(silent=True) or {}; text = str(payload.get("request", "")).strip(); agent = str(payload.get("agent", "")).strip() or None
        if not text: return jsonify({"error": "فیلد request الزامی است."}), 400
        try: return jsonify(workflow.execute(text, agent))
        except (KeyError, PermissionError, ValueError) as error: return jsonify({"error": str(error)}), 400

    @app.get("/api/projects")
    def list_projects(): return jsonify(projects.list())

    @app.post("/api/project/create")
    def create_project():
        payload = request.get_json(silent=True) or {}; name, description, project_request = (str(payload.get(k, "")).strip() for k in ("name", "description", "request"))
        if not name or not description or not project_request: return jsonify({"error": "name، description و request الزامی هستند."}), 400
        project = projects.create(name=name, description=description, request=project_request, project_type=str(payload.get("project_type", "other")), is_private=bool(payload.get("private", True))); activity.add(project["id"], "project.created", "پروژه ایجاد شد."); return jsonify(project), 201

    @app.get("/api/project/<project_id>")
    def get_project(project_id: str):
        project = projects.get(project_id)
        return jsonify(project) if project else (jsonify({"error": "پروژه پیدا نشد."}), 404)

    @app.get("/api/project/<project_id>/workflow")
    def get_project_workflow(project_id: str):
        project = projects.get(project_id)
        if not project: return jsonify({"error": "پروژه پیدا نشد."}), 404
        saved = workflows.get(project_id)
        if saved: return jsonify(saved["workflow"])
        try:
            plan = workflow.plan(project["request"]).to_dict(); workflows.save(project_id, plan); return jsonify(plan)
        except (KeyError, PermissionError, ValueError) as error: return jsonify({"error": str(error)}), 400

    @app.put("/api/project/<project_id>/workflow")
    def update_project_workflow(project_id: str):
        if not projects.get(project_id): return jsonify({"error": "پروژه پیدا نشد."}), 404
        payload = request.get_json(silent=True) or {}; plan = payload.get("workflow", payload)
        if not isinstance(plan, dict) or not isinstance(plan.get("tasks"), list): return jsonify({"error": "workflow باید شامل tasks باشد."}), 400
        tasks = plan["tasks"]; ids = [str(t.get("id", "")).strip() for t in tasks if isinstance(t, dict)]
        if len(ids) != len(tasks) or not all(ids) or len(set(ids)) != len(ids): return jsonify({"error": "شناسه Taskها باید یکتا و معتبر باشند."}), 400
        id_set = set(ids)
        for task in tasks:
            if not isinstance(task, dict) or not str(task.get("title", "")).strip() or not str(task.get("agent", "")).strip(): return jsonify({"error": "هر Task باید title و agent داشته باشد."}), 400
            deps = task.get("depends_on", [])
            if not isinstance(deps, list) or any(str(dep) not in id_set for dep in deps) or str(task["id"]) in {str(dep) for dep in deps}: return jsonify({"error": "Dependencyهای Workflow نامعتبر هستند."}), 400
        if _has_cycle(tasks): return jsonify({"error": "چرخه در Dependencyهای Workflow مجاز نیست."}), 400
        plan["edges"] = [{"from": dep, "to": task["id"]} for task in tasks for dep in task.get("depends_on", [])]
        saved = workflows.save(project_id, plan); activity.add(project_id, "workflow.updated", "Workflow توسط کاربر ویرایش و ذخیره شد."); return jsonify(saved["workflow"])

    @app.post("/api/project/<project_id>/workflow/run")
    def run_saved_workflow(project_id: str):
        project = projects.get(project_id)
        if not project: return jsonify({"error": "پروژه پیدا نشد."}), 404
        saved = workflows.get(project_id)
        if not saved: return jsonify({"error": "Workflow ذخیره‌شده وجود ندارد."}), 404
        from manager.task import Task
        from manager.task_status import TaskStatus
        tasks = [Task(id=str(raw["id"]), title=str(raw["title"]), description=str(raw.get("description", "")), agent=str(raw["agent"]), depends_on=[str(x) for x in raw.get("depends_on", [])], status=TaskStatus.PENDING, max_attempts=int(raw.get("max_attempts", 5))) for raw in saved["workflow"].get("tasks", [])]
        allowed, gate = _approval_gate(project_id, tasks, activity)
        if not allowed:
            return jsonify(gate), 409
        projects.set_status(project_id, "running"); activity.add(project_id, "workflow.running", "Workflow ویرایش‌شده در حال اجراست.")
        try:
            report = manager_runtime.run_tasks(tasks); report_data = report.to_dict(); final = "completed" if report_data.get("status") in {"success", "completed"} else "failed"; projects.set_status(project_id, final)
            updated_workflow = _merge_report_into_workflow(saved["workflow"], report_data); workflows.save(project_id, updated_workflow)
            activity.add(project_id, "workflow.completed" if final == "completed" else "workflow.failed", f"اجرای Workflow ویرایش‌شده: {final}")
            return jsonify({"workflow": updated_workflow, "report": report_data, "project": projects.get(project_id)})
        except Exception as error:
            projects.set_status(project_id, "failed"); activity.add(project_id, "workflow.failed", str(error)); return jsonify({"error": str(error)}), 500

    @app.post("/api/project/<project_id>/run")
    def run_project(project_id: str):
        project = projects.get(project_id)
        if not project: return jsonify({"error": "پروژه پیدا نشد."}), 404
        payload = request.get_json(silent=True) or {}; text = str(payload.get("request", "")).strip() or str(project["request"]).strip(); agent = str(payload.get("agent", "")).strip() or None
        _ = runtime_for_project
        try:
            projects.set_status(project_id, "planning"); activity.add(project_id, "workflow.planning", "برنامه Workflow ساخته شد."); plan = workflow.plan(text, agent); gate_tasks = plan.tasks; allowed, gate = _approval_gate(project_id, gate_tasks, activity)
            if not allowed:
                projects.set_status(project_id, "paused"); return jsonify(gate), 409
            execution = workflow.execute(text, agent); report = execution["report"]; final = "completed" if report.get("status") in {"success", "completed"} else "failed"; projects.set_status(project_id, final)
            execution["workflow"] = _merge_report_into_workflow(execution["workflow"], report); activity.add(project_id, "workflow.completed" if final == "completed" else "workflow.failed", f"اجرای Workflow: {final}"); workflows.save(project_id, execution["workflow"])
            return jsonify({"project": projects.get(project_id), "workflow": execution["workflow"], "report": report})
        except Exception as error:
            projects.set_status(project_id, "failed"); activity.add(project_id, "workflow.failed", str(error)); return jsonify({"error": "اجرای پروژه ناموفق بود.", "detail": str(error)}), 500

    @app.post("/api/project/<project_id>/workflow/plan")
    def project_workflow_plan(project_id: str):
        project = projects.get(project_id)
        if not project: return jsonify({"error": "پروژه پیدا نشد."}), 404
        saved = workflows.get(project_id)
        if saved: return jsonify(saved["workflow"])
        try:
            plan = workflow.plan(project["request"]).to_dict(); workflows.save(project_id, plan); return jsonify(plan)
        except (KeyError, PermissionError, ValueError) as error: return jsonify({"error": str(error)}), 400

    @app.post("/api/project/<project_id>/status")
    def update_project_status(project_id: str):
        payload = request.get_json(silent=True) or {}; status = str(payload.get("status", "")).strip()
        if not status: return jsonify({"error": "فیلد status الزامی است."}), 400
        try: project = projects.set_status(project_id, status)
        except ValueError as error: return jsonify({"error": str(error)}), 400
        if project is None: return jsonify({"error": "پروژه پیدا نشد."}), 404
        activity.add(project_id, "project.status", f"وضعیت به {status} تغییر کرد."); return jsonify(project)

    @app.get("/api/project/<project_id>/activity")
    def project_activity(project_id: str):
        if not projects.get(project_id): return jsonify({"error": "پروژه پیدا نشد."}), 404
        return jsonify(activity.list(project_id))

    @app.get("/api/approvals")
    def list_approvals(): return jsonify(activity.approvals(request.args.get("project_id")))

    @app.post("/api/project/<project_id>/approvals")
    def create_approval(project_id: str):
        if not projects.get(project_id): return jsonify({"error": "پروژه پیدا نشد."}), 404
        payload = request.get_json(silent=True) or {}; action, description = str(payload.get("action", "")).strip(), str(payload.get("description", "")).strip()
        if not action or not description: return jsonify({"error": "action و description الزامی هستند."}), 400
        item = activity.create_approval(project_id, action, description); activity.add(project_id, "approval.created", f"تأییدیه ایجاد شد: {action}"); return jsonify(item), 201

    @app.post("/api/approvals/<approval_id>/resolve")
    def resolve_approval(approval_id: str):
        payload = request.get_json(silent=True) or {}; status = str(payload.get("status", "")).strip().lower()
        if status not in {"approved", "rejected"}: return jsonify({"error": "status باید approved یا rejected باشد."}), 400
        item = activity.resolve_approval(approval_id, status)
        if item is None: return jsonify({"error": "Approval پیدا نشد یا قبلاً تعیین تکلیف شده است."}), 404
        activity.add(item["project_id"], "approval.resolved", f"تأییدیه {approval_id}: {status}"); return jsonify(item)

    @app.get("/api/health")
    def health(): return jsonify({"status": "ok"})

    return app
