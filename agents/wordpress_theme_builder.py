from __future__ import annotations

from pathlib import Path
from agents.wordpress_requirements_agent import WordPressRequirements


class WordPressThemeBuilder:
    """Requirements را به صفحات واقعی PHP داخل Theme تبدیل می‌کند."""

    def build(self, requirements: WordPressRequirements, theme_root: str) -> tuple[str, ...]:
        root = Path(theme_root)
        root.mkdir(parents=True, exist_ok=True)
        created: list[str] = []

        for page in requirements.pages:
            if page.slug == "home":
                filename = "front-page.php"
            else:
                filename = f"page-{page.slug}.php"
            sections = "".join(f'<section class="section-{section}"><h2>{section.replace("-", " ").title()}</h2></section>\n' for section in page.sections)
            content = f"<?php get_header(); ?>\n<main class=\"site-page site-page-{page.slug}\">\n<h1>{page.title}</h1>\n{sections}</main>\n<?php get_footer(); ?>\n"
            target = root / filename
            target.write_text(content, encoding="utf-8")
            created.append(str(target))

        css = root / "style.css"
        css.write_text(
            "/* Theme Name: AI Manager Generated Theme */\n"
            ".site-page{max-width:1200px;margin:auto;padding:40px 20px}.section-hero{min-height:320px}.section-cta{padding:30px}\n",
            encoding="utf-8",
        )
        created.append(str(css))
        return tuple(created)
