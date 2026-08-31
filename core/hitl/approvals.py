"""Human-in-the-loop approval gateway with risk scoring and audit log."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Callable

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


RISK_BY_OP = {
    "git push": RiskLevel.HIGH,
    "deploy": RiskLevel.CRITICAL,
    "delete": RiskLevel.HIGH,
    "install dependency": RiskLevel.MEDIUM,
    "run shell": RiskLevel.MEDIUM,
    "database migration": RiskLevel.HIGH,
    "publish release": RiskLevel.CRITICAL,
    "merge": RiskLevel.HIGH,
}


@dataclass
class ApprovalRequest:
    id: str
    operation: str
    risk: RiskLevel
    payload: dict
    status: str = "pending"
    comment: str = ""
    created_at: float = field(default_factory=time.time)
    decided_at: float | None = None
    actor: str = ""


class ApprovalGateway:
    def __init__(self, expiry_seconds: float = 3600.0, auto_approve_low: bool = True, waiter: Callable[[float], None] | None = None) -> None:
        self.expiry_seconds = expiry_seconds
        self.auto_approve_low = auto_approve_low
        self.waiter = waiter
        self.requests: dict[str, ApprovalRequest] = {}
        self.audit: list[dict] = []

    def classify(self, operation: str, override: RiskLevel | None = None) -> RiskLevel:
        if override:
            return override
        return RISK_BY_OP.get(operation.lower(), RiskLevel.MEDIUM)

    def request(self, operation: str, payload: dict | None = None, risk: RiskLevel | None = None) -> ApprovalRequest:
        level = self.classify(operation, risk)
        req = ApprovalRequest(id=str(uuid.uuid4()), operation=operation, risk=level, payload=payload or {})
        if level == RiskLevel.LOW and self.auto_approve_low:
            req.status = "auto_approved"
            req.decided_at = time.time()
            req.actor = "system"
        self.requests[req.id] = req
        self._audit("created", req)
        logger.info("approval %s op=%s risk=%s status=%s", req.id, operation, level, req.status)
        return req

    def pending(self) -> list[ApprovalRequest]:
        self.expire_stale()
        return [r for r in self.requests.values() if r.status == "pending"]

    def decide(self, request_id: str, approved: bool, comment: str = "", actor: str = "human") -> ApprovalRequest:
        req = self.requests[request_id]
        if req.status != "pending":
            return req
        req.status = "approved" if approved else "rejected"
        req.comment = comment
        req.actor = actor
        req.decided_at = time.time()
        self._audit("decided", req)
        return req

    def expire_stale(self) -> None:
        now = time.time()
        for req in self.requests.values():
            if req.status == "pending" and now - req.created_at > self.expiry_seconds:
                req.status = "expired"
                req.decided_at = now
                self._audit("expired", req)

    def require(self, operation: str, payload: dict | None = None) -> ApprovalRequest:
        return self.request(operation, payload)

    def is_allowed(self, req: ApprovalRequest) -> bool:
        self.expire_stale()
        return req.status in {"approved", "auto_approved"}

    def _audit(self, event: str, req: ApprovalRequest) -> None:
        self.audit.append({"event": event, "at": time.time(), **asdict(req)})
