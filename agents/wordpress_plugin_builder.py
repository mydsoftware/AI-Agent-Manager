from __future__ import annotations

from pathlib import Path
from agents.wordpress_requirements_agent import WordPressRequirements


class WordPressPluginBuilder:
    """قابلیت‌های تشخیص‌داده‌شده را به Plugin واقعی WordPress تبدیل می‌کند."""

    def build(self, requirements: WordPressRequirements, plugins_root: str) -> tuple[str, ...]:
        created: list[str] = []
        root = Path(plugins_root)
        features = set(requirements.features)

        if "lead-form" in features:
            plugin = root / "ai-manager-leads" / "ai-manager-leads.php"
            plugin.parent.mkdir(parents=True, exist_ok=True)
            plugin.write_text(
                "<?php\n/**\n * Plugin Name: AI Manager Leads\n * Description: Generated lead form foundation.\n */\n"
                "if (!defined('ABSPATH')) exit;\n\n"
                "add_shortcode('ai_manager_lead_form', function () {\n"
                "    return '<form method=\"post\"><input name=\"name\" required placeholder=\"نام\"><input name=\"phone\" required placeholder=\"تلفن\"><button type=\"submit\">درخواست مشاوره</button></form>';\n"
                "});\n",
                encoding="utf-8",
            )
            created.append(str(plugin))

        return tuple(created)
