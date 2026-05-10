from typing import Any
from datetime import datetime

from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model
from mcp_client.client import get_streamable_http_mcp_client

# ⚠️ IMPORTANTE: client de memory (SDK AgentCore)
import boto3

app = BedrockAgentCoreApp()
log = app.logger

# Memory config (criado via CLI)
MEMORY_ID = "MyAgent_CustomerSupportSemantic-emALhQELQV"

# AWS client (AgentCore memory events)
data_client = boto3.client("bedrock-agentcore")

# MCP CLIENT
mcp_clients = [get_streamable_http_mcp_client()]

DEFAULT_SYSTEM_PROMPT = """
You are a helpful assistant. Use tools when appropriate.
"""

tools = []


@tool
def add_numbers(a: int, b: int) -> int:
    """Return the sum of two numbers"""
    return a + b

tools.append(add_numbers)


for mcp_client in mcp_clients:
    if mcp_client:
        tools.append(mcp_client)


_agent = None


def get_or_create_agent():
    global _agent
    if _agent is None:
        _agent = Agent(
            model=load_model(),
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            tools=tools
        )
    return _agent


def save_event(role: str, text: str, actor_id: str, session_id: str):
    """Salva evento na Memory do AgentCore"""
    data_client.create_event(
        memoryId=MEMORY_ID,
        actorId=actor_id,
        sessionId=session_id,
        eventTimestamp=datetime.now(),
        payload=[
            {
                "conversational": {
                    "role": role,
                    "content": {"text": text}
                }
            }
        ]
    )


def load_memory_context(actor_id: str, session_id: str) -> str:
    """Carrega histórico da memory"""

    response = data_client.list_events(
        memoryId=MEMORY_ID,
        actorId=actor_id,
        sessionId=session_id,
        maxResults=10
    )

    print("=== RAW MEMORY RESPONSE ===")
    print(response)

    events = response.get("events", [])

    print("=== EVENTS ===")
    print(events)

    context = []

    for e in events:
        print("=== EVENT ITEM ===")
        print(e)

        try:
            text = e["conversational"]["content"]["text"]
            role = e["conversational"]["role"]
            context.append(f"{role}: {text}")
        except Exception as err:
            print("PARSE ERROR:", err)
            continue

    result = "\n".join(context)

    print("=== FINAL CONTEXT ===")
    print(result)

    return result

@app.entrypoint
async def invoke(payload, context):
    log.info("Invoking Agent with Memory.....")

    agent = get_or_create_agent()

    # IDs obrigatórios
    actor_id = payload.get("actor_id", "default-user")
    session_id = payload.get("session_id", "default-session")
    user_message = payload.get("prompt")

    # 1. Salva input do usuário na memória
    save_event("USER", user_message, actor_id, session_id)

    # 2. Carrega memória (contexto curto)
    memory_context = load_memory_context(actor_id, session_id)

    # 3. Injeta contexto no prompt
    final_prompt = f"""
        You are a helpful assistant.
        
        Conversation history:
        {memory_context}
        
        User: {user_message}
        """

    # 4. Executa agente
    stream = agent.stream_async(final_prompt)

    full_response = ""

    async for event in stream:
        if "data" in event and isinstance(event["data"], str):
            full_response += event["data"]
            yield event["data"]

    save_event("ASSISTANT", full_response, actor_id, session_id)


if __name__ == "__main__":
    app.run()