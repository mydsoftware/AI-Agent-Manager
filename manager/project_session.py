from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass
class ProjectSession:
    """حافظه پایدار یک پروژه برای توقف، سؤال از کاربر و ادامه بدون شروع مجدد."""

    session_id: str
    request: str
    status: str = "running"
    current_stage: str = "requirements"
    pending_question: str | None = None
    answers: dict[str, str] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def ask(self, question: str, key: str = "answer") -> None:
        self.status = "waiting_for_user"
        self.pending_question = question
        self.events.append({"event": "question", "key": key, "question": question})

    def answer(self, value: str, key: str = "answer") -> None:
        if self.status != "waiting_for_user":
            raise RuntimeError("session-not-waiting")
        self.answers[key] = value.strip()
        self.pending_question = None
        self.status = "running"
        self.events.append({"event": "answer", "key": key, "value": value.strip()})

    def stage(self, name: str) -> None:
        self.current_stage = name
        self.events.append({"event": "stage", "name": name})

    def save(self, directory: str) -> Path:
        path = Path(directory) / f"{self.session_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str) -> "ProjectSession":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))


class ProjectSessionStore:
    def __init__(self, directory: str) -> None:
        self.directory = Path(directory)

    def save(self, session: ProjectSession) -> Path:
        return session.save(str(self.directory))

    def load(self, session_id: str) -> ProjectSession:
        return ProjectSession.load(str(self.directory / f"{session_id}.json"))
