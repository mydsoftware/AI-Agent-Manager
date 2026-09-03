from __future__ import annotations

import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_KEY = os.getenv("AI_AGENT_MANAGER_API_KEY", "")

AGENTS = {
    "developer": {"name": "توسعه‌دهنده", "icon": "💻", "desc": "بررسی و توسعه کد"},
    "researcher": {"name": "پژوهشگر", "icon": "🔍", "desc": "تحقیق و جمع‌آوری اطلاعات"},
    "qa": {"name": "کنترل کیفیت", "icon": "✅", "desc": "تست و کنترل کیفیت"},
    "github": {"name": "گیت‌هاب", "icon": "🐙", "desc": "عملیات GitHub"},
    "website-audit": {"name": "ممیزی سایت", "icon": "🌐", "desc": "ممیزی کامل سایت"},
    "wordpress-factory": {"name": "کارخانه وردپرس", "icon": "🔧", "desc": "ساخت و راه‌اندازی وردپرس"},
    "wordpress-security": {"name": "امنیت وردپرس", "icon": "🔒", "desc": "بررسی امنیت وردپرس"},
    "wordpress-performance": {"name": "عملکرد وردپرس", "icon": "⚡", "desc": "بهینه‌سازی عملکرد"},
    "wordpress-seo": {"name": "SEO وردپرس", "icon": "📈", "desc": "بهینه‌سازی موتور جستجو"},
    "wordpress-ui": {"name": "رابط کاربری وردپرس", "icon": "🎨", "desc": "طراحی و رابط کاربری"},
}


def api_call(endpoint: str, method: str = "GET", data: dict | None = None) -> dict:
    """فراخوانی امن API مرکزی."""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=30)
        else:
            response = requests.post(f"{API_BASE}{endpoint}", headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": str(exc)}
    except ValueError:
        return {"error": "پاسخ نامعتبر از API مرکزی"}


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, X-Execution-ID"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/")
def landing():
    return render_template("index.html", agents=AGENTS)


@app.route("/app")
def command_center():
    return render_template("dashboard.html", agents=AGENTS, health=api_call("/api/health"), api_base=API_BASE)


@app.route("/execute")
def execute_page():
    return render_template("execute.html", agents=AGENTS)


@app.route("/audit")
def audit_page():
    return render_template("audit.html")


@app.route("/projects")
def projects_page():
    return render_template("projects.html", agents=AGENTS)


@app.route("/projects/workspace")
def project_workspace():
    return render_template("project_workspace.html", agents=AGENTS)


@app.route("/api/execute", methods=["POST"])
def api_execute():
    data = request.get_json(silent=True) or {}
    request_text = str(data.get("request", "")).strip()
    agent = str(data.get("agent", "developer")).strip() or "developer"
    if not request_text:
        return jsonify({"error": "درخواست نمی‌تواند خالی باشد"}), 400
    result = api_call("/api/run", "POST", {"request": request_text, "agent": agent})
    return jsonify(result)


@app.route("/api/route", methods=["POST"])
def api_route():
    data = request.get_json(silent=True) or {}
    request_text = str(data.get("request", "")).strip()
    if not request_text:
        return jsonify({"error": "درخواست نمی‌تواند خالی باشد"}), 400
    return jsonify(api_call("/api/route", "POST", {"request": request_text}))


@app.route("/api/projects", methods=["GET"])
def api_projects():
    return jsonify(api_call("/api/projects"))


@app.route("/api/project/create", methods=["POST"])
def api_project_create():
    return jsonify(api_call("/api/project/create", "POST", request.get_json(silent=True) or {}))


@app.route("/api/project/<project_id>")
def api_project(project_id: str):
    return jsonify(api_call(f"/api/project/{project_id}"))


@app.route("/api/audit", methods=["POST"])
def api_audit():
    data = request.get_json(silent=True) or {}
    url = str(data.get("url", "")).strip()
    if not url:
        return jsonify({"error": "URL الزامی است"}), 400
    return jsonify(api_call("/api/run", "POST", {"request": f"ممیزی سایت {url}", "agent": "website-audit"}))


@app.route("/api/proxy/<path:endpoint>", methods=["GET", "POST"])
def api_proxy(endpoint):
    payload = request.get_json(silent=True) or {}
    return jsonify(api_call(f"/{endpoint}", request.method, payload if request.method == "POST" else None))


@app.route("/api/session/start", methods=["POST"])
def api_session_start():
    return jsonify(api_call("/api/session/start", "POST", request.get_json(silent=True) or {}))


@app.route("/api/session/answer", methods=["POST"])
def api_session_answer():
    return jsonify(api_call("/api/session/answer", "POST", request.get_json(silent=True) or {}))


@app.route("/api/executions/<execution_id>")
def api_executions(execution_id):
    return jsonify(api_call(f"/api/executions/{execution_id}"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
