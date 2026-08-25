from __future__ import annotations

import os
from typing import Any


EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/microsoft-edge",
    "/usr/bin/microsoft-edge-stable",
]


def launch_browser(playwright: Any, headless: bool = True) -> Any:
    """مرورگر را با اولویت Chromium و fallback به Edge راه‌اندازی می‌کند."""
    # تلاش اول: Chromium
    try:
        return playwright.chromium.launch(headless=headless)
    except Exception:
        pass

    # تلاش دوم: Edge
    for edge_path in EDGE_PATHS:
        if os.path.exists(edge_path):
            try:
                return playwright.chromium.launch(headless=headless, executable_path=edge_path)
            except Exception:
                continue

    raise RuntimeError("هیچ مرورگری (Chromium یا Edge) یافت نشد.")
