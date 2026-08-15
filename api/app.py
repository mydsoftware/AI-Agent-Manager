from __future__ import annotations

from api.agent_team_api import AgentTeamAPI
from api.http import create_app
from runtime import ManagerRuntime


runtime = ManagerRuntime()
team_api = AgentTeamAPI(runtime.agent_team, runtime.registry_manager)
app = create_app(team_api, runtime)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
