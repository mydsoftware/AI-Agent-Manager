"""CrewAI-style Crew and Flow system.

Crews: Teams of AI agents with roles, goals, and backstories working together.
Flows: Event-driven automations that combine workflow control with agent execution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentConfig:
    """Configuration for a crew agent."""

    role: str
    goal: str
    backstory: str = ""
    tools: list[str] = field(default_factory=list)
    llm: str | None = None
    verbose: bool = True
    memory: bool = True
    max_iter: int = 15
    max_retry_limit: int = 3


@dataclass
class TaskConfig:
    """Configuration for a crew task."""

    description: str
    expected_output: str
    agent_role: str
    context: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    output_pydantic: str | None = None
    output_json: bool = False
    human_input: bool = False


@dataclass
class CrewResult:
    """Result of a crew execution."""

    success: bool
    outputs: dict[str, Any] = field(default_factory=dict)
    agent_logs: list[dict] = field(default_factory=list)
    token_usage: int = 0
    error: str | None = None


class Crew:
    """A team of agents working together on tasks.

    Inspired by CrewAI's Crew abstraction:
    - Agents have roles, goals, and backstories
    - Tasks are assigned to specific agents
    - Execution follows task dependencies
    """

    def __init__(
        self,
        agents: list[AgentConfig] | None = None,
        tasks: list[TaskConfig] | None = None,
        process: str = "sequential",  # sequential | hierarchical
        verbose: bool = True,
    ) -> None:
        self.agents = {a.role: a for a in (agents or [])}
        self.tasks = tasks or []
        self.process = process
        self.verbose = verbose
        self._results: dict[str, Any] = {}

    def add_agent(self, agent: AgentConfig) -> None:
        self.agents[agent.role] = agent

    def add_task(self, task: TaskConfig) -> None:
        self.tasks.append(task)

    def kickoff(self, inputs: dict | None = None) -> CrewResult:
        """Execute the crew's tasks."""
        if inputs:
            self._results.update(inputs)

        agent_logs = []

        for task in self.tasks:
            agent = self.agents.get(task.agent_role)
            if not agent:
                return CrewResult(
                    success=False,
                    error=f"Agent '{task.agent_role}' not found in crew",
                )

            # Gather context
            context = {}
            for ctx_name in task.context:
                if ctx_name in self._results:
                    context[ctx_name] = self._results[ctx_name]

            # Execute task (in production, this calls the LLM)
            log = {
                "task": task.description[:80],
                "agent": agent.role,
                "status": "completed",
                "context_keys": list(context.keys()),
            }
            agent_logs.append(log)

            # Store output
            output_key = task.description[:30].replace(" ", "_").lower()
            self._results[output_key] = {
                "task": task.description,
                "agent": agent.role,
                "status": "simulated",
            }

        return CrewResult(
            success=True,
            outputs=self._results,
            agent_logs=agent_logs,
        )


class Flow:
    """Event-driven automation that combines workflow control with agent execution.

    Flows allow mixing:
    - Regular Python code
    - LLM calls
    - Crew execution
    - Conditional branching
    """

    def __init__(self) -> None:
        self._steps: list[dict] = []
        self._state: dict[str, Any] = {}

    def add_step(
        self,
        name: str,
        handler: Callable | None = None,
        crew: Crew | None = None,
        condition: Callable | None = None,
    ) -> None:
        self._steps.append({
            "name": name,
            "handler": handler,
            "crew": crew,
            "condition": condition,
        })

    def set_state(self, key: str, value: Any) -> None:
        self._state[key] = value

    def get_state(self, key: str) -> Any:
        return self._state.get(key)

    def kickoff(self, inputs: dict | None = None) -> dict:
        """Execute the flow."""
        if inputs:
            self._state.update(inputs)

        results = []

        for step in self._steps:
            # Check condition
            if step["condition"] and not step["condition"](self._state):
                results.append({"step": step["name"], "status": "skipped"})
                continue

            # Execute
            if step["handler"]:
                result = step["handler"](self._state)
                self._state[step["name"]] = result
                results.append({"step": step["name"], "status": "completed"})
            elif step["crew"]:
                crew_result = step["crew"].kickoff(self._state)
                self._state[step["name"]] = crew_result.outputs
                results.append({"step": step["name"], "status": "completed"})

        return {"flow_results": results, "final_state": self._state}


# ── Predefined Crew Templates ──────────────────────────────

def create_software_team() -> Crew:
    """Create a standard software development team."""
    crew = Crew(process="sequential")
    crew.add_agent(AgentConfig(
        role="Product Manager",
        goal="Define requirements and user stories",
        backstory="Experienced PM who understands both tech and business",
    ))
    crew.add_agent(AgentConfig(
        role="Architect",
        goal="Design scalable architecture",
        backstory="Senior architect with 15+ years experience",
        tools=["filesystem", "shell"],
    ))
    crew.add_agent(AgentConfig(
        role="Developer",
        goal="Write clean, maintainable code",
        backstory="Full-stack developer proficient in multiple languages",
        tools=["filesystem", "shell", "git", "test"],
    ))
    crew.add_agent(AgentConfig(
        role="QA Engineer",
        goal="Ensure quality through testing",
        backstory="Detail-oriented QA with automation expertise",
        tools=["test", "browser"],
    ))
    crew.add_agent(AgentConfig(
        role="DevOps",
        goal="Deploy and monitor applications",
        backstory="Infrastructure expert with CI/CD experience",
        tools=["shell", "git", "deploy"],
    ))
    return crew


def create_game_team() -> Crew:
    """Create a game development team."""
    crew = Crew(process="sequential")
    crew.add_agent(AgentConfig(
        role="Game Designer",
        goal="Create compelling game design",
        backstory="Creative game designer with experience in multiple genres",
    ))
    crew.add_agent(AgentConfig(
        role="Game Developer",
        goal="Implement game mechanics and systems",
        backstory="Game programmer skilled in Godot, Unity, and web engines",
        tools=["filesystem", "shell"],
    ))
    crew.add_agent(AgentConfig(
        role="Level Designer",
        goal="Design engaging levels and progression",
        backstory="Level designer who understands pacing and player psychology",
    ))
    crew.add_agent(AgentConfig(
        role="Game Artist",
        goal="Create cohesive visual assets",
        backstory="Pixel artist and concept artist for indie games",
    ))
    crew.add_agent(AgentConfig(
        role="Game QA",
        goal="Test gameplay and find bugs",
        backstory="Game tester with keen eye for gameplay issues",
        tools=["test", "browser"],
    ))
    return crew
