import os
import uuid
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)


def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(url, key)


def save_conversation(
    conversation_id: str,
    user_message: str,
    assistant_reply: str,
    tool_used: str | None,
    response_time_ms: int,
) -> None:
    """Save a conversation turn to Supabase."""
    try:
        client = get_client()
        client.table("conversations").insert({
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "user_message": user_message,
            "assistant_reply": assistant_reply,
            "tool_used": tool_used,
            "response_time_ms": response_time_ms,
        }).execute()
    except Exception as e:
        # Log but don't crash — DB failure shouldn't break the chat
        logger.warning(f"Failed to save conversation: {e}")


def get_metrics() -> dict:
    """Fetch aggregate metrics from the conversations table."""
    try:
        client = get_client()
        rows = client.table("conversations").select("*").execute().data

        if not rows:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time_ms": 0.0,
                "tools_used": {},
            }

        total = len(rows)
        times = [r["response_time_ms"] for r in rows if r.get("response_time_ms")]
        avg_time = round(sum(times) / len(times), 2) if times else 0.0

        tools_used: dict[str, int] = {}
        for row in rows:
            tool = row.get("tool_used")
            if tool:
                tools_used[tool] = tools_used.get(tool, 0) + 1

        return {
            "total_requests": total,
            "successful_requests": total,
            "failed_requests": 0,
            "average_response_time_ms": avg_time,
            "tools_used": tools_used,
        }

    except Exception as e:
        logger.error(f"Failed to fetch metrics: {e}")
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time_ms": 0.0,
            "tools_used": {},
        }