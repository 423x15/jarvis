# Jarvis — a personal AI agent that asks before it acts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen)

Jarvis is a personal assistant agent built around one idea: **an agent should never take an irreversible action on its own authority.** The orchestration loop, the permission model and the memory are designed around that guardrail. The LLM engine is a swappable detail (Mistral by default; Claude, OpenAI or a local Ollama model also work).

## What makes it different

| Idea | How it is implemented | Where |
|---|---|---|
| **Human-in-the-loop that cannot be bypassed by the model** | Tools carry a permission scope. An `irreversible` tool is blocked until a *new human HTTP message* arrives; the model cannot approve itself within the same turn. The approval is bound to the exact arguments of the blocked action (fingerprint), not to the tool as a whole. | `app/core/tools/registry.py`, `app/core/agent_state.py` |
| **Hexagonal architecture (ports & adapters)** | Agent logic only knows interfaces: `LLMProvider`, `KVStore`, `VectorStore`, `Capability`. Switching engine = one env var (`JARVIS_LLM_PROVIDER`), zero change in the agent. | `app/core/ports/`, `app/core/llm/`, `app/core/adapters/` |
| **A system prompt rebuilt every turn** | The prompt is regenerated from an explicit `AgentState` (loaded skills, to-do, guardrails) instead of accumulating; only `messages[]` is append-only. | `app/core/agent.py` |
| **Suspend / resume with `ask_user`** | The agent can pause to ask a question; state is persisted in the KV store and the run resumes on the next message. A `think` tool allows multi-turn reasoning without ending the loop. | `app/core/tools/` |
| **Optional capabilities register themselves** | No webcam plugged in? The vision tool simply does not exist for that session and the agent keeps running. | `app/core/capabilities/registry.py` |
| **Skills in `SKILL.md` format** | Procedures stored as folders with frontmatter + instructions, loaded on demand. A generator can draft a skill from a completed task, to be reviewed by a human before activation. | `app/core/skills/`, `skills/` |

## Architecture

```
                          ┌─────────────────────┐
         requests ───────▶│   FastAPI (app/api)  │
                          └──────────┬───────────┘
                                     ▼
                          ┌─────────────────────────┐
                          │      ORCHESTRATOR        │
                          │  ReAct loop + AgentState │◀── Tools (think, ask_user,
                          │  (skills, to-do,         │     write_todo, vision…)
                          │   guardrails)            │     app/core/tools/
                          └────────────┬─────────────┘
                                       │  talks only to PORTS
                    ┌──────────────────┼──────────────────┬───────────────┐
                    ▼                  ▼                  ▼               ▼
             ┌─────────────┐   ┌──────────────┐   ┌──────────────┐  ┌───────────┐
             │ LLMProvider  │   │   KVStore     │   │ VectorStore   │  │ Capability │
             ├─────────────┤   ├──────────────┤   ├──────────────┤  ├───────────┤
             │ Mistral      │   │ Redis         │   │ Qdrant        │  │ Camera     │
             │ Claude       │   └──────────────┘   └──────────────┘  │ (optional) │
             │ OpenAI       │                                         └───────────┘
             │ Ollama/local │
             └─────────────┘
```

Full write-up (in French): [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Honest status

| Area | Status |
|---|---|
| ReAct loop, `AgentState`, dynamic system prompt, `think` / `ask_user` | Implemented, unit-tested |
| Human-approval guardrail on irreversible tools | Implemented, unit-tested (anti self-approval rule) |
| LLM providers (Mistral, Anthropic, OpenAI, Ollama) | Implemented behind one port |
| FastAPI app, `/health` listing live capabilities, Docker, CI (ruff + pytest) | Implemented |
| Agent evals (golden dataset + DeepEval) | Present, run separately (needs an API key) |
| RAG ingestion / retrieval, Redis & Qdrant adapters | Scaffolded |
| Skills registry / generator, camera capability, scheduled routines | Scaffolded |
| Langfuse tracing, hybrid search + reranking, multi-model routing | Planned — see [`docs/ROADMAP.md`](docs/ROADMAP.md) |

15 unit tests pass and `ruff` is clean on the current `main`.

## Quick start

```bash
cp .env.example .env          # JARVIS_LLM_PROVIDER=mistral + the matching API key
docker compose up -d          # Qdrant + Redis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

`GET http://localhost:8000/health` returns `{"status": "ok", "capabilities": [...]}`.

Fully local, no API key: `JARVIS_LLM_PROVIDER=ollama` and `ollama pull llama3.2`.

Run the tests:

```bash
pytest tests/ -v
```

## Tech stack

Python 3.12 · FastAPI · LangGraph · Pydantic · Redis · Qdrant · Docker · GitHub Actions · pytest · DeepEval · MIT licence. See [`CONTRIBUTING.md`](CONTRIBUTING.md) to add an LLM provider or a skill.

## Author

Alexis Lalanne — engineering student at École des Mines de Saint-Étienne, building agent architectures (LangGraph / LangChain) in industry. [LinkedIn](https://www.linkedin.com/in/alexis-lalanne-183726207)
