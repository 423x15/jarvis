# Contribuer à Jarvis

Jarvis est open source par choix d'architecture autant que par principe :
la valeur du projet est dans l'orchestration (agent, mémoire, skills,
sécurité), pas dans un moteur LLM propriétaire — n'importe qui doit
pouvoir le faire tourner avec le modèle de son choix, y compris en local.

## Ajouter un fournisseur LLM

1. Implémenter `app/core/llm/base.py::LLMProvider` dans
   `app/core/llm/providers/<nom>_provider.py`.
2. L'enregistrer dans `app/core/llm/factory.py`.
3. Si le fournisseur expose une API compatible OpenAI (beaucoup de serveurs
   d'inférence locaux le font), préférer réutiliser
   `OpenAICompatibleProvider` avec un `base_url` custom plutôt qu'écrire un
   nouvel adapter — cf. `OllamaProvider` en exemple dans la factory.

## Ajouter un skill

Voir `skills/README.md` — un skill est un dossier autonome, aucune
modification du code n'est nécessaire pour en ajouter un.

## Ajouter un outil

Déclarer le schéma JSON dans son propre module (cf.
`app/core/tools/web_search.py` comme référence minimale), l'enregistrer
dans `app/core/tools/registry.py` avec un scope de permission explicite
("read" / "write" / "irreversible").

## Style

`ruff check .` doit passer. Pas de règle plus stricte pour l'instant —
le projet est encore en phase de fondations (cf. `docs/ROADMAP.md`).
