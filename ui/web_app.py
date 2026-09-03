from __future__ import annotations

import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8080")
API_KEY = os.getenv("AI_AGENT_MANAGER_API_KEY", "test-key-for-development")

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
    """فراخوانی API مرکزی."""
    headers = {"Content-Type": "application/json"}
    if API_KEY and API_KEY != "test-key-for-development":
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
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, X-Execution-ID"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/")
def landing():
    return render_template("index.html", agents=AGENTS)


@app.route("/app")
def command_center():
    health = api_call("/health")
    return render_template("dashboard.html", agents=AGENTS, health=health, api_base=API_BASE)


@app.route("/execute")
def execute_page():
    return render_template("execute.html", agents=AGENTS)


@app.route("/audit")
def audit_page():
    return render_template("audit.html")


@app.route("/projects")
def projects_page():
    return render_template("projects.html")


@app.route("/api/execute", methods=["POST"])
def api_execute():
    data = request.get_json(silent=True) or {}
    request_text = data.get("request", "").strip()
    agent = data.get("agent", "developer")
    if not request_text:
        return jsonify({"error": "درخواست نمی‌تواند خالی باشد"}), 400
    return jsonify(api_call("/execute", "POST", {"request": request_text, "agent": agent}))


@app.route("/api/proxy/<path:endpoint>", methods=["GET", "POST"])
def api_proxy(endpoint):
    if request.method == "GET":
        result = api_call(f"/{endpoint}")
    else:
        result = api_call(f"/{endpoint}", "POST", request.get_json(silent=True) or {})
    return jsonify(result)


@app.route("/api/audit", methods=["POST"])
def api_audit():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    mode = data.get("mode", "pre_contract")
    if not url:
        return jsonify({"error": "URL الزامی است"}), 400
    result = api_call("/execute/website-audit", "POST", {
        "request_id": f"exec-{hash(url) % 10000}",
        "url": url,
        "mode": mode,
        "language": "fa",
    })
    return jsonify(result)


@app.route("/api/route", methods=["POST"])
def api_route():
    data = request.get_json(silent=True) or {}
    request_text = data.get("request", "").strip()
    if not request_text:
        return jsonify({"error": "درخواست نمی‌تواند خالی باشد"}), 400
    return jsonify(api_call("/route", "POST", {"request": request_text}))


@app.route("/api/project/create", methods=["POST"])
def api_project_create():
    return jsonify(api_call("/project/create", "POST", request.get_json(silent=True) or {}))


@app.route("/api/session/start", methods=["POST"])
def api_session_start():
    return jsonify(api_call("/session/start", "POST", request.get_json(silent=True) or {}))


@app.route("/api/session/answer", methods=["POST"])
def api_session_answer():
    return jsonify(api_call("/session/answer", "POST", request.get_json(silent=True) or {}))


@app.route("/api/executions/<execution_id>")
def api_executions(execution_id):
    return jsonify(api_call(f"/executions/{execution_id}"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
