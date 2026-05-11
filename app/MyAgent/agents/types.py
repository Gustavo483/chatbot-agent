from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class AgentRegistration:
    """Metadados e comportamento de um agente Strands endereçável por id."""

    id: str
    system_prompt: str
    tools: list[Any]
    memory_id: str | None
    build_user_prompt: Callable[[dict, str], str]
