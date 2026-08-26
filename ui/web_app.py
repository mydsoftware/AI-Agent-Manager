from __future__ import annotations

import os
import json
from flask import Flask, render_template, request, jsonify, session
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# تنظیمات API
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8080")
# اگر API key تنظیم نشده باشد، یک کلید پیش‌فرض برای تست استفاده می‌شود
API_KEY = os.getenv("AI_AGENT_MANAGER_API_KEY", "test-key-for-development")

# لیست ایجنت‌های موجود
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


def api_call(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """فراخوانی API مرکزی"""
    headers = {
        "Content-Type": "application/json",
    }
    # فقط اگر API key تنظیم شده باشد، آن را ارسال کن
    if API_KEY and API_KEY != "test-key-for-development":
        headers["X-API-Key"] = API_KEY
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        else:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@app.after_request
def add_cors_headers(response):
    """اضافه کردن هدر CORS"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-API-Key, X-Execution-ID'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


@app.route("/")
def dashboard():
    """داشبورد اصلی"""
    health = api_call("/health")
    return render_template(
        "dashboard.html",
        agents=AGENTS,
        health=health,
        api_base=API_BASE,
    )


@app.route("/execute")
def execute_page():
    """صفحه اجرای ایجنت"""
    return render_template("execute.html", agents=AGENTS)


@app.route("/audit")
def audit_page():
    """صفحه ممیزی سایت"""
    return render_template("audit.html")


@app.route("/projects")
def projects_page():
    """مدیریت پروژه‌ها"""
    return render_template("projects.html")


@app.route("/api/execute", methods=["POST"])
def api_execute():
    """API اجرای ایجنت"""
    data = request.json
    request_text = data.get("request", "").strip()
    agent = data.get("agent", "developer")

    if not request_text:
        return jsonify({"error": "درخواست نمی‌تواند خالی باشد"}), 400

    result = api_call("/execute", "POST", {"request": request_text, "agent": agent})
    return jsonify(result)


@app.route("/api/proxy/<path:endpoint>", methods=["GET", "POST"])
def api_proxy(endpoint):
    """پروکسی برای API مرکزی"""
    if request.method == "GET":
        result = api_call(f"/{endpoint}", "GET")
    else:
        result = api_call(f"/{endpoint}", "POST", request.json)
    return jsonify(result)


@app.route("/api/audit", methods=["POST"])
def api_audit():
    """API ممیزی سایت"""
    data = request.json
    url = data.get("url", "").strip()
    mode = data.get("mode", "pre_contract")

    if not url:
        return jsonify({"error": "URL الزامی است"}), 400

    execution_id = f"exec-{hash(url) % 10000}"
    result = api_call(
        "/execute/website-audit",
        "POST",
        {
            "request_id": execution_id,
            "url": url,
            "mode": mode,
            "language": "fa",
        },
    )
    return jsonify(result)


@app.route("/api/route", methods=["POST"])
def api_route():
    """API مسیریابی درخواست"""
    data = request.json
    request_text = data.get("request", "").strip()

    if not request_text:
        return jsonify({"error": "درخواست نمی‌تواند خالی باشد"}), 400

    result = api_call("/route", "POST", {"request": request_text})
    return jsonify(result)


@app.route("/api/project/create", methods=["POST"])
def api_project_create():
    """API ایجاد پروژه"""
    data = request.json
    result = api_call("/project/create", "POST", data)
    return jsonify(result)


@app.route("/api/session/start", methods=["POST"])
def api_session_start():
    """API شروع نشست"""
    data = request.json
    result = api_call("/session/start", "POST", data)
    return jsonify(result)


@app.route("/api/session/answer", methods=["POST"])
def api_session_answer():
    """API پاسخ به نشست"""
    data = request.json
    result = api_call("/session/answer", "POST", data)
    return jsonify(result)


@app.route("/api/executions/<execution_id>")
def api_executions(execution_id):
    """API دریافت وضعیت اجرا"""
    result = api_call(f"/executions/{execution_id}")
    return jsonify(result)


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    print(f"رابط وب در http://127.0.0.1:5000 اجرا شد")
    print(f"API مرکزی در {API_BASE}")
    app.run(host="127.0.0.1", port=5000, debug=True)
