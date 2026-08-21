from __future__ import annotations

from dataclasses import asdict
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from agents.wordpress_connection import WordPressConnectionCheck, WordPressConnectionConfig, WordPressConnectionTester


class WordPressConnectionApi:
    """لایه API ساده برای اتصال UI به Connection Tester."""

    def __init__(self, tester: WordPressConnectionTester | None = None) -> None:
        self.tester = tester or WordPressConnectionTester()

    def check(self, config: WordPressConnectionConfig) -> dict[str, object]:
        result = self.tester.test(config)
        return asdict(result)
