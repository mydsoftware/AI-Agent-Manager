"""GameDev Skills — skill router for game development agents.

Inspired by awesome-gamedev-agent-skills (68 skills for AI agents).
Automatically loads the right skill based on engine and task.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Skill:
    """A game development skill."""

    name: str
    engine: str
    category: str  # engine, concept, genre, workflow
    description: str
    content: str = ""  # SKILL.md content (prompt)

    def to_prompt(self) -> str:
        return f"## Skill: {self.name}\nEngine: {self.engine}\n\n{self.content}"


# ── Skill Database ─────────────────────────────────────────

SKILLS: list[Skill] = [
    # Godot skills
    Skill("godot-2d-movement", "godot", "engine",
          "CharacterBody2D kinematic movement with move_and_slide"),
    Skill("godot-tilemap", "godot", "engine",
          "TileMapLayer/TileSet: autotiling, terrain, collision layers"),
    Skill("godot-physics", "godot", "engine",
          "Rigid/Area/Static bodies, collision layers, raycasts"),
    Skill("godot-ui-control", "godot", "engine",
          "Control nodes: anchors, containers, themes"),
    Skill("godot-animation", "godot", "engine",
          "AnimationPlayer, AnimationTree, Tween"),
    Skill("godot-signals", "godot", "engine",
          "Event-driven design with signals + groups"),
    Skill("godot-gdscript", "godot", "engine",
          "GDScript language: typing, lifecycle, @export, signals"),

    # Unity skills
    Skill("unity-scriptableobjects", "unity", "engine",
          "ScriptableObjects for data architecture"),
    Skill("unity-physics2d", "unity", "engine",
          "2D physics: Rigidbody2D, Collider2D, joints"),
    Skill("unity-ui", "unity", "engine",
          "Canvas, UI Toolkit, responsive layout"),

    # Web engine skills
    Skill("phaser-setup", "phaser", "engine",
          "Phaser 3 project setup and scene management"),
    Skill("phaser-physics", "phaser", "engine",
          "Arcade physics, collisions, groups"),
    Skill("threejs-setup", "three.js", "engine",
          "Three.js scene, camera, renderer setup"),
    Skill("godot-export", "godot", "workflow",
          "Export to Android, Web, Windows, Linux"),

    # Concept skills
    Skill("platformer", "any", "genre",
          "Platformer mechanics: jump, double-jump, wall-jump, dash"),
    Skill("roguelike", "any", "genre",
          "Procedural generation, permadeath, inventory"),
    Skill("rpg", "any", "genre",
          "RPG systems: stats, equipment, dialogue, quests"),
    Skill("save-systems", "any", "concept",
          "Save/load system design: slots, auto-save, settings"),
    Skill("procedural-gen", "any", "concept",
          "Procedural level generation algorithms"),
    Skill("enemy-ai", "any", "concept",
          "FSM, behavior trees, patrol, chase, attack patterns"),
    Skill("boss-fights", "any", "concept",
          "Boss phase design, attack patterns, health systems"),
    Skill("inventory", "any", "concept",
          "Inventory system: items, slots, drag-and-drop"),
    Skill("dialogue-system", "any", "concept",
          "Branching dialogue with conditions and effects"),
    Skill("localization", "any", "concept",
          "Multi-language support: string tables, RTL"),
    Skill("pixel-art-assets", "any", "concept",
          "Pixel art style guide: resolution, palette, animation"),
    Skill("3d-modeling", "any", "concept",
          "3D asset pipeline: modeling, texturing, LOD"),
    Skill("audio-design", "any", "concept",
          "Game audio: SFX, music, ambient, UI sounds"),

    # Workflow skills
    Skill("itch-publish", "any", "workflow",
          "Publish to itch.io with Butler"),
    Skill("steam-publish", "any", "workflow",
          "Steam Direct submission and Steamworks"),
    Skill("android-build", "any", "workflow",
          "Android APK/AAB build and signing"),
    Skill("web-deploy", "any", "workflow",
          "Web game deployment: HTML5, WebGL"),
    Skill("performance", "any", "concept",
          "Performance optimization: FPS, memory, draw calls"),
    Skill("testing", "any", "workflow",
          "Game testing: unit, integration, playtest"),
]


class SkillRouter:
    """Routes requests to the appropriate game dev skills.

    Usage:
        router = SkillRouter()
        skills = router.route("godot", "platformer mechanics")
        # Returns: [godot-2d-movement, platformer, godot-physics]
    """

    def __init__(self, custom_skills: list[Skill] | None = None) -> None:
        self._skills = list(SKILLS)
        if custom_skills:
            self._skills.extend(custom_skills)

    def route(self, engine: str, task_description: str) -> list[Skill]:
        """Find the most relevant skills for a given engine and task."""
        matched = []
        task_lower = task_description.lower()

        # Phase 1: Engine-specific skills (exclusive)
        for skill in self._skills:
            if skill.engine.lower() == engine.lower() and skill.category == "engine":
                matched.append(skill)

        # Phase 2: Genre/concept skills (additive)
        keyword_map = {
            "platformer": ["jump", "double", "wall", "platform", "dash"],
            "roguelike": ["procedural", "random", "permadeath", "dungeon"],
            "rpg": ["rpg", "stats", "equipment", "quest", "dialogue"],
            "save": ["save", "load", "persist"],
            "ai": ["ai", "enemy", "patrol", "chase", "attack", "boss", "behavior"],
            "inventory": ["inventory", "item", "equipment"],
            "ui": ["ui", "menu", "hud", "interface"],
            "audio": ["audio", "sound", "music", "sfx"],
            "art": ["art", "sprite", "pixel", "animation", "asset"],
            "physics": ["physics", "collision", "body", "raycast"],
            "performance": ["fps", "performance", "optimize", "memory"],
            "build": ["build", "export", "deploy", "publish", "android", "web"],
        }

        for skill in self._skills:
            if skill.category in ("concept", "genre", "workflow"):
                # Check keyword match
                for keyword, triggers in keyword_map.items():
                    if any(t in task_lower for t in triggers):
                        if keyword in skill.name.lower() or keyword in skill.description.lower():
                            if skill not in matched:
                                matched.append(skill)

        return matched

    def get_skill(self, name: str) -> Skill | None:
        for skill in self._skills:
            if skill.name == name:
                return skill
        return None

    def list_all(self) -> list[Skill]:
        return list(self._skills)

    def list_by_engine(self, engine: str) -> list[Skill]:
        return [s for s in self._skills if s.engine.lower() == engine.lower()
                or s.engine == "any"]
