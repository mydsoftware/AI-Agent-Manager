"""تست‌های Game Factory."""

from __future__ import annotations

from game.factory import GameFactory, GameProject


def test_create_project() -> None:
    """ایجاد پروژه بازی جدید."""
    factory = GameFactory()
    project = factory.create_project("بازی ربات", "یک بازی پلتفرمر", genre="platformer")
    assert project.name == "بازی ربات"
    assert project.genre == "platformer"
    assert project.id.startswith("game-")


def test_get_project() -> None:
    """بازیابی پروژه."""
    factory = GameFactory()
    project = factory.create_project("test", "desc")
    retrieved = factory.get_project(project.id)
    assert retrieved.name == "test"


def test_get_project_not_found() -> None:
    """پروژه یافت نشد."""
    factory = GameFactory()
    try:
        factory.get_project("nonexistent")
        assert False
    except FileNotFoundError:
        pass


def test_generate_tasks() -> None:
    """تولید وظایف بازی."""
    factory = GameFactory()
    project = factory.create_project("test", "desc")
    tasks = factory.generate_tasks(project)

    assert len(tasks) == 10
    assert tasks[0].agent == "game-designer"
    assert tasks[-1].agent == "game-build"

    # بررسی وابستگی‌ها
    build_task = tasks[-1]
    assert "qa" in str(build_task.depends_on)


def test_list_projects() -> None:
    """فهرست پروژه‌ها."""
    factory = GameFactory()
    factory.create_project("p1", "d1")
    factory.create_project("p2", "d2")

    projects = factory.list_projects()
    assert len(projects) == 2
    names = [p["name"] for p in projects]
    assert "p1" in names
    assert "p2" in names


def test_game_project_defaults() -> None:
    """مقادیر پیش‌فرض پروژه بازی."""
    project = GameProject(id="g1", name="test", description="desc")
    assert project.platform == "multi"
    assert project.engine == ""
    assert project.status == "created"
    assert len(project.tasks) == 0
