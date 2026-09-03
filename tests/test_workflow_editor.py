from __future__ import annotations

from api.http import create_app
from services.project_store import ProjectStore
from services.activity_store import ActivityStore
from services.workflow_store import WorkflowStore


class FakeRuntime:
    class Governance:
        def can_use(self, agent): return True
    governance = Governance()


def make_app(tmp_path):
    projects = ProjectStore(str(tmp_path / "platform.db"))
    activity = ActivityStore(projects.database_path)
    workflows = WorkflowStore(projects.database_path)
    return create_app(team_api=object(), runtime=FakeRuntime(), project_store=projects, activity_store=activity, workflow_store=workflows), projects


def test_workflow_editor_save_and_reload(tmp_path):
    app, projects = make_app(tmp_path)
    project = projects.create(name="Demo", description="demo", request="build website")
    client = app.test_client()
    workflow = {"name":"custom","description":"edited","tasks":[
        {"id":"t1","title":"Design","description":"design UI","agent":"developer","depends_on":[],"max_attempts":3},
        {"id":"t2","title":"Test","description":"test","agent":"qa","depends_on":["t1"],"max_attempts":3}
    ]}
    response = client.put(f"/api/project/{project['id']}/workflow", json=workflow)
    assert response.status_code == 200
    assert response.get_json()["edges"] == [{"from":"t1","to":"t2"}]
    loaded = client.get(f"/api/project/{project['id']}/workflow")
    assert loaded.status_code == 200
    assert [t["id"] for t in loaded.get_json()["tasks"]] == ["t1", "t2"]


def test_workflow_editor_rejects_bad_dependency(tmp_path):
    app, projects = make_app(tmp_path)
    project = projects.create(name="Demo", description="demo", request="build website")
    response = app.test_client().put(f"/api/project/{project['id']}/workflow", json={"tasks":[
        {"id":"t1","title":"A","agent":"developer","depends_on":["missing"]}
    ]})
    assert response.status_code == 400


def test_workflow_editor_rejects_cycle(tmp_path):
    app, projects = make_app(tmp_path)
    project = projects.create(name="Demo", description="demo", request="build website")
    response = app.test_client().put(f"/api/project/{project['id']}/workflow", json={"tasks":[
        {"id":"t1","title":"A","agent":"developer","depends_on":["t2"]},
        {"id":"t2","title":"B","agent":"qa","depends_on":["t1"]}
    ]})
    assert response.status_code == 400
    assert "چرخه" in response.get_json()["error"]
