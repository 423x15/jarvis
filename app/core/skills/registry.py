"""Registre des skills — implémente la "progressive disclosure".

Domain: MLOps/LLMOps (gestion de prompts) + Agents IA
(function calling). Analogue direct du système de Skills de Claude, en
version portable/open source: un dossier = un skill, un YAML frontmatter
+ un corps markdown.

Semaine 17 de la roadmap.
"""
from dataclasses import dataclass
from pathlib import Path

import yaml

from app.config import settings


@dataclass
class SkillMeta:
    name: str
    description: str
    tags: list[str]
    path: Path


def _skills_root() -> Path:
    return Path(settings.skills_dir)


def list_skills() -> list[SkillMeta]:
    """Scanne skills/*/SKILL.md et n'en extrait QUE le frontmatter (name +
    description + tags) — jamais le corps. C'est ce qui garde l'index léger.
    """
    root = _skills_root()
    if not root.exists():
        return []

    metas = []
    for skill_dir in sorted(root.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        frontmatter, _ = split_frontmatter(skill_file.read_text(encoding="utf-8"))
        metas.append(
            SkillMeta(
                name=frontmatter.get("name", skill_dir.name),
                description=frontmatter.get("description", ""),
                tags=frontmatter.get("tags", []),
                path=skill_file,
            )
        )
    return metas


def skills_index_prompt() -> str:
    """Ce qui va dans le prompt système en permanence — nom + description
    seulement. Le corps complet se charge via app/core/skills/loader.py.
    """
    skills = list_skills()
    if not skills:
        return "(Aucun skill appris pour le moment.)"
    lines = [f"- {s.name}: {s.description}" for s in skills]
    return "\n".join(lines)


def split_frontmatter(raw: str) -> tuple[dict, str]:
    if not raw.startswith("---"):
        return {}, raw
    _, fm, body = raw.split("---", 2)
    return yaml.safe_load(fm) or {}, body.strip()
