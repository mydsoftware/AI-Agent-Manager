"""SOP System — MetaGPT-style Standard Operating Procedures.

Core philosophy: Code = SOP(Team)
Assigns roles to agents and orchestrates them through standardized workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SOPStep:
    """A single step in a Standard Operating Procedure."""

    name: str
    role: str  # which agent type handles this
    description: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    tool_needed: str | None = None
    max_retries: int = 3


@dataclass
class SOP:
    """Standard Operating Procedure — a sequence of steps for a team."""

    name: str
    description: str
    steps: list[SOPStep] = field(default_factory=list)

    def add_step(self, step: SOPStep) -> None:
        self.steps.append(step)

    def get_steps_for_role(self, role: str) -> list[SOPStep]:
        return [s for s in self.steps if s.role == role]

    def next_step(self, completed: set[str]) -> SOPStep | None:
        """Return the next executable step based on dependencies."""
        for step in self.steps:
            # Skip if step already done (name or any output in completed)
            if step.name in completed:
                continue
            if step.outputs and all(o in completed for o in step.outputs):
                continue
            # Check if all inputs are produced by completed steps
            all_deps_met = True
            for inp in step.inputs:
                if inp not in completed:
                    all_deps_met = False
                    break
            if all_deps_met:
                return step
        return None


# ── Predefined SOPs ────────────────────────────────────────

SOFTWARE_DEV_SOP = SOP(
    name="software_development",
    description="Standard software development workflow",
    steps=[
        SOPStep("research", "researcher", "Research requirements and alternatives",
                inputs=[], outputs=["requirements"]),
        SOPStep("architecture", "planner", "Design architecture and task graph",
                inputs=["requirements"], outputs=["architecture", "task_graph"]),
        SOPStep("implement", "developer", "Implement code based on architecture",
                inputs=["architecture", "task_graph"], outputs=["code"]),
        SOPStep("test", "qa", "Write and run tests",
                inputs=["code"], outputs=["test_results"]),
        SOPStep("review", "reviewer", "Code review and quality check",
                inputs=["code", "test_results"], outputs=["review_feedback"]),
        SOPStep("fix", "developer", "Fix issues found in review",
                inputs=["review_feedback", "code"], outputs=["fixed_code"]),
        SOPStep("commit", "github", "Commit and push to repository",
                inputs=["fixed_code"], outputs=["commit_hash"]),
        SOPStep("deploy", "deploy", "Deploy to production",
                inputs=["commit_hash"], outputs=["deploy_url"]),
    ],
)

GAME_DEV_SOP = SOP(
    name="game_development",
    description="Standard game development workflow",
    steps=[
        SOPStep("idea_analysis", "game_designer", "Analyze game idea and extract specs",
                inputs=[], outputs=["game_specs"]),
        SOPStep("gdd", "game_designer", "Create Game Design Document",
                inputs=["game_specs"], outputs=["gdd"]),
        SOPStep("engine_selection", "game_designer", "Select engine and platform",
                inputs=["gdd"], outputs=["tech_stack"]),
        SOPStep("architecture", "game_developer", "Design game architecture",
                inputs=["gdd", "tech_stack"], outputs=["game_architecture"]),
        SOPStep("art_direction", "game_asset", "Define art direction and asset plan",
                inputs=["gdd"], outputs=["art_direction", "asset_plan"]),
        SOPStep("level_design", "game_level", "Design levels and layouts",
                inputs=["gdd", "game_architecture"], outputs=["level_data"]),
        SOPStep("implement", "game_developer", "Implement game code",
                inputs=["game_architecture", "tech_stack"], outputs=["game_code"]),
        SOPStep("ai_impl", "game_ai", "Implement enemy AI and game logic",
                inputs=["game_code", "gdd"], outputs=["ai_code"]),
        SOPStep("ui_impl", "game_ui", "Implement UI screens",
                inputs=["game_code", "gdd"], outputs=["ui_code"]),
        SOPStep("audio", "game_audio", "Add sound effects and music",
                inputs=["gdd"], outputs=["audio_assets"]),
        SOPStep("test", "game_qa", "Playtest and QA",
                inputs=["game_code", "ai_code", "ui_code"], outputs=["test_results"]),
        SOPStep("build", "game_build", "Build for target platforms",
                inputs=["test_results"], outputs=["build_artifacts"]),
    ],
)

WEBSITE_AUDIT_SOP = SOP(
    name="website_audit",
    description="Website audit and remediation workflow",
    steps=[
        SOPStep("scan", "researcher", "Scan website for issues",
                inputs=[], outputs=["scan_results"]),
        SOPStep("analyze", "qa", "Analyze and categorize issues",
                inputs=["scan_results"], outputs=["categorized_issues"]),
        SOPStep("fix", "developer", "Fix identified issues",
                inputs=["categorized_issues"], outputs=["fixes"]),
        SOPStep("verify", "qa", "Verify fixes work",
                inputs=["fixes"], outputs=["verification"]),
    ],
)


class SOPRunner:
    """Executes an SOP by routing tasks to appropriate agents."""

    def __init__(self, agent_registry: Any = None) -> None:
        self._registry = agent_registry
        self._results: dict[str, Any] = {}
        self._completed: set[str] = set()

    def run(self, sop: SOP, initial_context: dict | None = None) -> dict:
        """Execute the SOP end-to-end."""
        if initial_context:
            self._results.update(initial_context)
            # Mark provided context as completed
            for key in initial_context:
                self._completed.add(key)

        execution_log = []

        while True:
            step = sop.next_step(self._completed)
            if step is None:
                break

            # Gather inputs
            step_input = {}
            for inp in step.inputs:
                if inp in self._results:
                    step_input[inp] = self._results[inp]

            # Execute step
            result = self._execute_step(step, step_input)
            self._results[step.name] = result
            self._completed.add(step.name)
            # Mark outputs as completed too
            for out in step.outputs:
                self._completed.add(out)

            execution_log.append({
                "step": step.name,
                "role": step.role,
                "status": "completed",
                "outputs": step.outputs,
            })

        return {
            "sop": sop.name,
            "execution_log": execution_log,
            "results": self._results,
            "completed_steps": list(self._completed),
        }

    def _execute_step(self, step: SOPStep, inputs: dict) -> Any:
        """Execute a single SOP step. In production, routes to the actual agent."""
        # In real execution, this would call the agent via the registry
        return {
            "step": step.name,
            "role": step.role,
            "inputs_received": list(inputs.keys()),
            "status": "simulated",
        }

    def reset(self) -> None:
        self._results.clear()
        self._completed.clear()
