from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.request import Request, urlopen

from adapters.github_adapter import GitHubAPIClient


@dataclass
class BuildResult:
    repository: str
    branch: str
    files: list[str]
    pull_request: str | None


class DeepSeekBuilder:
    """ساخت فایل‌های پروژه با API سازگار با OpenAI متعلق به DeepSeek."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.endpoint = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/") + "/chat/completions"

    def generate_files(self, request: str) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY تنظیم نشده است.")
        prompt = f"""تو یک Agent ارشد توسعه وب هستی. درخواست کاربر را به فایل‌های واقعی پروژه تبدیل کن.
فقط JSON معتبر برگردان و هیچ Markdown یا توضیح اضافی ننویس.
فرمت دقیق: {{\"files\": {{\"index.html\": \"...\", \"style.css\": \"...\"}}}}
برای سایت HTML مستقل، حداقل index.html و style.css را بساز. اگر JavaScript لازم است app.js هم بساز.
درخواست کاربر:
{request}
"""
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You generate production-ready web project files as strict JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }).encode("utf-8")
        req = Request(self.endpoint, data=payload, method="POST", headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        with urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        result = json.loads(content)
        files = result.get("files")
        if not isinstance(files, dict) or not files:
            raise RuntimeError("مدل فایل قابل استفاده‌ای تولید نکرد.")
        return {str(path): str(value) for path, value in files.items()}


class ProjectBuilder:
    def __init__(self, github: GitHubAPIClient | None = None, ai: DeepSeekBuilder | None = None) -> None:
        self.github = github or GitHubAPIClient()
        self.ai = ai or DeepSeekBuilder()

    def build(self, repository: str, request: str, branch: str, base: str = "main", pr_title: str | None = None) -> BuildResult:
        self.github.create_branch(repository, branch, base)
        files = self.ai.generate_files(request)
        written = []
        for path, content in files.items():
            self.github.put_file(repository, path, content, f"feat: AI build {path}", branch)
            written.append(path)
        pr = self.github.create_pull_request(
            repository,
            branch,
            base,
            pr_title or "AI Agent Manager: generated project",
            f"ساخته‌شده خودکار توسط AI-Agent-Manager\n\nدرخواست: {request}",
            True,
        )
        return BuildResult(repository, branch, written, pr.get("html_url"))
