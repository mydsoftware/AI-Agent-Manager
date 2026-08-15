from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from manager.session_runtime import SessionRuntime


class SessionAPIHandler(BaseHTTPRequestHandler):
    runtime = SessionRuntime()

    def send_json(self, status: int, data: dict) -> None:
        payload = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

    @staticmethod
    def state(state) -> dict:
        return state.to_dict() if hasattr(state, "to_dict") else state.__dict__

    def do_POST(self) -> None:
        try:
            body = self.body()
            if self.path == "/session/start":
                state = self.runtime.start(body["session_id"], body["request"])
            elif self.path == "/session/answer":
                state = self.runtime.answer(body["session_id"], body["answer"])
            elif self.path == "/session/resume":
                state = self.runtime.resume(body["session_id"])
            else:
                self.send_json(404, {"error": "مسیر درخواست پیدا نشد."})
                return
            self.send_json(200, self.state(state))
        except KeyError as exc:
            self.send_json(400, {"error": f"فیلد الزامی: {exc.args[0]}"})
        except (ValueError, RuntimeError) as exc:
            self.send_json(400, {"error": str(exc)})
        except FileNotFoundError:
            self.send_json(404, {"error": "Session پیدا نشد."})
        except Exception as exc:
            self.send_json(500, {"error": str(exc)})

    def do_GET(self) -> None:
        if self.path.startswith("/session/"):
            session_id = self.path.removeprefix("/session/").strip("/")
            if not session_id:
                self.send_json(400, {"error": "شناسه Session الزامی است."})
                return
            try:
                self.send_json(200, self.state(self.runtime.sessions.load(session_id)))
            except FileNotFoundError:
                self.send_json(404, {"error": "Session پیدا نشد."})
            return
        self.send_json(404, {"error": "مسیر درخواست پیدا نشد."})


def run_server(host: str = "127.0.0.1", port: int = 8081) -> None:
    HTTPServer((host, port), SessionAPIHandler).serve_forever()
