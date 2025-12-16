# LLM Agent Execution Core

**Minimal Production-Minded LLM Agent Execution System for oFoundation**

A Python-based agent execution core that orchestrates LLM-driven tool selection and execution with complete traceability. Designed for AI-native systems, ready for integration with higher-level AI orchestrators (AI CEOs, operators) and future decentralized workflows.

## Features

- 🤖 **LLM-Driven Planning**: Natural language goal processing with intelligent tool selection
- 🔧 **Extensible Tool System**: Protocol-based architecture for easy tool additions
- 📊 **Complete Traceability**: Full execution traces for debugging and auditing
- 🚀 **FastAPI HTTP API**: RESTful endpoints for AI orchestration systems
- 🔒 **Production-Minded**: Safe execution, error handling, and clean architecture
- 🎯 **Trigger.dev Ready**: Decoupled core for background job execution

## Quick Start

### Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/getting-started/installation/) (fast Python package manager)

Install UV from the official website - choose your preferred installation method:
**https://docs.astral.sh/uv/getting-started/installation/**

Available methods: pip, pipx, Homebrew, winget, Cargo, and more.

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ofoundation-python-engineer-test.git
cd ofoundation-python-engineer-test

# Copy environment file
cp .env.example .env

# Install dependencies
uv sync

# Run the server
uv run main.py
```

The API will be available at `http://127.0.0.1:8000`

- API Docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Architecture

### System Overview

```
User / AI CEO
     ↓
FastAPI HTTP API
     ↓
Agent Core (orchestration)
     ↓
LLM Client (planning)
     ↓
Tool Registry → Tools (web_search, math, governance_note)
```

### Module Structure

```
app/
├── agent/           # Agent orchestration core
│   ├── core.py      # Main Agent class
│   ├── state.py     # Execution state & traces
│   └── planner.py   # LLM-based planning
├── tools/           # Tool system
│   ├── base.py      # Tool Protocol & Registry
│   ├── web_search.py
│   ├── math.py
│   └── governance.py
├── llm/             # LLM abstraction layer
│   ├── interface.py # LLMClient Protocol
│   └── mock_client.py
├── api/             # HTTP layer
│   ├── routes.py    # FastAPI endpoints
│   └── models.py    # Request/Response schemas
├── config.py        # Configuration
└── main.py          # FastAPI app
```

### Key Design Decisions

#### 1. Protocol-Based Tools (Not Inheritance)
Tools use Python Protocols instead of base classes for maximum flexibility:

```python
# Tools implement the interface without inheritance
class MathTool:  # No (Tool) needed!
    @property
    def name(self) -> str:
        return "math"

    def run(self, input: dict) -> dict:
        ...
```

**Benefits**: Duck typing, easier mocking, no shared state, flexible implementations.

#### 2. Mock LLM as Default
No real API integration - runs out of the box with pattern-based tool selection:
- No API keys required
- Deterministic testing
- Zero API costs
- Fast development

The interface supports swapping to real LLMs (Vercel AI SDK, OpenAI, Anthropic) without code changes.

#### 3. In-Memory Storage
Governance notes use dict-based storage for simplicity:
- No database setup needed
- Perfect for demos
- Clear upgrade path to PostgreSQL/Redis

#### 4. HTTP-Independent Agent Core
Agent can be imported directly without FastAPI:
```python
from app.agent.core import Agent

agent = Agent()
result = agent.run(goal="Calculate 2+2")
```

**Perfect for**: Trigger.dev jobs, CLI tools, background workers.

#### 5. UV for Dependency Management
Fast, modern Python tooling:
- 10-100x faster than pip
- Deterministic builds with lock files
- Simple command surface

## Usage Examples

### Example 1: Math Calculation

```bash
curl -X POST http://localhost:8000/api/v1/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Calculate the result of (100 + 50) * 2",
    "tools": ["math"]
  }'
```

**Response:**
```json
{
  "status": "success",
  "output": "Calculation result: 300 (from (100 + 50) * 2)",
  "trace": [
    {
      "step": 1,
      "tool": "math",
      "input": {"expression": "(100 + 50) * 2"},
      "output": {"result": 300, "expression": "(100 + 50) * 2"},
      "error": null,
      "timestamp": "2025-12-16T10:30:00Z"
    }
  ]
}
```

### Example 2: Web Search

```bash
curl -X POST http://localhost:8000/api/v1/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Search for Python FastAPI best practices",
    "context": "Focus on production deployment",
    "tools": ["web_search"]
  }'
```

**Response:**
```json
{
  "status": "success",
  "output": "Found 3 search results for 'Python FastAPI best practices'",
  "trace": [...]
}
```

### Example 3: Governance Notes

**Adding a note:**
```bash
curl -X POST http://localhost:8000/api/v1/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Add note to PROP-2025-001: Legal review completed",
    "tools": ["governance_note"]
  }'
```

**Retrieving notes:**
```bash
curl http://localhost:8000/api/v1/governance-notes/PROP-2025-001
```

**Response:**
```json
{
  "proposal_id": "PROP-2025-001",
  "notes": [
    "Legal review completed",
    "Budget approved",
    "Ready for vote"
  ]
}
```

### Example 4: Running Python Scripts

```bash
# Math examples
uv run python examples/example_math.py

# Web search examples
uv run python examples/example_web_search.py

# Governance examples
uv run python examples/example_governance.py
```

## API Reference

### POST /api/v1/run-task

Execute agent with natural language goal.

**Request Body:**
```json
{
  "goal": "string (required)",
  "context": "string (optional)",
  "tools": ["array of tool names (optional, defaults to all)"]
}
```

**Response:**
```json
{
  "status": "success | error",
  "output": "user-facing result",
  "trace": [{"step": 1, "tool": "...", ...}]
}
```

### GET /api/v1/governance-notes/{proposal_id}

Retrieve all notes for a proposal.

**Response:**
```json
{
  "proposal_id": "string",
  "notes": ["array of note strings"]
}
```

### GET /api/v1/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "llm-agent-core",
  "version": "0.1.0"
}
```

## Development

### Running Tests

```bash
# Run example scripts as integration tests
uv run python examples/example_math.py
uv run python examples/example_web_search.py
uv run python examples/example_governance.py
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .
```

### Environment Variables

Copy `.env.example` to `.env` and adjust as needed:
```bash
cp .env.example .env
```

See `.env.example` for all available configuration options.

## Production Deployment

### Docker

```bash
# Build image
docker build -t llm-agent-core .

# Run container
docker run -p 8000:8000 llm-agent-core

# With environment variables
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  llm-agent-core
```

### Environment Configuration

Production checklist:
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Replace mock LLM with real integration
- [ ] Replace in-memory storage with database
- [ ] Add authentication/authorization
- [ ] Configure logging and monitoring

## Extension Points

### Adding a Real LLM

Replace `MockLLMClient` with a real implementation:

**1. Create `app/llm/openai_client.py`:**
```python
from app.llm.interface import LLMClient, LLMResponse
import openai

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = openai.Client(api_key=api_key)

    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        # Parse response and return LLMResponse
        ...
```

**2. Update Agent initialization:**
```python
from app.llm.openai_client import OpenAIClient
agent = Agent(llm_client=OpenAIClient(api_key="..."))
```

### Adding Database Storage

Replace `GovernanceNoteStore`:

**1. Create `app/storage/database.py`:**
```python
from sqlalchemy import create_engine

class DatabaseStore:
    def add_note(self, proposal_id: str, note: str) -> int:
        # Database operations
        ...

    def get_notes(self, proposal_id: str) -> list[str]:
        # Database queries
        ...
```

**2. Inject into tool:**
```python
from app.storage.database import DatabaseStore
store = DatabaseStore(connection_string="postgresql://...")
tool = GovernanceNoteTool(store=store)
```

### Adding New Tools

**1. Create `app/tools/my_tool.py`:**
```python
from app.tools.base import Tool, tool_registry

class MyTool:
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Does something useful"

    @property
    def input_schema(self) -> dict:
        return {"type": "object", ...}

    def run(self, input: dict) -> dict:
        # Tool logic
        return {"result": "success"}

# Auto-register
tool_registry.register(MyTool())
```

**2. Import in `app/main.py`:**
```python
import app.tools.my_tool  # Triggers registration
```

### Trigger.dev Integration

The agent core is already decoupled from HTTP:

```typescript
// trigger/agent-job.ts
import { task } from "@trigger.dev/sdk/v3";

export const agentTask = task({
  id: "agent-execution",
  run: async (payload: { goal: string; context?: string }) => {
    // Call Python agent via subprocess or API
    const result = await fetch("http://agent-api:8000/api/v1/run-task", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    return result.json();
  }
});
```

Or call Python directly:
```python
# trigger_jobs.py
from app.agent.core import Agent

def run_agent_job(goal: str, context: str = None):
    agent = Agent()
    result = agent.run(goal, context)
    return result.model_dump()
```

## Architecture Notes

### Security Features

1. **Safe Math Evaluation**: AST parsing prevents code injection
2. **Input Validation**: Pydantic models validate all inputs
3. **Error Isolation**: Tool failures don't crash the agent
4. **Max Steps Limit**: Prevents infinite execution loops

### Future Roadmap

- [ ] **Real LLM Integration**: Vercel AI SDK / OpenAI / Anthropic
- [ ] **Database Persistence**: PostgreSQL for governance notes
- [ ] **On-Chain Tools**: Blockchain interaction capabilities
- [ ] **Multi-Agent Orchestration**: Coordinate multiple agents
- [ ] **Streaming Responses**: Real-time execution updates via SSE
- [ ] **Authentication**: API key or JWT-based auth
- [ ] **Rate Limiting**: Prevent abuse
- [ ] **Metrics & Monitoring**: Prometheus/Grafana integration

### Production Considerations

**Current State**: Demo/Test Implementation
- Mock LLM (no real AI)
- In-memory storage (data lost on restart)
- No authentication
- Single-instance only

**For Production**:
1. Replace mock components with real implementations
2. Add database with connection pooling
3. Implement authentication & authorization
4. Add comprehensive error logging
5. Set up monitoring and alerts
6. Use process manager (gunicorn/uvicorn workers)
7. Add rate limiting and request validation
8. Implement caching strategies

## Testing

While formal unit tests aren't included (per spec), the example scripts serve as integration tests:

```bash
# Validate all tools work
uv run python examples/example_math.py
uv run python examples/example_web_search.py
uv run python examples/example_governance.py

# Test API endpoints
curl http://localhost:8000/api/v1/health
```

## Troubleshooting

### Module Import Errors

Make sure you're using UV to run:
```bash
uv run python examples/example_math.py
# NOT: python examples/example_math.py
```

### Port Already in Use

Change port in `.env`:
```bash
PORT=9000
```

Or specify directly:
```bash
uv run uvicorn app.main:app --port 9000
```

### Tools Not Registered

Ensure tool modules are imported in `app/main.py`:
```python
import app.tools.web_search
import app.tools.math
import app.tools.governance
```

## Contributing

This is a test project for oFoundation. For questions or issues:
1. Review the inline documentation (comprehensive docstrings)
2. Check the plan file: `.claude/plans/generic-pondering-storm.md`
3. Run example scripts to understand behavior

## License

MIT

## Acknowledgments

Built for oFoundation Python Engineer (LLM Team) test task.

Key Technologies:
- FastAPI - Modern Python web framework
- Pydantic - Data validation
- UV - Fast Python package manager
- Protocol-based design patterns
