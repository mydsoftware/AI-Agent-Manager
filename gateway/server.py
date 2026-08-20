from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


MANAGER_URL = os.environ.get("MANAGER_URL", "http://127.0.0.1:8080").rstrip("/")
GATEWAY_TOKEN = os.environ.get("GATEWAY_TOKEN", "")


def manager_request(path: str, body: dict, execution_id: str | None = None) -> tuple[int, dict]:
    """درخواست را از Gateway به Manager منتقل می‌کند."""
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-API-Key": GATEWAY_TOKEN,
    }
    if execution_id:
        headers["X-Execution-ID"] = execution_id
    request = urllib.request.Request(
        f"{MANAGER_URL}{path}", data=payload, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return response.status, data
    except urllib.error.HTTPError as error:
        try:
            data = json.loads(error.read().decode("utf-8"))
        except Exception:
            data = {"error": "پاسخ نامعتبر از Manager دریافت شد."}
        return error.code, data
    except urllib.error.URLError:
        return 502, {"error": "ارتباط Gateway با Manager برقرار نشد."}


class GatewayHandler(BaseHTTPRequestHandler):
    """Gateway مستقل و قابل استقرار خارج از Cloudflare."""

    def _send_json(self, status: int, data: dict) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _authorized(self) -> bool:
        authorization = self.headers.get("Authorization", "")
        expected = f"Bearer {GATEWAY_TOKEN}"
        if not GATEWAY_TOKEN or authorization != expected:
            self._send_json(401, {"error": "توکن Gateway معتبر نیست."})
            return False
        return True

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "فعال"})
            return
        if not self._authorized():
            return
        if self.path.startswith("/executions/"):
            execution_id = self.path.removeprefix("/executions/").strip("/")
            if not execution_id:
                self._send_json(400, {"error": "execution_id الزامی است."})
                return
            try:
                payload = urllib.request.Request(
                    f"{MANAGER_URL}/executions/{execution_id}",
                    headers={"X-API-Key": GATEWAY_TOKEN},
                    method="GET",
                )
                with urllib.request.urlopen(payload, timeout=15) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    self._send_json(response.status, data)
            except urllib.error.HTTPError as error:
                self._send_json(error.code, {"error": "Execution پیدا نشد."})
            except urllib.error.URLError:
                self._send_json(502, {"error": "ارتباط Gateway با Manager برقرار نشد."})
            return
        self._send_json(404, {"error": "مسیر Gateway پیدا نشد."})

    def do_POST(self) -> None:
        if not self._authorized():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            self._send_json(400, {"error": "JSON نامعتبر است."})
            return

        if self.path == "/route":
            request = str(body.get("request", "")).strip()
            if not request:
                self._send_json(400, {"error": "request الزامی است."})
                return
            status, data = manager_request("/route", {"request": request})
            self._send_json(status, data)
            return

        if self.path == "/execute":
            request = str(body.get("request", "")).strip()
            if not request:
                self._send_json(400, {"error": "request الزامی است."})
                return
            execution_id = str(body.get("execution_id", "")).strip()
            if not execution_id:
                self._send_json(400, {"error": "execution_id الزامی است."})
                return
            status, data = manager_request("/execute", {"request": request}, execution_id)
            self._send_json(status, data)
            return

        if self.path == "/execute/website-audit":
            request_id = str(body.get("request_id", "")).strip()
            url = str(body.get("url", "")).strip()
            if not request_id or not url:
                self._send_json(400, {"error": "request_id و url الزامی هستند."})
                return
            if body.get("mode", "pre_contract") == "pre_contract" and bool(body.get("access", False)):
                self._send_json(400, {"error": "در حالت قبل از قرارداد دسترسی نباید فعال باشد."})
                return
            execution_id = str(body.get("execution_id", "")).strip()
            if not execution_id:
                self._send_json(400, {"error": "execution_id الزامی است."})
                return
            status, data = manager_request(
                "/execute/website-audit", body, execution_id
            )
            self._send_json(status, data)
            return

        self._send_json(404, {"error": "مسیر Gateway پیدا نشد."})

    def log_message(self, format: str, *args) -> None:
        print(f"Gateway: {format % args}")


def run_server(host: str = "127.0.0.1", port: int = 8787) -> None:
    server = ThreadingHTTPServer((host, port), GatewayHandler)
    print(f"Gateway در http://{host}:{port} اجرا شد.")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
