"""Apprend un nouveau skill à Jarvis — le cœur de la demande d'Alexis :
pouvoir lui enseigner des choses "comme à un vrai assistant".

Deux sources possibles :
- `from_description()` : Alexis décrit la procédure en langage naturel.
- `from_task_transcript()` : Jarvis vient de réussir une tâche ; on lui
  demande de généraliser ce qu'il a fait en une procédure réutilisable
  (mêmes principes que le skill-creator de Claude).

Dans les deux cas, le LLM actif (quel qu'il soit — cf. app/core/llm/)
rédige un brouillon de SKILL.md, mais RIEN n'est jamais activé
automatiquement : le brouillon est écrit dans skills/<slug>-draft/SKILL.md
et c'est Alexis qui le relit et le renomme (retire le suffixe "-draft")
pour qu'il devienne actif. Un skill appris sans relecture humaine est un
skill qu'on ne contrôle plus — cf. Sécurité IA du catalogue technique.

Semaine 17 de la roadmap.
"""
import re
from pathlib import Path

from app.config import settings
from app.core.llm.base import Message
from app.core.llm.factory import get_provider

GENERATION_PROMPT = """Tu vas rédiger un skill au format SKILL.md pour Jarvis, l'assistant IA personnel d'Alexis.

Format attendu (frontmatter YAML + corps markdown) :
---
name: <slug-court-en-kebab-case>
description: <une phrase : QUAND ce skill doit se déclencher>
tags: [tag1, tag2]
---

# Instructions
<procédure étape par étape, réutilisable, sans détail propre à une seule fois>

Voici la source à généraliser :
{source}

Réponds UNIQUEMENT avec le contenu du fichier SKILL.md, rien d'autre.
"""


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40] or "nouveau-skill"


def _write_draft(skill_md_content: str, hint: str) -> Path:
    slug = _slugify(hint) + "-draft"
    skill_dir = Path(settings.skills_dir) / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill_md_content, encoding="utf-8")
    return skill_file


def from_description(description: str) -> Path:
    """Alexis décrit une procédure qu'il veut que Jarvis sache reproduire."""
    provider = get_provider()
    result = provider.chat([Message(role="user", content=GENERATION_PROMPT.format(source=description))])
    return _write_draft(result.content, hint=description)


def from_task_transcript(task_summary: str, steps: list[str]) -> Path:
    """Jarvis vient de réussir une tâche ; on généralise les étapes en skill.

    `steps` = les actions réellement prises (outils appelés, décisions) —
    typiquement extraites des logs Langfuse de la session (semaine 10+).
    """
    transcript = f"Tâche : {task_summary}\nÉtapes suivies :\n" + "\n".join(f"- {s}" for s in steps)
    provider = get_provider()
    result = provider.chat([Message(role="user", content=GENERATION_PROMPT.format(source=transcript))])
    return _write_draft(result.content, hint=task_summary)


learn_skill_schema = {
    "type": "function",
    "function": {
        "name": "learn_skill",
        "description": (
            "Enregistre un brouillon de nouveau skill à partir d'une description en langage naturel "
            "fournie par Alexis. Le brouillon doit être relu et validé par Alexis avant de devenir actif."
        ),
        "parameters": {
            "type": "object",
            "properties": {"description": {"type": "string", "description": "Ce que le skill doit permettre de faire"}},
            "required": ["description"],
        },
    },
}


def learn_skill_tool(description: str) -> str:
    path = from_description(description)
    return f"Brouillon écrit dans {path}. Relis-le et renomme le dossier (retire '-draft') pour l'activer."
