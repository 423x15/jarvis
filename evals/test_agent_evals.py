"""Évaluations de l'agent — pas des tests unitaires classiques mais des
mesures de qualité de comportement (trajectoire, pas juste le résultat final).

Bloc catalogue technique: Agents IA — évaluation d'agent, Testing & Qualité —
évaluation LLM style unit test.

Semaine 6 de la roadmap: écrire ici 10 évals DeepEval basées sur
evals/golden_dataset.json. Nécessite MISTRAL_API_KEY -> à exécuter à part de
la CI classique (job séparé une fois la clé disponible en secret GitHub).
"""
import json
from pathlib import Path

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"


def load_golden_dataset() -> list[dict]:
    return json.loads(GOLDEN_DATASET_PATH.read_text())["cases"]


def test_golden_dataset_loads():
    """Sanity check minimal — les vraies évals DeepEval arrivent semaine 6."""
    cases = load_golden_dataset()
    assert len(cases) > 0


# TODO semaine 6:
# from deepeval import assert_test
# from deepeval.metrics import GEval
# for case in load_golden_dataset():
#     ... appeler run_agent(case["input"]) et scorer avec GEval selon
#     case["expected_behavior"]
