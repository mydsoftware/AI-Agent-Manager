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


class ProjectRepositoryFactory:
    """ساخت Repository مستقل و اسکلت اولیه پروژه برای هر درخواست جدید."""

    def __init__(self, client: GitHubAPIClient | None = None, owner: str | None = None) -> None:
        self.client = client or GitHubAPIClient()
        self.owner = owner or os.getenv("GITHUB_OWNER", "mydsoftware")

    @staticmethod
    def _slug(value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")[:45]
        return slug or "ai-project"

    def create(self, name: str, description: str, request: str, project_type: str = "website", private: bool = True) -> ProjectCreationResult:
        base_name = self._slug(name)
        repo = self.client.create_repository(
            owner=self.owner,
            name=f"{base_name}-{os.urandom(3).hex()}",
            description=description,
            private=private,
            auto_init=True,
        )
        repository = repo["full_name"]
        branch = repo.get("default_branch", "main")

        files: dict[str, str] = {
            "PROJECT_REQUEST.json": self._json({
                "source": "AI-Agent-Manager",
                "request": request,
                "project_type": project_type,
                "status": "created",
            }),
            "agent/state.json": self._json({"status": "created", "phase": "planning", "next": "build"}),
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
            self.client.put_file(repository, path, content, f"feat: initialize {path}", branch)

        return ProjectCreationResult(repository, repo["html_url"], branch, project_type, list(files))

    @staticmethod
    def _json(value: Any) -> str:
        import json
        return json.dumps(value, ensure_ascii=False, indent=2) + "\n"
