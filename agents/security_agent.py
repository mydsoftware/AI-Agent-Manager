from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.request import Request, urlopen

from manager.task import Task
from .base_agent import BaseAgent


@dataclass(frozen=True)
class SecurityFinding:
    severity: str
    category: str
    message: str


@dataclass(frozen=True)
class SecurityResult:
    passed: bool
    findings: tuple[SecurityFinding, ...] = ()


class SecurityAgent(BaseAgent):
    """ایجنت امنیتی برای بررسی دفاعی Source، وابستگی‌ها و HTTP."""

    name = "security"

    SOURCE_PATTERNS = (
        (r"eval\s*\(", "high", "code-execution", "استفاده از eval شناسایی شد."),
        (r"exec\s*\(", "high", "code-execution", "استفاده از exec شناسایی شد."),
        (r"(?:password|api[_-]?key|secret|token)\s*=\s*['\"]", "critical", "secret", "احتمال hard-code شدن Secret شناسایی شد."),
        (r"verify\s*=\s*False", "high", "tls", "غیرفعال کردن TLS verification شناسایی شد."),
        (r"\b(?:shell_exec|system|passthru)\s*\(", "high", "command-execution", "اجرای مستقیم فرمان سیستم شناسایی شد."),
        (r"pickle\.loads\s*\(", "high", "unsafe-deserialization", "Deserialization ناامن شناسایی شد."),
    )

    def run(self, task: Task) -> str:
        """وظیفه امنیتی JSON را به نتیجه اسکن تبدیل می‌کند."""
        import json
        try:
            command = json.loads(task.description)
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError("وظیفه Security باید JSON معتبر باشد.") from error
        if not isinstance(command, dict):
            raise ValueError("ساختار وظیفه Security معتبر نیست.")
        if command.get("action") == "http":
            result = self.scan_http(str(command["url"]))
        else:
            result = self.scan(command.get("source", command.get("diff", "")), command.get("dependency_report"))
        return json.dumps({
            "status": "passed" if result.passed else "failed",
            "findings": [item.__dict__ for item in result.findings],
        }, ensure_ascii=False)

    def scan(self, diff: str | None, dependency_report: str | None = None) -> SecurityResult:
        text = diff or ""
        findings: list[SecurityFinding] = []
        for pattern, severity, category, message in self.SOURCE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append(SecurityFinding(severity, category, message))

        report = (dependency_report or "").lower()
        if "critical" in report and ("vulnerability" in report or "vulnerabilit" in report):
            findings.append(SecurityFinding("critical", "dependency", "وابستگی دارای آسیب‌پذیری Critical گزارش شده است."))

        return SecurityResult(not self._blocking(findings), tuple(findings))

    def scan_source(self, source: str) -> SecurityResult:
        return self.scan(source)

    def scan_http(self, url: str, timeout: int = 10) -> SecurityResult:
        """Headerها، Cookieها و افشای اطلاعات HTTP را بدون payload تهاجمی بررسی می‌کند."""
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL باید با http:// یا https:// شروع شود.")

        request = Request(url, method="GET", headers={"User-Agent": "AI-Agent-Manager-Security"})
        findings: list[SecurityFinding] = []
        try:
            with urlopen(request, timeout=timeout) as response:
                headers = response.headers
                header_names = {name.lower() for name in headers.keys()}
                if url.startswith("https://") and "strict-transport-security" not in header_names:
                    findings.append(SecurityFinding("medium", "headers", "HSTS فعال نیست."))
                if "content-security-policy" not in header_names:
                    findings.append(SecurityFinding("medium", "headers", "Content-Security-Policy وجود ندارد."))
                if "x-content-type-options" not in header_names:
                    findings.append(SecurityFinding("low", "headers", "X-Content-Type-Options وجود ندارد."))
                if "x-frame-options" not in header_names and "content-security-policy" not in header_names:
                    findings.append(SecurityFinding("medium", "headers", "محافظت در برابر Clickjacking شناسایی نشد."))
                if "referrer-policy" not in header_names:
                    findings.append(SecurityFinding("low", "headers", "Referrer-Policy تنظیم نشده است."))
                server = headers.get("Server", "")
                if re.search(r"(?:apache|nginx|iis|php)/?\d", server, re.I):
                    findings.append(SecurityFinding("low", "information-disclosure", "نسخه نرم‌افزار در Server Header افشا شده است."))
                for cookie in headers.get_all("Set-Cookie", []) or []:
                    cookie_lower = cookie.lower()
                    if "secure" not in cookie_lower and url.startswith("https://"):
                        findings.append(SecurityFinding("medium", "cookie", "Cookie بدون Secure روی HTTPS ارسال شده است."))
                    if "httponly" not in cookie_lower:
                        findings.append(SecurityFinding("medium", "cookie", "Cookie بدون HttpOnly ارسال شده است."))
                    if "samesite" not in cookie_lower:
                        findings.append(SecurityFinding("low", "cookie", "Cookie بدون SameSite ارسال شده است."))
        except Exception as exc:
            return SecurityResult(False, (SecurityFinding("medium", "availability", f"بررسی HTTP انجام نشد: {type(exc).__name__}"),))

        return SecurityResult(not self._blocking(findings), tuple(findings))

    @staticmethod
    def _blocking(findings: list[SecurityFinding]) -> bool:
        return any(item.severity in {"critical", "high"} for item in findings)
