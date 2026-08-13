# AI-Agent-Manager

Multi-agent orchestration core.

## Goal

The Manager is the control plane for a family of specialist AI agents. It decomposes user requests into tasks, routes tasks to registered specialists, tracks dependencies and results, and can use a GitHub adapter for repository operations.

## v0.1 implemented

- Agent Registry
- Task model
- Dependency-aware Manager loop
- Provider-neutral GitHub Adapter
- Specialist registry bootstrap
- Automated pytest workflow
- Initial Manager tests

## Planned runtime

```text
User -> Manager -> Planner/Router -> Specialist Agents -> Tools -> Manager -> Result
                                      |
                                      +-> GitHub Adapter
```

The concrete AI model/runtime and GitHub credentials are injected by the host application. Secrets are never stored in this repository.
