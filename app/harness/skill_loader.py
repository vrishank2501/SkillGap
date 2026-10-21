import os
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import settings

class SkillDefinition:
    def __init__(self, name: str, command: str, version: str, description: str, instructions: str, path: str):
        self.name = name
        self.command = command
        self.version = version
        self.description = description
        self.instructions = instructions
        self.path = path

    def __repr__(self):
        return f"<SkillDefinition name={self.name} command={self.command}>"

class SkillLoader:
    """Loads and caches SKILL.md definitions from the skills folder."""

    def __init__(self, skills_dir: Optional[str] = None):
        self.skills_dir = Path(skills_dir or settings.SKILLS_DIR)
        self._skills: Dict[str, SkillDefinition] = {}
        self._command_map: Dict[str, str] = {}
        self.reload_skills()

    def reload_skills(self):
        self._skills.clear()
        self._command_map.clear()

        if not self.skills_dir.exists():
            return

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            content = skill_file.read_text(encoding="utf-8")
            metadata, instructions = self._parse_frontmatter(content)
            name = metadata.get("name", skill_dir.name)
            command = metadata.get("command", f"/{name}")
            version = metadata.get("version", "1.0.0")
            description = metadata.get("description", "")

            skill_def = SkillDefinition(
                name=name,
                command=command,
                version=version,
                description=description,
                instructions=instructions,
                path=str(skill_file)
            )

            self._skills[name] = skill_def
            self._command_map[command.lower()] = name

    def _parse_frontmatter(self, content: str):
        metadata = {}
        instructions = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                header = parts[1]
                instructions = parts[2].strip()
                for line in header.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip('"').strip("'")
        return metadata, instructions

    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        return self._skills.get(name)

    def get_skill_by_command(self, command: str) -> Optional[SkillDefinition]:
        cmd_clean = command.strip().lower()
        if not cmd_clean.startswith("/"):
            cmd_clean = f"/{cmd_clean}"
        skill_name = self._command_map.get(cmd_clean)
        if skill_name:
            return self._skills.get(skill_name)
        return None

    def list_skills(self) -> Dict[str, SkillDefinition]:
        return self._skills

skill_loader = SkillLoader()

