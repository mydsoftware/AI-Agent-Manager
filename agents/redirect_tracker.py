from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin


REDIRECT_STATUSES = {301, 302, 303, 307, 308}


@dataclass(frozen=True)
class RedirectObservation:
    """اطلاعات یک Redirect HTTP برای گزارش ممیزی سایت."""
    source_url: str
    status: int
    location: str
    destination_url: str


class RedirectTracker:
    """تشخیص و ثبت Redirectهای HTTP بدون دنبال‌کردن کورکورانه حلقه‌ها."""

    def __init__(self) -> None:
        self.observations: list[RedirectObservation] = []

    @staticmethod
    def resolve(source_url: str, status: int, location: str | None) -> str | None:
        """مقصد Redirect را از Location به URL مطلق تبدیل می‌کند."""
        if status not in REDIRECT_STATUSES or not location:
            return None
        return urljoin(source_url, location.strip())

    def record(self, source_url: str, status: int, location: str | None) -> RedirectObservation | None:
        """Redirect معتبر را ثبت می‌کند."""
        destination = self.resolve(source_url, status, location)
        if destination is None:
            return None
        observation = RedirectObservation(source_url, status, location.strip(), destination)
        self.observations.append(observation)
        return observation
