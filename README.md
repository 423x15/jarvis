# Jarvis — assistant IA personnel (et projet phare de stage)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Un agent IA personnel qui fait progressivement "à peu près tout ce que fait Alexis" : veille technique, rédaction de contenu (LinkedIn/YouTube), suivi de candidatures, recherche dans ses propres notes, automatisation de tâches répétitives — et, à terme, un œil sur ses projets physiques via webcam.

Ce n'est pas un side-project de plus : c'est **le véhicule pour traiter, un par un, tous les blocs du `Plan_Stage_Mistral_AI_12mois.xlsx`** (onglet *Catalogue technique*). Chaque brique de Jarvis correspond à un domaine que Mistral (et tout lab IA sérieux) attend d'un Applied AI Engineer : RAG, agents, mémoire, infra, observabilité, testing, sécurité, MLOps.

Voir [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) pour le mapping complet bloc → module → stack, et [`docs/ROADMAP.md`](docs/ROADMAP.md) pour la feuille de route semaine par semaine.

## Pourquoi Jarvis plutôt qu'un "agent support technique" générique

Le plan de stage proposait deux pistes de projet phare : un agent support inspiré de Thales, ou un petit produit "Mistral-powered". Jarvis fait mieux que les deux à la fois :

- **Produit complet, pas une démo** (pilier n°1 de Mathias) : Alexis l'utilise vraiment, tous les jours — c'est le meilleur test de qualité possible.
- **Couvre nativement tout le catalogue technique** : un assistant personnel a besoin de RAG (ses notes), d'agents (ses outils), de mémoire (le suivre dans la durée), d'infra (le faire tourner en continu), d'observabilité (savoir ce qu'il fait), de sécurité (actions irréversibles = guardrails).
- **Value talk chiffrable** (pilier n°8) : temps gagné par semaine, nombre de tâches automatisées, coût par requête — un récit concret à raconter en entretien.
- **Open source et indépendant du moteur** : Jarvis n'est pas "l'app qui utilise l'API Mistral", c'est **l'orchestration** — le moteur LLM (Mistral par défaut, mais aussi Claude, OpenAI, ou un modèle local via Ollama) est un détail d'implémentation interchangeable. C'est ce choix d'architecture qui fait la valeur du projet, pas un fournisseur en particulier — et qui permet de le déployer dans un environnement très restreint, sans clé API ni réseau sortant.

## Architecture en un coup d'œil

Hexagonale de bout en bout : la logique métier (agent, mémoire, outils) ne parle qu'à des interfaces (**ports**) ; chaque intégration externe (LLM, base de données, caméra) est un **adapter** interchangeable. Détail complet dans [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

```
                          ┌─────────────────────┐
         requêtes ───────▶│   FastAPI (app/api)  │
                          └──────────┬───────────┘
                                     ▼
                          ┌─────────────────────────┐
                          │      ORCHESTRATEUR       │
                          │  boucle ReAct + état     │◀── Tools (think, ask_user,
                          │  (skills, to-do, garde-  │     write_todo, vision…
                          │   fous) — agent.py +      │     app/core/tools/
                          │   agent_state.py          │
                          └────────────┬─────────────┘
                                       │  parle uniquement à des PORTS
                    ┌──────────────────┼──────────────────┬───────────────┐
                    ▼                  ▼                  ▼               ▼
             ┌─────────────┐   ┌──────────────┐   ┌──────────────┐  ┌───────────┐
             │ LLMProvider  │   │   KVStore     │   │ VectorStore   │  │ Capability │
             │ (port)       │   │   (port)      │   │  (port)       │  │  (port)    │
             ├─────────────┤   ├──────────────┤   ├──────────────┤  ├───────────┤
             │ Mistral      │   │ Redis         │   │ Qdrant        │  │ Caméra     │
             │ Claude       │   │ (interchange- │   │ (interchange- │  │ (registre  │
             │ OpenAI       │   │  able)        │   │  able)        │  │  optionnel)│
             │ Ollama/local │   └──────────────┘   └──────────────┘  └───────────┘
             └─────────────┘
```

## Modularité : ajouter ou retirer un bloc ne casse jamais le reste

Chaque bloc optionnel (aujourd'hui : la caméra) s'enregistre dans un **registre de capacités** au démarrage, seulement s'il répond réellement (`app/core/capabilities/registry.py`, `app/core/bootstrap.py`). Conséquence directe :

- pas de webcam branchée → l'outil de vision n'existe simplement pas pour cette session, Jarvis continue de tourner ;
- le jour où un nouveau bloc est ajouté (micro, capteur, intégration tierce), tout composant qui sait interroger le registre en profite immédiatement, sans être modifié.

## Skills : apprendre à Jarvis comme à un vrai assistant

Format calqué sur les *Skills* de Claude — un dossier `skills/<nom>/SKILL.md` (frontmatter + instructions), chargé en deux temps (nom + description toujours en mémoire, corps complet chargé à la demande par l'agent). Trois façons de le remplir : à la main, importé, ou généré depuis une tâche réussie (`app/core/skills/generator.py`). Détail du format dans [`skills/README.md`](skills/README.md).

## Stack technique (choix assumés, pas de débat inutile)

| Couche | Choix | Pourquoi |
|---|---|---|
| Langage / API | Python 3.12 + FastAPI | Standard du catalogue technique, rapide à itérer |
| LLM (port + adapters) | Mistral par défaut ; Claude, OpenAI, Ollama interchangeables | `app/core/llm/` — indépendance vis-à-vis du fournisseur |
| Orchestration agent | LangGraph | "Standard prod 2026" selon le catalogue, state graph explicite |
| Storage (ports + adapters) | Redis (court terme), Qdrant (long terme/RAG) — interchangeables | `app/core/adapters/`, `app/core/storage_factory.py` |
| Embeddings | Mistral Embed | Cohérence écosystème Mistral par défaut |
| Skills | Format SKILL.md (frontmatter + markdown) | Portable, inspiré des Skills Claude |
| Vision | OpenCV (capture) + provider vision-capable | Capacité optionnelle, dégrade proprement si absente |
| Observabilité LLM | Langfuse | Leader open-source 2026 selon le catalogue |
| Tests | pytest + DeepEval + RAGAS | Tests classiques + évals agent + évals RAG |
| Conteneurisation | Docker + docker-compose | Dockerisation systématique |
| CI/CD | GitHub Actions | — |
| Licence | MIT | Open source assumé — cf. [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Démarrage rapide

```bash
cp .env.example .env          # JARVIS_LLM_PROVIDER=mistral par défaut + la clé correspondante
docker compose up -d          # lance Qdrant + Redis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

`GET http://localhost:8000/health` répond `{"status": "ok", "capabilities": [...]}` — la liste des capacités reflète ce qui est réellement disponible dans l'environnement courant.

Pour tourner 100% en local sans aucune clé API : `JARVIS_LLM_PROVIDER=ollama` + `ollama pull llama3.2` (cf. `.env.example`).

## Structure du repo

```
jarvis/
├── app/
│   ├── main.py                    # point d'entrée FastAPI + bootstrap des capacités
│   ├── config.py                  # settings (env vars)
│   ├── api/routes.py              # endpoints HTTP
│   ├── core/
│   │   ├── agent.py               # orchestrateur (ReAct -> LangGraph) + prompt système dynamique
│   │   ├── agent_state.py         # état persistant: to-do, skills chargés, garde-fous
│   │   ├── memory.py              # mémoire court/long terme (via ports)
│   │   ├── ports/                 # interfaces: LLMProvider, KVStore, VectorStore, Capability
│   │   ├── adapters/              # implémentations storage: Redis, Qdrant
│   │   ├── llm/                   # port LLM + adapters Mistral/Anthropic/OpenAI/Ollama
│   │   ├── capabilities/registry.py  # registre des blocs optionnels
│   │   ├── bootstrap.py           # enregistre les blocs dispo au démarrage
│   │   ├── skills/                # registre, loader, générateur de skills
│   │   ├── vision/                # capacité caméra + outil look_at_workspace
│   │   ├── routines/               # routines programmées (squelette)
│   │   └── tools/                 # registre d'outils dynamique
│   └── rag/                       # ingestion + retrieval de la base perso
├── skills/                        # skills appris (format SKILL.md)
├── tests/                         # tests unitaires classiques (pytest)
├── evals/                         # golden dataset + évals agent (DeepEval)
├── docs/
│   ├── ARCHITECTURE.md            # hexagonale, modularité, mapping catalogue technique
│   └── ROADMAP.md                 # feuille de route semaine par semaine
├── docker-compose.yml              # Qdrant + Redis en local
├── Dockerfile
├── LICENSE                         # MIT
├── CONTRIBUTING.md
└── .github/workflows/ci.yml        # lint + tests automatiques
```

## Prochaine étape immédiate

Voir la semaine 1 dans [`docs/ROADMAP.md`](docs/ROADMAP.md) — l'architecture hexagonale, le registre de capacités, les skills et la vision sont déjà scaffoldés ; il n'y a plus qu'à brancher une clé API et commencer à remplir les `TODO`, dans l'ordre de la roadmap.
