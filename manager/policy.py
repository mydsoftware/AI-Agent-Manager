from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDecision:
    """نتیجه بررسی مجوز اجرای عملیات."""

    allowed: bool
    reason: str


def authorize(*, action: str, mode: str, access: bool) -> PolicyDecision:
    """سیاست مرکزی اجرای Agent را اعمال می‌کند."""
    normalized_action = action.strip().lower()
    normalized_mode = mode.strip().lower()

    if normalized_mode not in {"pre_contract", "post_contract"}:
        return PolicyDecision(False, "حالت اجرای درخواست معتبر نیست.")

    if normalized_mode == "pre_contract":
        if access:
            return PolicyDecision(False, "در حالت قبل از قرارداد، دسترسی نباید فعال باشد.")
        if normalized_action not in {"audit", "website-audit"}:
            return PolicyDecision(False, "قبل از قرارداد فقط عملیات ممیزی مجاز است.")
        return PolicyDecision(True, "ممیزی قبل از قرارداد مجاز است.")

    if normalized_mode == "post_contract" and not access:
        return PolicyDecision(False, "برای عملیات بعد از قرارداد، دسترسی معتبر الزامی است.")

    return PolicyDecision(True, "عملیات بعد از قرارداد مجاز است.")
