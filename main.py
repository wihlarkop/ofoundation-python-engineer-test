"""FastAPI application entry point.

This module creates and configures the FastAPI application,
registers routes, sets up middleware, and provides startup/shutdown hooks.

The application can be run via:
- uvicorn app.main:app --reload (development)
- uv run uvicorn app.main:app --reload (with UV)
- Docker container
- Gunicorn with uvicorn workers (production)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.tools.governance
import app.tools.math

# Import tool modules to trigger registration
import app.tools.web_search
from app.api.routes import router
from app.config import settings
from app.logger import setup_logger
from app.tools.base import tool_registry

# Setup logger
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events.

    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown").
    This is the recommended approach in FastAPI 0.109.0+.

    Yields control to the application, then runs cleanup on shutdown.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("LLM Agent Execution Core starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"LLM Provider: {settings.llm_provider}")

    # Report registered tools
    tools = tool_registry.get_all()
    logger.info(f"Registered tools: {len(tools)}")
    for tool_name, tool in tools.items():
        logger.info(f"  - {tool_name}: {tool.description[:60]}...")

    logger.info("API Endpoints:")
    logger.info("  - POST   /api/v1/run-task")
    logger.info("  - GET    /api/v1/governance-notes/{proposal_id}")
    logger.info("  - GET    /api/v1/health")
    logger.info("Docs available at:")
    logger.info(f"  - http://{settings.host}:{settings.port}/docs")
    logger.info(f"  - http://{settings.host}:{settings.port}/redoc")
    logger.info("=" * 60)

    yield  # Application runs here

    # Shutdown
    logger.info("LLM Agent Execution Core shutting down...")
    # In production: close database connections, flush logs, etc.


# Create FastAPI app with lifespan
app: FastAPI = FastAPI(
    title="LLM Agent Execution Core",
    description=(
        "Minimal production-minded agent execution system for oFoundation. "
        "Orchestrates LLM-driven tool execution with complete traceability."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes with prefix
app.include_router(router, prefix="/api/v1", tags=["agent"])


# Direct execution support (python -m app.main)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
