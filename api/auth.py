from __future__ import annotations

import hmac
import os
import re
from dataclasses import dataclass
from functools import wraps
from typing import Callable

from flask import Flask, jsonify, request, g


@dataclass(frozen=True)
class Principal:
    """هویت احراز‌شده API و نقش دسترسی آن را نگه می‌دارد."""

    subject: str
    role: str


def _token_map() -> dict[str, Principal]:
    """توکن‌های نقش‌دار را فقط از متغیرهای محیطی می‌خواند و هرگز مقدارشان را لاگ نمی‌کند."""
    values = {
        "MANAGER_API_TOKEN": ("manager-admin", "admin"),
        "MANAGER_OPERATOR_TOKEN": ("manager-operator", "operator"),
        "MANAGER_VIEWER_TOKEN": ("manager-viewer", "viewer"),
    }
    return {name: Principal(subject, role) for name, (subject, role) in values.items() if os.getenv(name)}


def authenticate() -> Principal | None:
    """X-Manager-API-Key را با compare_digest بررسی و Principal متناظر را برمی‌گرداند."""
    supplied = request.headers.get("X-Manager-API-Key", "")
    if not supplied:
        return None
    for env_name, principal in _token_map().items():
        expected = os.getenv(env_name, "")
        if expected and hmac.compare_digest(supplied, expected):
            return principal
    return None


def require_auth(*roles: str) -> Callable:
    """Decorator احراز هویت و در صورت نیاز محدودیت نقش را اعمال می‌کند."""
    allowed = set(roles)

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapped(*args, **kwargs):
            """Handler را پس از بررسی Principal و نقش اجرا می‌کند."""
            principal = getattr(g, "principal", None)
            if principal is None:
                return jsonify({"error": "احراز هویت الزامی است."}), 401
            if allowed and principal.role not in allowed:
                return jsonify({"error": "مجوز کافی برای این عملیات وجود ندارد."}), 403
            return view(*args, **kwargs)
        return wrapped

    return decorator


def _project_id_from_path(path: str) -> str | None:
    """شناسه پروژه را فقط از مسیرهای استاندارد Project API استخراج می‌کند."""
    match = re.match(r"^/api/project/([^/]+)(?:/|$)", path)
    return match.group(1) if match else None


def _approval_id_from_path(path: str) -> str | None:
    """شناسه Approval را فقط از مسیر resolve استخراج می‌کند."""
    match = re.match(r"^/api/approvals/([^/]+)/resolve$", path)
    return match.group(1) if match else None


def _check_project_scope(project_id: str) -> tuple[bool, tuple[dict, int] | None]:
    """مالکیت پروژه را از همان SQLite بررسی می‌کند و در صورت عدم دسترسی 404 می‌دهد."""
    from services.project_store import ProjectStore

    project = ProjectStore().get(project_id)
    if project is None:
        return False, ({"error": "پروژه پیدا نشد."}, 404)
    principal = current_principal()
    if principal is None:
        return False, ({"error": "احراز هویت الزامی است."}, 401)
    if principal.role != "admin" and str(project.get("owner_id", "")) != principal.subject:
        return False, ({"error": "پروژه پیدا نشد."}, 404)
    return True, None


def install_api_auth(app: Flask) -> None:
    """احراز هویت، RBAC و Project Scope را برای APIهای مدیریتی نصب می‌کند."""

    @app.before_request
    def _authenticate_api():
        """درخواست‌های /api را پیش از اجرای Handler احراز و scope می‌کند."""
        if not request.path.startswith("/api/") or request.path == "/api/health":
            return None
        principal = authenticate()
        if principal is None:
            return jsonify({"error": "احراز هویت الزامی است."}), 401
        g.principal = principal
        if principal.role == "viewer" and request.method not in {"GET", "HEAD", "OPTIONS"}:
            return jsonify({"error": "Viewer فقط دسترسی خواندنی دارد."}), 403

        project_id = _project_id_from_path(request.path)
        if project_id:
            allowed, error = _check_project_scope(project_id)
            if not allowed:
                return jsonify(error[0]), error[1]

        approval_id = _approval_id_from_path(request.path)
        if approval_id:
            from services.activity_store import ActivityStore
            approval = ActivityStore().get_approval(approval_id)
            if approval is None:
                return jsonify({"error": "Approval پیدا نشد."}), 404
            allowed, error = _check_project_scope(str(approval["project_id"]))
            if not allowed:
                return jsonify(error[0]), error[1]
        if request.path == "/api/approvals" and request.args.get("project_id"):
            allowed, error = _check_project_scope(request.args["project_id"])
            if not allowed:
                return jsonify(error[0]), error[1]
        if request.path == "/api/approvals" and not request.args.get("project_id") and principal.role != "admin":
            return jsonify({"error": "برای مشاهده Approvalها باید project_id مشخص شود."}), 403
        return None


def current_principal() -> Principal | None:
    """Principal درخواست جاری را بدون افشای credential برمی‌گرداند."""
    return getattr(g, "principal", None)


def project_access_allowed(project: dict | None) -> bool:
    """دسترسی پروژه را بر اساس owner و نقش admin بررسی می‌کند."""
    if project is None:
        return False
    principal = current_principal()
    if principal is None:
        return False
    return principal.role == "admin" or str(project.get("owner_id", "")) == principal.subject
