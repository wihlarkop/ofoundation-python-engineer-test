# LLM Agent Execution Core

**Minimal Production-Minded LLM Agent Execution System for OFoundation**

A Python-based agent execution core that orchestrates LLM-driven tool selection and execution with full traceability. Designed for AI-native systems and ready to be integrated with higher-level AI orchestrators (e.g. AI CEO / operators) and future decentralized workflows.

---

## Overview

This project implements a minimal yet production-minded **LLM Agent Execution Core** with the following goals:

* Accept natural language task goals
* Decide whether to respond directly or invoke tools
* Execute tools safely and sequentially
* Maintain structured execution traces
* Expose a clean HTTP API for orchestration systems

The focus is on **architecture, clarity, and extensibility**, not feature completeness.

---

## Features

* **LLM-Driven Planning**: Natural language goal processing with tool selection logic
* **Extensible Tool System**: Protocol-based, loosely coupled tools
* **Execution Traceability**: Structured step-by-step traces for auditing and analysis
* **FastAPI API Layer**: Simple HTTP interface for external orchestrators
* **Production-Minded Design**: Error handling, safe execution, and clean boundaries
* **Trigger.dev Ready**: Agent core is decoupled from HTTP for background execution

---

## Quick Start

### Prerequisites

* Python **3.11+**

### Dependency Management

This project can be run using **standard pip**, or optionally using **UV** (the tool used during development).

**Option A: Using pip (most compatible)**

```bash
pip install -r requirements.txt
```

**Option B: Using UV (optional, faster local development)**

UV is a fast Python package manager used during development of this project.

Installation instructions:

* [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

Once installed:

```bash
uv sync
```

---

### Installation & Run

```bash
# Clone repository
git clone https://github.com/yourusername/ofoundation-python-engineer-test.git
cd ofoundation-python-engineer-test

# Create environment file
cp .env.example .env

# Run the service
uvicorn app.main:app --reload
```

The API will be available at:

* [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Architecture

### High-Level Flow

```
Client / AI Orchestrator
        ↓
FastAPI HTTP API
        ↓
Agent Core (orchestration)
        ↓
LLM Client (planning abstraction)
        ↓
Tool Registry → Tools (web_search, math, governance_note)
```

### Module Structure

```
app/
├── agent/           # Agent orchestration core
│   ├── core.py      # Main Agent logic
│   ├── state.py     # Execution state & trace models
│   └── planner.py   # LLM-based planning logic
├── tools/           # Tool implementations
│   ├── base.py      # Tool protocol & registry
│   ├── web_search.py
│   ├── math.py
│   └── governance.py
├── llm/             # LLM abstraction layer
│   ├── interface.py # LLMClient protocol
│   └── mock_client.py
├── api/             # HTTP API layer
│   ├── routes.py
│   └── models.py
├── config.py        # Configuration
└── main.py          # FastAPI app entrypoint
```

---

## Key Design Decisions

### 1. Protocol-Based Tool Interfaces

Tools implement a protocol instead of inheriting from a shared base class, enabling loose coupling and easier testing.

```python
class MathTool:
    @property
    def name(self) -> str:
        return "math"

    def run(self, input: dict) -> dict:
        ...
```

This allows flexible implementations without shared state.

---

### 2. Mock LLM by Default

The system ships with a **mock LLM client**:

* No API keys required
* Deterministic behavior
* Fast local execution

The LLM is fully abstracted and can later be replaced with a real provider (e.g. OpenAI-compatible or Vercel AI-backed gateway) without changing agent logic.

---

### 3. HTTP-Independent Agent Core

The agent can be used without FastAPI:

```python
from app.agent.core import Agent

agent = Agent()
result = agent.run(goal="Calculate 2 + 2")
```

This makes it suitable for background jobs, schedulers, or Trigger.dev-style orchestration.

---

## API Usage Examples

### Example 1: Math Tool

```bash
curl -X POST http://localhost:8000/api/v1/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Calculate (100 + 50) * 2",
    "tools": ["math"]
  }'
```

---

### Example 2: Web Search

```bash
curl -X POST http://localhost:8000/api/v1/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Search for Python FastAPI best practices",
    "context": "Focus on production usage",
    "tools": ["web_search"]
  }'
```

---

### Example 3: Governance Notes

```bash
curl -X POST http://localhost:8000/api/v1/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Add note to PROP-2025-001: Legal review completed",
    "tools": ["governance_note"]
  }'
```

Retrieve notes:

```bash
curl http://localhost:8000/api/v1/governance-notes/PROP-2025-001
```

---

## Trigger.dev Readiness

The agent core exposes a clean execution boundary and is intentionally decoupled from HTTP concerns. It can be wrapped as a background job or scheduler task without refactoring the core logic.

---

## Notes on Production Extension

This implementation is intentionally minimal and designed for extension:

* Replace mock LLM with a real provider
* Replace in-memory storage with a persistent database
* Add authentication and rate limiting
* Add monitoring and structured logging

These are deliberately omitted to keep the focus on architecture and clarity.

---

## License

MIT

---

## Acknowledgments

Built as part of the **OFoundation – Python Engineer (LLM Team)** technical assessment.
