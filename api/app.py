from __future__ import annotations

from api.agent_team_api import AgentTeamAPI
from api.agent_logs_api import register_agent_logs_api
from api.github_api import register_github_api
from api.http import create_app
from api.memory_knowledge_api import register_memory_knowledge_api
from agents.wordpress_connection_http_api import WordPressConnectionHttpApi
from runtime import ManagerRuntime


def create_manager_app() -> object:
    """برنامه اصلی را با وابستگی‌های واقعی در زمان اجرا می‌سازد."""
    runtime = ManagerRuntime()
    team_api = AgentTeamAPI(runtime.agent_team, runtime.registry_manager)
    wordpress_connection_api = WordPressConnectionHttpApi()
    app = create_app(team_api, runtime, wordpress_connection_api)
    register_memory_knowledge_api(app, str(runtime.persistent_memory.database_path))
    register_agent_logs_api(app, str(runtime.persistent_memory.database_path))
    register_github_api(app)
    return app


app = create_manager_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
