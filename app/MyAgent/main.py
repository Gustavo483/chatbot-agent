import json

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from agents import get_or_create_strands_agent, get_registration
from config.settings import DEFAULT_AGENT_ID
from model.load import load_model
from runtime.memory import load_memory_context, resolve_memory_id, save_event
from runtime.responses import (
    normalize_agent_output,
    response_payload,
    response_to_assistant_text,
)

app = BedrockAgentCoreApp()
log = app.logger


@app.entrypoint
async def invoke(payload, context):
    try:
        agent_id = payload.get("agent_id", DEFAULT_AGENT_ID)
        log.info(f"Invoking agent_id={agent_id!r}")

        try:
            registration = get_registration(agent_id)
        except KeyError as e:
            yield response_payload(
                {
                    "action": "ERROR",
                    "message": str(e),
                    "agent_id": agent_id,
                }
            )
            return

        strands_agent = get_or_create_strands_agent(registration, load_model())
        memory_id = resolve_memory_id(registration.memory_id)

        actor_id = payload.get("actor_id", "default-user")
        session_id = payload.get("session_id", "default-session")
        user_message = payload.get("prompt", "")

        log.info(
            f"actor_id={actor_id} session_id={session_id} user_message={user_message!r}"
        )

        save_event(log, memory_id, "USER", user_message, actor_id, session_id)

        memory_context = load_memory_context(
            log, memory_id, actor_id, session_id
        )
        final_prompt = registration.build_user_prompt(payload, memory_context)

        response = await strands_agent.invoke_async(final_prompt)
        log.info(f"RAW AGENT RESPONSE: {response}")

        normalized = normalize_agent_output(response)
        assistant_text = response_to_assistant_text(normalized)
        log.info(f"ASSISTANT TEXT: {assistant_text}")

        final_response = {
            "action": "FINAL_RESPONSE",
            "agent_id": agent_id,
            "message": assistant_text,
        }

        save_event(
            log,
            memory_id,
            "ASSISTANT",
            json.dumps(final_response, ensure_ascii=False),
            actor_id,
            session_id,
        )

        yield response_payload(final_response)

    except Exception as e:
        log.error(f"invoke error: {str(e)}")
        yield response_payload({"action": "ERROR", "message": str(e)})


if __name__ == "__main__":
    app.run()
