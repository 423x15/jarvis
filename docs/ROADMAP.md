# Feuille de route Jarvis (16 semaines)

Feuille de route semaine par semaine. Voir le tableau de statut du [README](../README.md) pour l'état réel de chaque brique.

## Phase A bis — Fondations Jarvis (J1 → J8)

| Semaine | Tâche | Bloc catalogue attaqué | Livrable |
|---|---|---|---|
| J1 | Scope + cas d'usage prioritaire (ex: veille technique + brouillons LinkedIn + suivi de tâches) + **fondation hexagonale** : ports LLM/storage, registre de capacités (déjà scaffoldés dans le starter, cf. `docs/ARCHITECTURE.md`) | System design, Patterns d'architecture | Repo Git pushé, README rempli, schéma d'archi |
| J2 | FastAPI + Docker + `/health` (expose les capacités actives) + CI GitHub Actions (lint + test) | Infra & Déploiement | CI verte |
| J3 | ReAct implémenté **à la main**, sans framework, avec 1 seul outil (recherche web) — **via la couche LLM abstraite**, jamais d'appel direct au SDK Mistral | Agents IA — patterns de raisonnement | Agent CLI qui trace un tool call en log |
| J4 | Migration vers LangGraph + 3-5 tools typés Pydantic ; les 3 conditions d'arrêt de la boucle actuelle (`app/core/agent.py`) deviennent de vrais nœuds/edges du graphe | Agents IA — function calling, orchestration | Graphe LangGraph fonctionnel |
| J5 | Mémoire court terme + long terme + 1ère brique RAG (indexer ses propres notes) — via les ports `KVStore`/`VectorStore`, jamais d'appel direct à Redis/Qdrant | RAG, Agents IA — mémoire | Agent qui se souvient d'une session à l'autre |
| J6 | Tests pytest + 10 évals DeepEval + golden dataset (15-20 cas perso) | Testing & Qualité | CI qui fait tourner les évals à chaque push |
| J7 | Dockerisation complète + déploiement speedrun (<1h chrono) sur Railway/Fly.io | Infra & Déploiement | Jarvis accessible via une URL publique |
| J8 | README + 3 ADR (Architecture Decision Records) + 1er post LinkedIn "Pourquoi j'ai choisi ce projet" | Architecture logicielle — documentation | Repo documenté, 1er post publié |

## Phase B bis — V1 déployée (J9 → J16)

| Semaine | Tâche | Bloc catalogue attaqué | Livrable |
|---|---|---|---|
| J9 | Front minimal (page + streaming SSE) | Performance & Scalabilité — latence | UI de chat fonctionnelle |
| J10 | Logging structuré (structlog) + Langfuse branché | Monitoring & Observabilité | 20 traces réelles analysées |
| J11 | Hybrid search (dense + BM25) + reranking | RAG — hybrid search, reranking | Gain de qualité de retrieval mesuré |
| J12 | Guardrails : validation humaine avant action irréversible (email, post LinkedIn) | Agents IA — human-in-the-loop, sécurité | Point de validation ajouté |
| J13 | RAG agentique (boucle retrieve → évalue suffisance → re-retrieve) | RAG — RAG agentique | Critère d'arrêt explicite implémenté |
| J14 | Routing multi-modèles selon complexité + mesure coût/latence | Performance & Scalabilité — coûts | Value talk chiffré (coût/requête) |
| J15 | Retours utilisateurs réels (soi + 2-3 amis) + itération | Testing & Qualité | 3-5 retours intégrés |
| J16 | Finalisation v1 + article technique détaillé + vidéo YouTube walkthrough | Documentation | v1 "complète" documentée et publiée |

## Phase C bis — Les différenciateurs (J17 → J20)

À ce stade Jarvis a couvert la quasi-totalité des blocs et fonctionne avec n'importe quel moteur LLM. Cette phase remplit les squelettes déjà présents dans le starter (`app/core/skills/`, `app/core/vision/`, `app/core/routines/`) — rien à créer, tout est scaffoldé, seuls les `TODO`/`NotImplementedError` restent à lever.

| Semaine | Tâche | Bloc | Livrable |
|---|---|---|---|
| J17 | Système de Skills : remplir `registry.py`/`loader.py`, écrire 3-5 vrais skills (pas l'exemple) à partir de tâches réellement faites | MLOps/LLMOps — gestion de prompts (+ différenciateur) | L'agent charge un skill pertinent via `load_skill` en conditions réelles |
| J18 | `generator.py` : générer un brouillon de skill depuis une tâche réussie, le relire, l'activer | MLOps/LLMOps | Premier skill appris "à chaud", sans écrire le SKILL.md à la main |
| J19 | Module vision : brancher une vraie caméra, tester `look_at_workspace` sur un cas concret (montage électronique, schéma au tableau...) | Différenciateur (aucun bloc catalogue direct) | Jarvis décrit correctement ce qu'il voit sur 5 cas de test |
| J20 | Routines programmées (APScheduler branché sur `app/core/routines/registry.py`) + polish open source (README public, badges) | Différenciateur + documentation | Une routine réelle tourne (ex: rappel hebdomadaire) |
