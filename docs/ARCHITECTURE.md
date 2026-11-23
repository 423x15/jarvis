# Architecture de Jarvis

Ce document décrit l'architecture de Jarvis et relie chaque domaine technique (RAG, agents, observabilité, infra…) au module qui l'implémente.

## Le principe directeur : hexagonal, et vraiment modulaire

Jarvis suit une architecture **ports & adapters (hexagonale)** de bout en bout, pas seulement pour le LLM : tout ce qui parle à un service externe (moteur LLM, base clé-valeur, base vectorielle, caméra) passe par une interface abstraite (**port**), jamais par un SDK importé en dur dans la logique métier. Chaque intégration concrète (Mistral, Redis, Qdrant, une webcam...) est un **adapter**, interchangeable sans toucher au reste du code.

```
app/core/ports/        <- interfaces (LLMProvider, KVStore, VectorStore, Capability)
app/core/llm/providers/   <- adapters LLM (Mistral, Anthropic, OpenAI, Ollama)
app/core/adapters/        <- adapters storage (Redis, Qdrant)
app/core/*_factory.py     <- choisit l'adapter actif selon .env, rien d'autre ne décide
```

Concrètement :
- `app/core/agent.py` ne connaît ni `mistralai`, ni `redis`, ni `qdrant_client` — seulement `LLMProvider`, `get_short_term_history()`, `build_tools()`.
- Changer de moteur LLM (Mistral → Claude → OpenAI → un modèle Ollama local) = changer `JARVIS_LLM_PROVIDER` dans `.env`. Aucune ligne de `app/core/agent.py` ne bouge. C'est ce qui permet de déployer Jarvis dans un environnement très restreint (aucune clé API, pas de réseau sortant) avec un modèle local — au prix, assumé, de quelques couches d'adaptation par fournisseur (`app/core/llm/providers/`).
- Changer de base de données (Redis → autre chose, Qdrant → Pinecone/Weaviate/pgvector) = même principe, un nouvel adapter dans `app/core/adapters/`.

### Le registre de capacités : modularité au sens fort

Au-delà du LLM et du storage, Jarvis va plus loin : n'importe quel **bloc optionnel** (aujourd'hui la caméra, demain un micro, un capteur, une intégration tierce) implémente le port `Capability` (`app/core/ports/capability.py`) et s'enregistre — s'il répond réellement — dans `app/core/capabilities/registry.py` au démarrage (`app/core/bootstrap.py`).

Deux garanties concrètes en découlent :
1. **Retirer un bloc, ou son service externe est down → Jarvis tourne quand même.** `app/core/tools/registry.py::build_tools()` construit la liste d'outils disponibles à partir de ce qui est *réellement* enregistré, pas d'une liste figée. Pas de caméra branchée ? L'outil `look_at_workspace` n'existe simplement pas pour cette session, et l'agent continue sans planter.
2. **Ajouter un bloc → tous les blocs existants qui savent le demander en profitent immédiatement.** Le jour où la caméra est ajoutée, tout composant qui fait `registry.has("vision")` la découvre sans avoir été modifié — c'est la caméra qui vient s'annoncer au reste du système, jamais le reste du système qui va la chercher.

## La boucle : prompt système reconstruit, historique accumulé

Pas de "noyau" séparé qui déciderait de l'intention ou du routing avant la boucle : cette analyse se dissout dans le premier tour de la boucle ReAct elle-même — c'est le modèle qui, en voyant l'index des skills et la liste d'outils, décide seul s'il répond directement ou ouvre une to-do (outil `write_todo`). Un module `kernel/` séparé aurait dupliqué une décision que le modèle prend de toute façon à chaque tour.

Deux zones bien distinctes dans chaque appel au LLM (`app/core/agent.py`) :

- **Le prompt système** (`build_system_prompt(state)`) n'est **jamais accumulé** — il est régénéré intégralement à chaque tour à partir de `AgentState` (`app/core/agent_state.py`) : identité/règles fixes + index des skills + corps des skills actuellement chargés (`load_skill`/`unload_skill`) + to-do en cours. C'est cet état, pas l'historique, qui permet au modèle de relire et corriger son propre plan, et de décharger un skill qui ne sert plus.
- **`messages[]`** (l'historique de conversation, `app/core/memory.py`) est append-only : chaque tool_call et son résultat s'y ajoutent et y restent. C'est la vraie source de croissance du contexte sur une tâche longue — pas le prompt système.

Trois façons de sortir de la boucle, documentées en tête de `app/core/agent.py` :

1. **Plus de tool_call** dans la réponse → le modèle a fini, réponse finale.
2. **`MAX_HOPS` atteint** → garde-fou anti-boucle-infinie, indépendant du modèle.
3. **`ask_user` appelé** → ni une fin ni une itération de plus : une **suspension**. L'état (`AgentState.pending_question`) est persisté via le `KVStore` ; la reprise se fait au message HTTP suivant, sans plomberie spéciale côté API — c'est juste une nouvelle conversation normale dont l'historique contient déjà la question posée.

Un outil `think` (sans effet sur le monde) permet au modèle de réfléchir sur plusieurs tours sans que ça compte comme une réponse finale — sans lui, un tour 100% texte serait interprété comme la fin de la boucle.

### Le garde-fou humain sur les actions irréversibles

`app/core/tools/registry.py::_authorize` bloque tout outil au scope `"irreversible"` — mais avec une règle précise : le déblocage ne peut avoir lieu qu'entre deux messages HTTP distincts (`AgentState.human_replied_since_block`, remis à `True` une seule fois par appel à `run_agent()`, juste après réception d'un vrai message d'Alexis), jamais par un tool_call du modèle lui-même dans le même tour. Sans cette règle, rien n'empêcherait techniquement le modèle de "s'auto-approuver" en insistant. La confirmation est en plus scopée aux arguments exacts de l'action bloquée (`fingerprint()`), pas un blanc-seing sur l'outil entier.

## Domaines techniques ↔ modules

| Domaine (plan) | Sous-thème prioritaire | Module Jarvis | Emplacement | Stack |
|---|---|---|---|---|
| RAG | Chunking, embeddings, bases vectorielles | Base de connaissance perso | `app/rag/ingest.py` | LlamaIndex/LangChain splitters, Mistral Embed, port `VectorStore` |
| RAG | Hybrid search, reranking | Retrieval avancé (v2, semaine 11) | `app/rag/retriever.py` | BM25 + dense, Cohere Rerank |
| RAG | RAG agentique | Boucle retrieve → évalue → re-retrieve | `app/core/agent.py` | LangGraph, critère d'arrêt explicite |
| RAG | Évaluation RAG | Golden dataset + RAGAS | `evals/` | RAGAS |
| Agents IA | Function calling / tool use | Registre d'outils dynamique | `app/core/tools/registry.py` | Pydantic, schémas stricts, capacités |
| Agents IA | Orchestration | Boucle ReAct + état de l'agent | `app/core/agent.py`, `app/core/agent_state.py` | LangGraph (state graph) |
| Agents IA | Patterns de raisonnement | ReAct à la main (semaine 3), puis LangGraph | `app/core/agent.py` | from scratch, puis LangGraph |
| Agents IA | Mémoire d'agent | Court terme (port `KVStore`) + long terme (port `VectorStore`) | `app/core/memory.py` | Redis + Qdrant, interchangeables |
| Agents IA | Guardrails & sécurité | Scopes de permission par outil, validation stricte | `app/core/tools/registry.py` | Pydantic, sandboxing (v2) |
| Agents IA | Human-in-the-loop | Validation avant action irréversible (envoi email, post LinkedIn) | `app/core/agent.py` | LangGraph interrupts |
| Agents IA | Évaluation d'agent | Scénarios de test + taux de succès | `evals/test_agent_evals.py` | DeepEval |
| Architecture logicielle | Design d'API | Contrats clairs, OpenAPI | `app/api/routes.py` | FastAPI + OpenAPI |
| Architecture logicielle | Patterns d'architecture | Hexagonal / ports & adapters, de bout en bout | `app/core/ports/`, `app/core/adapters/`, `app/core/llm/` | voir section ci-dessus |
| Architecture logicielle | Documentation d'archi | Architecture Decision Records | `docs/adr/` (à créer semaine 8) | Markdown ADR |
| Infra & Déploiement | Conteneurisation | Dockerfile multi-stage | `Dockerfile`, `docker-compose.yml` | Docker |
| Infra & Déploiement | CI/CD | Lint + tests + build automatiques | `.github/workflows/ci.yml` | GitHub Actions |
| Infra & Déploiement | Inférence LLM optimisée | Déploiement 100% local, zéro clé API | `app/core/llm/providers/openai_compatible_provider.py` (config Ollama) | vLLM / Ollama |
| Monitoring & Observabilité | Logging structuré | Logs JSON dès la v1, y compris les capacités actives | `app/main.py` | structlog |
| Monitoring & Observabilité | Observabilité LLM | Traces de chaque appel modèle | `app/core/agent.py` | Langfuse |
| Testing & Qualité | Tests classiques | Couverture correcte | `tests/` | pytest |
| Testing & Qualité | Évaluation LLM | Évals type unit test | `evals/test_agent_evals.py` | DeepEval |
| Data & Pipelines | Ingestion pour LLM | Pipeline complet parsing → chunking → embedding → indexation | `app/rag/ingest.py` | LlamaIndex/LangChain |
| MLOps / LLMOps | Gestion de prompts | Prompts versionnés séparément du code | `app/core/prompts/` (v2) | registre maison, puis Langfuse |
| MLOps / LLMOps | Apprentissage / gestion de skills | Registre + progressive disclosure + génération depuis une tâche | `app/core/skills/`, `skills/` | format SKILL.md (frontmatter + markdown) |
| Sécurité IA | Prompt injection & jailbreak | Red teaming manuel puis Promptfoo | `evals/` (v2) | Promptfoo |
| Performance & Scalabilité | Latence | Streaming de tokens | `app/api/routes.py` (v2, semaine 9) | SSE |
| Performance & Scalabilité | Coûts | Routing multi-modèles selon complexité | `app/core/agent.py` (v2, semaine 14) | routing custom |

## Les 3 différenciateurs 

Ces trois blocs sont la valeur ajoutée propre à Jarvis en tant que produit, et existent uniquement grâce à l'architecture hexagonale ci-dessus.

| Différenciateur | Ce que ça permet | Emplacement | Statut |
|---|---|---|---|
| **Skills** | Apprendre une procédure à Jarvis (à la main, depuis une tâche réussie, ou importée) sans toucher au code | `app/core/skills/` (registry, loader, generator), `skills/` | Scaffoldé — à remplir |
| **Vision / caméra** | Jarvis "voit" un projet physique en cours via webcam | `app/core/vision/` (camera, tool), enregistré comme capacité optionnelle | Scaffoldé — à remplir |
| **Routines programmées** | Déclencher un skill ou une tâche sur un cron ("tous les lundis...") | `app/core/routines/registry.py` | Scaffoldé — scheduler (APScheduler) à brancher |
