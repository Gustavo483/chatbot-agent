from mcp_client.client import get_streamable_http_mcp_client

from agents.specs import vehicle_debts
from agents.types import AgentRegistration

_REGISTRY: dict[str, AgentRegistration] | None = None


def _mcp_clients():
    return [get_streamable_http_mcp_client()]


def build_registry() -> dict[str, AgentRegistration]:
    """Registra todos os agentes. Adicione novos specs aqui."""
    mcp = _mcp_clients()
    registrations = [
        vehicle_debts.register(mcp),
    ]
    return {r.id: r for r in registrations}


def get_registry() -> dict[str, AgentRegistration]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = build_registry()
    return _REGISTRY


def get_registration(agent_id: str) -> AgentRegistration:
    reg = get_registry().get(agent_id)
    if reg is None:
        raise KeyError(f"Agente desconhecido: {agent_id!r}")
    return reg
