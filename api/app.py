from __future__ import annotations

from api.agent_team_api import AgentTeamAPI
from api.http import create_app
from agents.wordpress_connection_http_api import WordPressConnectionHttpApi
from runtime import ManagerRuntime


def create_manager_app() -> object:
    """برنامه اصلی را با وابستگی‌های واقعی در زمان اجرا می‌سازد."""
    runtime = ManagerRuntime()
    team_api = AgentTeamAPI(runtime.agent_team, runtime.registry_manager)
    wordpress_connection_api = WordPressConnectionHttpApi()
    return create_app(team_api, runtime, wordpress_connection_api)


app = create_manager_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
