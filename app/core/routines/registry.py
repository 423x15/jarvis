"""Routines programmées — l'équivalent pour Jarvis des tâches planifiées
("tous les lundis, relis mes brouillons LinkedIn en attente").

Une routine est volontairement légère : un déclenchement (cron) + soit un
skill à exécuter, soit une tâche en langage naturel passée à run_agent().
Pas de scheduler branché pour l'instant — recommandation: APScheduler
(BackgroundScheduler) lancé depuis app/main.py au démarrage, une fois ce
squelette rempli.

Extension à traiter après la v1 (post-J16 de la roadmap, en même temps que
les Skills et la Vision).
"""
from dataclasses import dataclass


@dataclass
class Routine:
    name: str
    cron: str  # ex: "0 9 * * MON" -> tous les lundis 9h
    skill_or_task: str  # nom d'un skill (app/core/skills/) ou message en langage naturel
    enabled: bool = True


_routines: list[Routine] = []


def register(routine: Routine) -> None:
    _routines.append(routine)


def list_routines() -> list[Routine]:
    return list(_routines)


# TODO: brancher APScheduler ici — pour chaque Routine activée, programmer
# un job qui appelle app.core.agent.run_agent(routine.skill_or_task, ...)
# ou charge directement le skill correspondant.
