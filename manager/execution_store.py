from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock


@dataclass
class ExecutionRecord:
    """رکورد پایدار وضعیت اجرای یک Agent."""

    execution_id: str
    request_id: str
    agent: str
    url: str
    status: str
    created_at: str
    updated_at: str
    result: object | None = None
    error: str | None = None


class ExecutionStore:
    """ذخیره‌سازی اتمیک Executionها؛ بدون قرار دادن داده‌ها در کد."""

    def __init__(self, root: str = "data/executions") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _path(self, execution_id: str) -> Path:
        if not execution_id or any(c not in "0123456789abcdefABCDEF-" for c in execution_id):
            raise ValueError("execution_id نامعتبر است.")
        return self.root / f"{execution_id}.json"

    def create(self, execution_id: str, request_id: str, agent: str, url: str) -> ExecutionRecord:
        now = datetime.now(timezone.utc).isoformat()
        record = ExecutionRecord(execution_id, request_id, agent, url, "accepted", now, now)
        with self._lock:
            path = self._path(execution_id)
            if path.exists():
                raise FileExistsError("execution_id قبلاً استفاده شده است.")
            self._write(path, record)
        return record

    def update(self, execution_id: str, **changes: object) -> ExecutionRecord:
        with self._lock:
            path = self._path(execution_id)
            if not path.exists():
                raise FileNotFoundError("Execution پیدا نشد.")
            data = json.loads(path.read_text(encoding="utf-8"))
            data.update(changes)
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
            record = ExecutionRecord(**data)
            self._write(path, record)
            return record

    def get(self, execution_id: str) -> ExecutionRecord:
        path = self._path(execution_id)
        if not path.exists():
            raise FileNotFoundError("Execution پیدا نشد.")
        return ExecutionRecord(**json.loads(path.read_text(encoding="utf-8")))

    @staticmethod
    def _write(path: Path, record: ExecutionRecord) -> None:
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(record), ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)
