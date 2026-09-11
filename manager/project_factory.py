from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

from adapters.github_adapter import GitHubAPIClient


@dataclass
class ProjectCreationResult:
    repository: str
    url: str
    branch: str
    project_type: str
    files: list[str]
    status: str = "created"
    execution: dict[str, Any] | None = None
    reused_repository: bool = False


class ProjectRepositoryFactory:
    """مدیریت چرخه عمر Repository پروژه؛ هر پروژه یک Repository پایدار دارد."""

    def __init__(self, client: GitHubAPIClient | None = None, owner: str | None = None) -> None:
        self.client = client or GitHubAPIClient()
        self.owner = owner or os.getenv("GITHUB_OWNER", "mydsoftware")
        self.autonomous_agent_repo = os.getenv("AUTONOMOUS_AGENT_REPO", "mydsoftware/GitHub-Autonomous-Agent")

    @staticmethod
    def _slug(value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")[:45]
        return slug or "ai-project"

    def _get_or_create_repository(self, name: str, description: str, private: bool) -> tuple[dict[str, Any], bool]:
        """Repository را idempotent پیدا می‌کند و فقط در صورت نبودن می‌سازد."""
        repository_name = self._slug(name)
        repository_full_name = f"{self.owner}/{repository_name}"
        try:
            existing = self.client.get_repository(repository_full_name)
            if not isinstance(existing, dict) or not existing.get("full_name"):
                raise RuntimeError("پاسخ نامعتبر از GitHub برای Repository موجود دریافت شد.")
            return existing, True
        except RuntimeError as error:
            # فقط 404 را به معنی نبود Repository در نظر می‌گیریم؛ خطاهای auth/rate-limit/network نباید
            # باعث تلاش برای ساخت Repository دوم شوند.
            if "GitHub API خطای 404" not in str(error):
                raise

        created = self.client.create_repository(
            owner=self.owner,
            name=repository_name,
            description=description,
            private=private,
            auto_init=True,
        )
        return created, False

    def create(
        self,
        name: str,
        description: str,
        request: str,
        project_type: str = "website",
        private: bool = True,
        plan: dict[str, Any] | None = None,
        repository: str | None = None,
    ) -> ProjectCreationResult:
        """پروژه را روی Repository مشخص یا Repository پایدار مشتق‌شده از نام ایجاد/ادامه می‌دهد."""
        if repository and "/" not in repository:
            repository = f"{self.owner}/{repository.strip()}"

        if repository:
            repo = self.client.get_repository(repository.strip())
            reused_repository = True
        else:
            repo, reused_repository = self._get_or_create_repository(name, description, private)

        repository_full_name = str(repo["full_name"])
        branch = str(repo.get("default_branch") or "main")

        files: dict[str, str] = {
            "PROJECT_REQUEST.json": self._json({
                "source": "AI-Agent-Manager",
                "request": request,
                "project_type": project_type,
                "status": "created" if not reused_repository else "resumed",
                "repository": repository_full_name,
            }),
            "agent/state.json": self._json({"status": "created" if not reused_repository else "resumed", "phase": "planning", "next": "build"}),
            "README.md": f"# {name}\n\n{description}\n\n## AI-Agent-Manager\n\nدرخواست اولیه:\n\n{request}\n",
        }
        if project_type in {"html", "website", "web"}:
            files["site/index.html"] = (
                "<!doctype html>\n<html lang=\"fa\" dir=\"rtl\">\n"
                "<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
                f"<title>{name}</title></head>\n<body><main><h1>{name}</h1>"
                "<p>نسخه اولیه توسط AI-Agent-Manager ساخته شد.</p></main></body>\n</html>\n"
            )

        for path, content in files.items():
            self.client.put_file(repository_full_name, path, content, f"feat: initialize {path}", branch)

        execution = None
        status = "resumed" if reused_repository else "created"
        if plan is not None:
            execution = self.client.repository_dispatch(
                self.autonomous_agent_repo,
                "ai-agent-project",
                {
                    "target_repository": repository_full_name,
                    "target_branch": branch,
                    "plan": plan,
                },
            )
            status = "agent-dispatched"

        return ProjectCreationResult(
            repository_full_name,
            str(repo["html_url"]),
            branch,
            project_type,
            list(files),
            status,
            execution,
            reused_repository,
        )

    @staticmethod
    def _json(value: Any) -> str:
        import json
        return json.dumps(value, ensure_ascii=False, indent=2) + "\n"
