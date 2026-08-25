from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def sample_request() -> str:
    return "check and analyze website https://example.com"


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_AGENT_MANAGER_API_KEY", "test-key-123")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
