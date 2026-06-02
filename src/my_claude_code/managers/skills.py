from pathlib import Path
import re
import yaml

class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills = {}
        self._load_all()

    def _load_all(self):
        if not self.skills_dir.exists():
            return
        
        for f in sorted(self.skills_dir.rglob("SKILL.md")):
            text = f.read_text()
            meta, body = self._parse_frontmatter(text)
            name = meta.get("name", f.parent.name)
            self.skills[name] = {"meta": meta, "body": body, "path": str(f)}

    def _parse_frontmatter(self, text:str):
        """Parse YAML frontmatter between --- delimiters."""
        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
        if not match:
            return {}, text
        try:
            meta = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            meta = {}
        return meta, match.group(2).strip()

    def get_descriptions(self):
        """Layer 1: get short descriptions of all skills for the system prompts"""
        if not self.skills:
            return f"(no skills available)"
        
        lines = []
        for name, skill in self.skills.items():
            desc = skill["meta"].get("descriptipn", "No description")
            tags = skill["meta"].get("tags", "")
            line = f"  - {name}: {desc}"
            if tags:
                line += f" [{tags}]"
            lines.append(line)
        return '\n'.join(lines)

    def get_content(self, name:str):
        """Layer 2 : get full skill body if the modle use load_skill"""
        skill = self.skills.get(name)
        if not skill:
            return f"<ERROR> Unknown skill {name}. Available: {',.'.join(self.skills.keys())}</ERROR>"
        return f"<skill name=\"{name}\">\n{skill['body']}\n</skill>"
