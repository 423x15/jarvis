"""Vérifie le garde-fou 'irreversible' — la propriété de sécurité centrale:
une action irreversible ne peut être débloquée que par un VRAI nouveau
message humain (AgentState.human_replied_since_block), jamais par le
modèle qui insiste dans le même tour.
"""
import pytest

from app.core.agent_state import AgentState
from app.core.tools.registry import _SCOPES, _authorize


def test_irreversible_tool_blocked_on_first_attempt(monkeypatch):
    monkeypatch.setitem(_SCOPES, "fake_publish", "irreversible")
    state = AgentState()

    with pytest.raises(PermissionError):
        _authorize("fake_publish", {"text": "post"}, state)

    assert state.pending_confirmation is not None
    assert state.pending_confirmation.tool_name == "fake_publish"


def test_irreversible_tool_still_blocked_if_model_retries_same_turn(monkeypatch):
    monkeypatch.setitem(_SCOPES, "fake_publish", "irreversible")
    state = AgentState()

    with pytest.raises(PermissionError):
        _authorize("fake_publish", {"text": "post"}, state)

    # Le modèle retente dans la foulée, sans qu'aucun nouveau message
    # humain ne soit arrivé entre-temps -> toujours bloqué.
    with pytest.raises(PermissionError):
        _authorize("fake_publish", {"text": "post"}, state)


def test_irreversible_tool_allowed_after_genuine_human_reply(monkeypatch):
    monkeypatch.setitem(_SCOPES, "fake_publish", "irreversible")
    state = AgentState()

    with pytest.raises(PermissionError):
        _authorize("fake_publish", {"text": "post"}, state)

    state.human_replied_since_block = True  # simule un nouveau message HTTP d'Alexis

    _authorize("fake_publish", {"text": "post"}, state)  # ne lève plus
    assert state.pending_confirmation is None


def test_irreversible_tool_confirmation_is_scoped_to_exact_arguments(monkeypatch):
    monkeypatch.setitem(_SCOPES, "fake_publish", "irreversible")
    state = AgentState()

    with pytest.raises(PermissionError):
        _authorize("fake_publish", {"text": "post A"}, state)

    state.human_replied_since_block = True

    # Une confirmation pour "post A" n'approuve pas "post B".
    with pytest.raises(PermissionError):
        _authorize("fake_publish", {"text": "post B"}, state)


def test_non_irreversible_tool_is_never_blocked():
    state = AgentState()
    _authorize("web_search", {"query": "mistral ai"}, state)  # ne lève rien
    assert state.pending_confirmation is None
