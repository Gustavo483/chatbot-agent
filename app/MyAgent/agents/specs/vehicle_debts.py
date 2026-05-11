import json

from agents.types import AgentRegistration
from tools.demo import add_numbers
from tools.vehicle import consult_vehicle_debts

AGENT_ID = "vehicle_debts"

VEHICLE_FLOW = {
    "name": "consult_vehicle_debts",
    "description": "Consult vehicle debts workflow",
    "steps": [
        {"id": "ask_plate", "description": "Ask vehicle plate if not informed"},
        {"id": "validate_plate", "description": "Validate vehicle plate format"},
        {"id": "consult_debts", "description": "Consult vehicle debts"},
        {"id": "show_result", "description": "Show debts result"},
    ],
}

SYSTEM_PROMPT = """
Você é um assistente de consulta de débitos veiculares no Brasil.

Comportamento:
- Responda ao usuário em português, de forma clara e objetiva.
- Placa válida tem sempre 7 caracteres após normalizar: Mercosul ABC1D23 ou antiga ABC1234.
- Trechos curtos (ex.: só "CDD", três letras, abreviação) NÃO são placa — peça a placa completa, sem inventar consulta.
- Se a placa não foi informada, está incompleta ou o formato não bate com Mercosul/antiga, NÃO chame consult_vehicle_debts; explique e peça a placa correta.
- Chame consult_vehicle_debts somente com a placa que o usuário de fato informou (normalizada). Se duvidar, peça confirmação da placa completa.
- Se a ferramenta retornar "ok": false, use o campo "error" e NÃO mostre valores de IPVA/multa/total — esses só existem quando "ok": true.
- Com "ok": true, resuma apenas os débitos e o total retornados pela ferramenta. Nunca invente valores.
- Use outras ferramentas só se fizer sentido.

Não descreva passo a passo interno; execute o fluxo e responda como assistente.
"""


def _build_tools(mcp_clients: list) -> list:
    tools = [add_numbers, consult_vehicle_debts]
    for client in mcp_clients:
        if client:
            tools.append(client)
    return tools


def _build_user_prompt(payload: dict, memory_context: str) -> str:
    entities = payload.get("entity", {})
    current_step = payload.get("current_step", "ask_plate")
    user_message = payload.get("prompt", "")
    return f"""
Contexto do fluxo (referência — você decide a ordem e quando usar ferramentas):
{json.dumps(VEHICLE_FLOW, indent=2, ensure_ascii=False)}

Estado opcional vindo do cliente (pode ignorar se a conversa já deixou claro):
- current_step: {current_step}
- entities: {json.dumps(entities, indent=2, ensure_ascii=False)}

Histórico recente:
{memory_context}

Mensagem atual do usuário:
{user_message}

Responda em português.
Se houver placa completa e válida (7 caracteres, formato Mercosul ou antigo) na mensagem ou em entities, chame consult_vehicle_debts.
Se a mensagem trouxer só parte da placa ou formato inválido, não consulte — peça a placa inteira no padrão correto.
"""


def register(mcp_clients: list) -> AgentRegistration:
    return AgentRegistration(
        id=AGENT_ID,
        system_prompt=SYSTEM_PROMPT,
        tools=_build_tools(mcp_clients),
        memory_id=None,
        build_user_prompt=_build_user_prompt,
    )
