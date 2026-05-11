from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WhatsButton:
    text: str
    id: str | None = None


@dataclass(frozen=True)
class WhatsTemplate:
    id: str
    payload: str
    buttons: list[WhatsButton]


def _btn(text: str, id: str | None = None) -> WhatsButton:
    return WhatsButton(text=text, id=id)


TEMPLATES: dict[str, WhatsTemplate] = {
    "vehicle_debts.ask_plate": WhatsTemplate(
        id="vehicle_debts.ask_plate",
        payload="Para consultar seu veículo, por favor informe a placa no formato ABD1D34.",
        buttons=[_btn("Voltar ao menu principal", "menu")],
    ),
    "vehicle_debts.invalid_plate": WhatsTemplate(
        id="vehicle_debts.invalid_plate",
        payload=(
            "Placa incompleta ou inválida: no Brasil a placa tem 7 caracteres "
            "(Mercosul, ex. ABC1D23, ou antiga, ex. ABC1234)."
        ),
        buttons=[_btn("Voltar ao menu principal", "menu")],
    ),
}


def render_template(template_id: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Renderiza template para formato "WhatsApp-like":

    {
      "payload": "...",
      "buttons": [{"text": "...", "id": "..."}, ...]
    }
    """
    data = data or {}
    tpl = TEMPLATES.get(template_id)
    if tpl is None:
        return {
            "payload": f"Template não encontrado: {template_id}",
            "buttons": [{"text": "Voltar ao menu principal", "id": "menu"}],
        }

    # Permite interpolação simples via {chave} no payload (opcional).
    try:
        payload = tpl.payload.format(**data)
    except Exception:
        payload = tpl.payload

    return {
        "payload": payload,
        "buttons": [
            {"text": b.text, "id": b.id} if b.id else {"text": b.text}
            for b in tpl.buttons
        ],
    }

