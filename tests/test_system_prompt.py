"""Le prompt système doit refléter EXACTEMENT l'état courant, ni plus ni
moins : un skill déchargé (absent de AgentState.loaded_skills) ne doit
plus jamais y apparaître.
"""
from app.core.agent import build_system_prompt
from app.core.agent_state import AgentState, TaskPlan, TodoItem


def test_system_prompt_includes_loaded_skill_and_todo_state():
    state = AgentState(
        loaded_skills={"example-linkedin-post": "contenu très spécifique du skill"},
        todo=TaskPlan(items=[TodoItem("Étape 1", done=True), TodoItem("Étape 2")]),
    )
    prompt = build_system_prompt(state)

    assert "contenu très spécifique du skill" in prompt
    assert "[x] Étape 1" in prompt
    assert "[ ] Étape 2" in prompt


def test_system_prompt_omits_skill_once_unloaded():
    state = AgentState(loaded_skills={})  # simule un unload_skill() déjà passé
    prompt = build_system_prompt(state)
    assert "contenu très spécifique du skill" not in prompt


def test_system_prompt_has_no_todo_section_when_no_task_open():
    state = AgentState()
    prompt = build_system_prompt(state)
    assert "TA TO-DO ACTUELLE" not in prompt
