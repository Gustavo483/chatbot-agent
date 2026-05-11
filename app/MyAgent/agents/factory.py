from strands import Agent

from agents.types import AgentRegistration

_agents: dict[str, Agent] = {}


def get_or_create_strands_agent(registration: AgentRegistration, model) -> Agent:
    agent_id = registration.id
    if agent_id not in _agents:
        _agents[agent_id] = Agent(
            model=model,
            system_prompt=registration.system_prompt,
            tools=registration.tools,
        )
    return _agents[agent_id]
