"""Outils `write_todo` / `update_todo`.

La to-do vit dans AgentState.todo (app/core/agent_state.py), pas dans
l'historique de messages — c'est cet état, relu et reconstruit dans le
prompt système à chaque tour par app.core.agent.build_system_prompt(),
qui permet au modèle de relire puis corriger lui-même son propre plan
d'un tour sur l'autre.
"""
from app.core.agent_state import AgentState, TaskPlan, TodoItem

write_todo_schema = {
    "type": "function",
    "function": {
        "name": "write_todo",
        "description": (
            "Crée la to-do list de la tâche en cours à partir d'une liste de "
            "sous-étapes. Écrase toute to-do précédente — à appeler une fois, "
            "au moment où tu identifies qu'une tâche a plusieurs étapes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["items"],
        },
    },
}

update_todo_schema = {
    "type": "function",
    "function": {
        "name": "update_todo",
        "description": (
            "Modifie la to-do en cours : reformule un item existant (item + "
            "new_text), le marque fait (item + done: true), ou en ajoute un "
            "nouveau (new_item, sans préciser item)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Texte exact de l'item à modifier"},
                "new_text": {"type": "string", "description": "Nouveau texte de cet item"},
                "done": {"type": "boolean", "description": "Marque cet item comme fait/pas fait"},
                "new_item": {"type": "string", "description": "Ajoute un nouvel item plutôt que d'en modifier un"},
            },
        },
    },
}


def write_todo_tool(state: AgentState, items: list[str]) -> str:
    state.todo = TaskPlan(items=[TodoItem(text=i) for i in items])
    return f"{len(items)} item(s) créé(s)."


def update_todo_tool(
    state: AgentState,
    item: str | None = None,
    new_text: str | None = None,
    done: bool | None = None,
    new_item: str | None = None,
) -> str:
    if state.todo is None:
        state.todo = TaskPlan()

    if new_item is not None:
        state.todo.items.append(TodoItem(text=new_item))
        return f"Item ajouté: {new_item!r}"

    for it in state.todo.items:
        if it.text == item:
            if new_text is not None:
                it.text = new_text
            if done is not None:
                it.done = done
            return "To-do mise à jour."

    return f"Item introuvable dans la to-do: {item!r}"
