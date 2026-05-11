from datetime import datetime

import boto3

from config.settings import MEMORY_ID as DEFAULT_MEMORY_ID

data_client = boto3.client("bedrock-agentcore")


def save_event(
    log,
    memory_id: str,
    role: str,
    text: str,
    actor_id: str,
    session_id: str,
) -> None:
    try:
        data_client.create_event(
            memoryId=memory_id,
            actorId=actor_id,
            sessionId=session_id,
            eventTimestamp=datetime.now(),
            payload=[
                {
                    "conversational": {
                        "role": role,
                        "content": {"text": text},
                    }
                }
            ],
        )
    except Exception as e:
        log.error(f"save_event error: {str(e)}")


def load_memory_context(
    log,
    memory_id: str,
    actor_id: str,
    session_id: str,
    max_results: int = 10,
) -> str:
    try:
        response = data_client.list_events(
            memoryId=memory_id,
            actorId=actor_id,
            sessionId=session_id,
            maxResults=max_results,
        )
        events = response.get("events", [])
        context = []
        for e in events:
            try:
                text = e["conversational"]["content"]["text"]
                role = e["conversational"]["role"]
                context.append(f"{role}: {text}")
            except Exception:
                continue
        return "\n".join(context)
    except Exception as e:
        log.error(f"load_memory_context error: {str(e)}")
        return ""


def resolve_memory_id(override: str | None) -> str:
    return override or DEFAULT_MEMORY_ID
