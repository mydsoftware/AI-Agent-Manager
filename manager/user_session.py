from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Any


@dataclass
class UserSession:
    session_id: str
    request: str
    status: str = "running"
    stage: str = "requirements"
    question: str | None = None
    answers: list[str] | None = None
    output: Any = None

    def __post_init__(self) -> None:
        if self.answers is None:
            self.answers = []


class UserSessionManager:
    def __init__(self, root: str = "data/sessions") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self.root / f"{session_id}.json"

    def create(self, session_id: str, request: str) -> UserSession:
        return self.save(UserSession(session_id=session_id, request=request))

    def save(self, session: UserSession) -> UserSession:
        self._path(session.session_id).write_text(
            json.dumps(asdict(session), ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )
        return session

    def load(self, session_id: str) -> UserSession:
        return UserSession(**json.loads(self._path(session_id).read_text(encoding="utf-8")))

    def update(self, session: UserSession) -> UserSession:
        return self.save(session)
