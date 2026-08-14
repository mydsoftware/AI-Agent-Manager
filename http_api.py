from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from api import execute


class ManagerRequestHandler(BaseHTTPRequestHandler):
    """درخواست‌های HTTP مربوط به اجرای Manager را مدیریت می‌کند."""

    def _send_json(self, status: int, data: dict) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:
        """درخواست POST برای اجرای Manager را پردازش می‌کند."""
        if self.path != "/execute":
            self._send_json(404, {"error": "مسیر درخواست پیدا نشد."})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            result = execute(body.get("request", ""), body.get("agent", "developer"))
            self._send_json(200, result)
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
        except Exception as error:
            self._send_json(500, {"error": str(error)})

    def log_message(self, format: str, *args) -> None:
        """گزارش‌های پیش‌فرض HTTP را فارسی و کوتاه نگه می‌دارد."""
        print(f"درخواست HTTP: {format % args}")


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    """سرور HTTP محلی Manager را اجرا می‌کند."""
    server = HTTPServer((host, port), ManagerRequestHandler)
    print(f"Manager در http://{host}:{port} اجرا شد.")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
