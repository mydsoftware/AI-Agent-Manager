from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from api import execute
from manager.api_guard import APIGuard
from manager.project_factory import ProjectRepositoryFactory
from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class ManagerRequestHandler(BaseHTTPRequestHandler):
    """درخواست‌های HTTP مربوط به اجرای Manager را مدیریت می‌کند."""

    guard = APIGuard()
    session_runtime = SessionRuntime(sessions=UserSessionManager("data/sessions"))
    project_factory = ProjectRepositoryFactory()

    def _send_json(self, status: int, data: dict) -> None:
        payload = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _authorized(self) -> bool:
        if self.guard.authorized(self.headers.get("X-API-Key")):
            return True
        self._send_json(401, {"error": "کلید دسترسی معتبر نیست."})
        return False

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "فعال"})
            return
        if not self._authorized():
            return
        if self.path.startswith("/session/"):
            session_id = self.path.removeprefix("/session/").strip("/")
            if not session_id:
                self._send_json(400, {"error": "شناسه Session الزامی است."})
                return
            try:
                state = self.session_runtime.resume(session_id)
                self._send_json(200, state.__dict__)
            except FileNotFoundError:
                self._send_json(404, {"error": "Session پیدا نشد."})
            return
        self._send_json(404, {"error": "مسیر درخواست پیدا نشد."})

    def do_POST(self) -> None:
        if not self._authorized():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if self.path == "/execute":
                self._send_json(200, execute(body.get("request", ""), body.get("agent", "developer")))
                return
            if self.path == "/project/create":
                name = str(body.get("name", "")).strip()
                description = str(body.get("description", "")).strip()
                request = str(body.get("request", "")).strip()
                project_type = str(body.get("project_type", "website")).strip() or "website"
                is_private = bool(body.get("private", True))
                if not name or not description or not request:
                    self._send_json(400, {"error": "name، description و request الزامی هستند."})
                    return
                result = self.project_factory.create(name, description, request, project_type, is_private)
                self._send_json(201, result.__dict__)
                return
            if self.path == "/session/start":
                session_id = body.get("session_id", "").strip()
                request = body.get("request", "").strip()
                if not session_id or not request:
                    self._send_json(400, {"error": "session_id و request الزامی هستند."})
                    return
                self._send_json(200, self.session_runtime.start(session_id, request).__dict__)
                return
            if self.path == "/session/answer":
                session_id = body.get("session_id", "").strip()
                answer = body.get("answer", "").strip()
                if not session_id or not answer:
                    self._send_json(400, {"error": "session_id و answer الزامی هستند."})
                    return
                self._send_json(200, self.session_runtime.answer(session_id, answer).__dict__)
                return
            self._send_json(404, {"error": "مسیر درخواست پیدا نشد."})
        except json.JSONDecodeError:
            self._send_json(400, {"error": "JSON نامعتبر است."})
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
        except FileNotFoundError:
            self._send_json(404, {"error": "Session پیدا نشد."})
        except Exception as error:
            self._send_json(500, {"error": str(error)})

    def log_message(self, format: str, *args) -> None:
        print(f"درخواست HTTP: {format % args}")


APIHandler = ManagerRequestHandler


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = HTTPServer((host, port), ManagerRequestHandler)
    print(f"Manager در http://{host}:{port} اجرا شد.")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
