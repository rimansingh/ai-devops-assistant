import os
import uuid
import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.models import ChatRequest, ChatResponse, HealthResponse, MetricsResponse
from app.agent import run_agent
from app.database import save_conversation, get_metrics

load_dotenv()

# ── Structured JSON logging ───────────────────────────────────────────────
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "response_time_ms"):
            log["response_time_ms"] = record.response_time_ms
        if hasattr(record, "tool_used"):
            log["tool_used"] = record.tool_used
        return json.dumps(log)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)


# ── App setup ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI DevOps Assistant starting up")
    yield
    logger.info("AI DevOps Assistant shutting down")

app = FastAPI(
    title="AI DevOps Assistant",
    description="LLM-powered assistant for DevOps engineers",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
@app.head("/health")
async def health_check():
    """Health check endpoint — used by Fly.io and UptimeRobot."""
    return HealthResponse(
        status="healthy",
        environment=os.getenv("ENVIRONMENT", "production"),
    )


@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    """Returns usage metrics from the database."""
    data = get_metrics()
    return MetricsResponse(**data)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint — runs the LangChain agent and returns a response."""
    conversation_id = request.conversation_id or str(uuid.uuid4())

    logger.info(json.dumps({
        "event": "chat_request",
        "conversation_id": conversation_id,
        "message_length": len(request.message),
    }))

    try:
        result = run_agent(request.message, request.history)

        save_conversation(
            conversation_id=conversation_id,
            user_message=request.message,
            assistant_reply=result["reply"],
            tool_used=result.get("tool_used"),
            response_time_ms=result.get("response_time_ms", 0),
        )

        return ChatResponse(
            reply=result["reply"],
            conversation_id=conversation_id,
            tool_used=result.get("tool_used"),
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))