"""Game Factory - کارخانه تولید خودکار بازی."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from manager.task import Task
from manager.task_status import TaskStatus


@dataclass
class GameProject:
    """اطلاعات پروژه بازی."""

    id: str
    name: str
    description: str
    genre: str = ""
    platform: str = "multi"
    engine: str = ""
    status: str = "created"
    tasks: list[Task] = field(default_factory=list)
    assets: dict[str, Any] = field(default_factory=dict)
    design: dict[str, Any] = field(default_factory=dict)
    build_results: dict[str, Any] = field(default_factory=dict)
    reports: list[dict[str, Any]] = field(default_factory=list)


class GameFactory:
    """کارخانه تولید خودکار بازی از ایده تا Build نهایی."""

    def __init__(self) -> None:
        self._projects: dict[str, GameProject] = {}

    def create_project(self, name: str, description: str, **kwargs: Any) -> GameProject:
        """پروژه بازی جدیدی ایجاد می‌کند."""
        import uuid
        project_id = f"game-{uuid.uuid4().hex[:8]}"

        project = GameProject(
            id=project_id,
            name=name,
            description=description,
            genre=kwargs.get("genre", ""),
            platform=kwargs.get("platform", "multi"),
            engine=kwargs.get("engine", ""),
        )
        self._projects[project_id] = project
        return project

    def get_project(self, project_id: str) -> GameProject:
        """پروژه را با شناسه برمی‌گرداند."""
        if project_id not in self._projects:
            raise FileNotFoundError(f"پروژه {project_id} یافت نشد.")
        return self._projects[project_id]

    def generate_tasks(self, project: GameProject) -> list[Task]:
        """وظایف کامل تولید بازی را تولید می‌کند."""
        tasks = [
            Task(
                id=f"{project.id}-design",
                title="طراحی بازی (GDD)",
                description=f"بازی «{project.name}» را طراحی کن.\nتوضیحات: {project.description}",
                agent="game-designer",
            ),
            Task(
                id=f"{project.id}-story",
                title="نوشتن داستان",
                description=f"داستان بازی «{project.name}» را بنویس.",
                agent="game-writer",
                depends_on=[f"{project.id}-design"],
            ),
            Task(
                id=f"{project.id}-assets",
                title="برنامه‌ریزی Assetها",
                description=f"Assetهای بصری بازی «{project.name}» را برنامه‌ریزی کن.",
                agent="game-asset",
                depends_on=[f"{project.id}-design"],
            ),
            Task(
                id=f"{project.id}-audio",
                title="برنامه‌ریزی صدا",
                description=f"صداهای بازی «{project.name}» را برنامه‌ریزی کن.",
                agent="game-audio",
                depends_on=[f"{project.id}-design"],
            ),
            Task(
                id=f"{project.id}-levels",
                title="طراحی سطوح",
                description=f"سطوح بازی «{project.name}» را طراحی کن.",
                agent="game-level-designer",
                depends_on=[f"{project.id}-design"],
            ),
            Task(
                id=f"{project.id}-ai",
                title="طراحی AI",
                description=f"هوش مصنوعی بازی «{project.name}» را طراحی کن.",
                agent="game-ai",
                depends_on=[f"{project.id}-design"],
            ),
            Task(
                id=f"{project.id}-code",
                title="پیاده‌سازی کد",
                description=f"کد بازی «{project.name}» را پیاده‌سازی کن.",
                agent="game-developer",
                depends_on=[f"{project.id}-design", f"{project.id}-ai"],
            ),
            Task(
                id=f"{project.id}-ui",
                title="طراحی UI",
                description=f"رابط کاربری بازی «{project.name}» را طراحی کن.",
                agent="game-ui",
                depends_on=[f"{project.id}-design"],
            ),
            Task(
                id=f"{project.id}-qa",
                title="تست بازی",
                description=f"بازی «{project.name}» را تست کن.",
                agent="game-qa",
                depends_on=[f"{project.id}-code", f"{project.id}-ui"],
            ),
            Task(
                id=f"{project.id}-build",
                title="Build بازی",
                description=f"بازی «{project.name}» را برای پلتفرم {project.platform} بساز.",
                agent="game-build",
                depends_on=[f"{project.id}-qa"],
            ),
        ]
        project.tasks = tasks
        return tasks

    def list_projects(self) -> list[dict[str, Any]]:
        """فهرست تمام پروژه‌ها را برمی‌گرداند."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "genre": p.genre,
                "platform": p.platform,
                "tasks_count": len(p.tasks),
            }
            for p in self._projects.values()
        ]
