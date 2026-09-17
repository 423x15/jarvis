import pytest

from app.core.tools.ask_user import AskUserInterrupt, ask_user
from app.core.tools.think import think


def test_think_never_raises_and_returns_ack():
    assert think("je réfléchis à la suite") == "Noté."


def test_ask_user_raises_interrupt_carrying_the_question():
    with pytest.raises(AskUserInterrupt) as exc_info:
        ask_user("Quel ton pour le post ?")
    assert exc_info.value.question == "Quel ton pour le post ?"
