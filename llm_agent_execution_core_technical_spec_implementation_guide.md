# Test Task – Python Engineer (LLM Team)

## Project Title
**Minimal Production‑Minded LLM Agent Execution Core**

---

## 1. Context & Goal

You are asked to design and implement a **minimal but production‑oriented LLM Agent Execution Core** in Python. The system should be able to:

- Accept a natural‑language goal
- Select and sequence tools using an LLM
- Maintain execution state and traceability
- Expose a clean HTTP API for orchestration by higher‑level AI systems (e.g. an AI CEO / Operator)

The implementation **does not require real decentralized or on‑chain integration**, but the architecture **must be clearly extensible** toward such use cases.

This project emphasizes:
- Clean Python architecture
- Robust abstractions
- Traceability and reliability
- Readiness for AI‑native and decentralized execution

---

## 2. Functional Requirements

### 2.1 Core Agent Behavior

Implement an `Agent` class that:

**Inputs**
- `goal: str`
- `context: Optional[str]`
- `tools: List[ToolDefinition]`

**Responsibilities**
- Decide whether to answer directly or call tools
- Choose tools and their execution order via an LLM
- Maintain step‑by‑step execution state
- Capture structured execution traces
- Return a final structured result

**Output (Final Result Object)**
```json
{
  "status": "success | error",
  "output": "final user‑facing result",
  "trace": [
    {
      "step": 1,
      "tool": "WebSearchTool",
      "input": {...},
      "output": {...},
      "error": null
    }
  ]
}
```

> Note: LLM chain‑of‑thought should NOT be exposed. Preserve reasoning structure only.

---

## 3. Tooling System

### 3.1 Tool Interface

Define a common tool abstraction:

```python
class Tool(Protocol):
    name: str
    description: str
    input_schema: dict

    def run(self, input: dict) -> dict:
        ...
```

### 3.2 Required Tools

#### 1. WebSearchTool
- Input: `{ "query": str }`
- Output: list of search result summaries
- Can be mocked or use a real API

#### 2. MathTool
- Input: `{ "expression": str }`
- Performs **safe arithmetic only**
- Must include validation and error handling

#### 3. GovernanceNoteTool
- Input: `{ "proposal_id": str, "note": str }`
- Appends notes to an **in‑memory store**
- Store structure:
```python
{ proposal_id: List[str] }
```

---

## 4. LLM Abstraction Layer

### 4.1 LLM Client Interface

The LLM must be abstracted behind a clean interface:

```python
class LLMClient(Protocol):
    def generate(self, prompt: str) -> dict:
        ...
```

### 4.2 Implementation Constraint

- Underlying implementation **must use Vercel AI SDK (v5+)**
- Must be swappable for a future internal “Sovereign AI CEO” model
- Mocking is acceptable for local testing

---

## 5. Execution & State Management

### 5.1 Agent State

Maintain minimal execution state:

```python
class AgentState:
    steps: List[ExecutionStep]
    memory: dict
```

Each step should include:
- Tool name
- Input arguments
- Output
- Errors (if any)
- Timestamp (optional)

---

## 6. HTTP API (FastAPI Preferred)

### 6.1 Endpoints

#### POST /run-task

Request:
```json
{
  "goal": "string",
  "context": "optional string",
  "tools": ["web_search", "math", "governance_note"]
}
```

Response:
- Final result object + trace

---

#### GET /governance-notes/{proposal_id}

Returns:
```json
{
  "proposal_id": "abc",
  "notes": ["note 1", "note 2"]
}
```

---

## 7. Architecture Requirements

### 7.1 Module Separation

Recommended structure:
```
app/
 ├─ agent/
 │   ├─ core.py        # Agent orchestration
 │   ├─ state.py       # AgentState & ExecutionStep
 │   └─ planner.py     # LLM‑driven tool planning
 ├─ tools/
 │   ├─ base.py
 │   ├─ web_search.py
 │   ├─ math.py
 │   └─ governance.py
 ├─ llm/
 │   ├─ interface.py
 │   └─ vercel_client.py
 ├─ api/
 │   └─ routes.py
 └─ main.py
```

---

## 8. Trigger.dev Readiness

- Expose a clean execution entry point
- Agent execution should be callable as a job
- Avoid tight coupling to HTTP layer

---

## 9. Deliverables

### Required
- GitHub repository
- Clean, runnable Python service
- README.md including:
  - Architecture explanation
  - How to run locally
  - 2–3 example task executions

### Optional (Strongly Preferred)
- Dockerfile
- Notes on future extension:
  - On‑chain tools
  - Governance workflows
  - Scheduled AI tasks

---

## 10. Constraints & Guidelines

- Timebox: ~24 hours (quality > completeness)
- FastAPI preferred
- No UI required
- Focus on backend clarity and extensibility
- You may use AI coding assistants

---

## 11. Claude Code Implementation Prompt (Copy‑Paste)

> You are implementing a minimal, production‑minded LLM Agent Execution Core in Python. Follow this spec exactly. Prioritize clean architecture, modular design, tool abstractions, execution traces, and FastAPI APIs. Mock LLM calls if needed but preserve interfaces. Do not over‑engineer. Focus on clarity, extensibility, and correctness.

