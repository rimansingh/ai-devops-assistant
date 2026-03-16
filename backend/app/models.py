from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Message(BaseModel):
    role: str          # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    history: list[Message] = []


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    tool_used: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    environment: str


class MetricsResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    tools_used: dict[str, int]