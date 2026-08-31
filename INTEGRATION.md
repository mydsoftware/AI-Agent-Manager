# Integration patches for existing files

Copy the new modules into the repository root (already on branch `feature/platform-extensions`).

## runtime.py
```python
from core.bootstrap import build_services
self.platform = build_services()
if self.platform.settings.plugins_enabled:
    self.platform.plugins.load_all()
```

## agents/registry.py
```python
from .database_agent import DatabaseAgent
from .documentation_agent import DocumentationAgent
registry.register(DatabaseAgent)
registry.register(DocumentationAgent)
```

## http_api / api app
```python
from api.platform_routes import create_platform_blueprint
app.register_blueprint(create_platform_blueprint(runtime.platform))
```

## tools/python.py & tools/shell.py
Route through `runtime.platform.sandbox`.

## deploy / git push
Call `runtime.platform.approvals.require(...)` first.

See ENV.example.additions for environment flags.
