from __future__ import annotations

import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8080")
API_KEY = os.getenv("AI_AGENT_MANAGER_API_KEY", "")

AGENTS = {
    "developer": {"name": "توسعه‌دهنده", "icon": "💻", "desc": "توسعه و اصلاح کد"},
    "researcher": {"name": "پژوهشگر", "icon": "🔍", "desc": "تحقیق و تحلیل"},
    "qa": {"name": "کنترل کیفیت", "icon": "✓", "desc": "تست و تضمین کیفیت"},
    "github": {"name": "GitHub", "icon": "◉", "desc": "Repository و CI/CD"},
    "website-audit": {"name": "ممیزی سایت", "icon": "⌁", "desc": "فنی، SEO و امنیت"},
    "wordpress-factory": {"name": "کارخانه وردپرس", "icon": "◆", "desc": "ساخت و راه‌اندازی وردپرس"},
    "wordpress-security": {"name": "امنیت وردپرس", "icon": "◇", "desc": "بررسی امنیت"},
    "wordpress-performance": {"name": "عملکرد وردپرس", "icon": "↗", "desc": "بهینه‌سازی سرعت"},
    "wordpress-seo": {"name": "SEO وردپرس", "icon": "⌁", "desc": "بهینه‌سازی موتور جستجو"},
    "wordpress-ui": {"name": "رابط کاربری وردپرس", "icon": "✦", "desc": "طراحی رابط کاربری"},
}


def api_call(endpoint: str, method: str = "GET", data: dict | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    try:
        response = requests.request(method, f"{API_BASE}{endpoint}", headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        return {"error": str(exc)}


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/app")
def dashboard():
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
    text = str(data.get("request", "")).strip()
    if not text:
        return jsonify({"error": "درخواست نمی‌تواند خالی باشد"}), 400
    return jsonify(api_call("/execute", "POST", {"request": text, "agent": data.get("agent", "developer")}))


@app.route("/api/proxy/<path:endpoint>", methods=["GET", "POST"])
def api_proxy(endpoint):
    data = request.get_json(silent=True) if request.method == "POST" else None
    return jsonify(api_call(f"/{endpoint}", request.method, data))


@app.route("/api/audit", methods=["POST"])
def api_audit():
    data = request.get_json(silent=True) or {}
    url = str(data.get("url", "")).strip()
    if not url:
        return jsonify({"error": "URL الزامی است"}), 400
    return jsonify(api_call("/execute/website-audit", "POST", {"request_id": f"exec-{abs(hash(url)) % 100000}", "url": url, "mode": data.get("mode", "pre_contract"), "language": "fa"}))


@app.route("/api/route", methods=["POST"])
def api_route():
    data = request.get_json(silent=True) or {}
    text = str(data.get("request", "")).strip()
    if not text:
        return jsonify({"error": "درخواست نمی‌تواند خالی باشد"}), 400
    return jsonify(api_call("/route", "POST", {"request": text}))


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
