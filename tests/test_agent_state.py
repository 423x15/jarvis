from app.core.agent_state import AgentState, TaskPlan, TodoItem, fingerprint


def test_agent_state_roundtrip_through_json():
    state = AgentState(
        loaded_skills={"example-linkedin-post": "corps du skill"},
        todo=TaskPlan(items=[TodoItem("Écrire le brouillon", done=True), TodoItem("Faire valider")]),
    )
    restored = AgentState.from_json(state.to_json())

    assert restored.loaded_skills == {"example-linkedin-post": "corps du skill"}
    assert restored.todo.items[0].text == "Écrire le brouillon"
    assert restored.todo.items[0].done is True
    assert restored.todo.items[1].done is False


def test_agent_state_from_empty_json_is_fresh_state():
    state = AgentState.from_json(None)
    assert state.loaded_skills == {}
    assert state.todo is None
    assert state.pending_question is None


def test_fingerprint_is_stable_regardless_of_key_order():
    assert fingerprint("publish", {"a": 1, "b": 2}) == fingerprint("publish", {"b": 2, "a": 1})


def test_fingerprint_differs_for_different_arguments():
    assert fingerprint("publish", {"text": "v1"}) != fingerprint("publish", {"text": "v2"})
