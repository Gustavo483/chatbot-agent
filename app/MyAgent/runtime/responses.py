import json

from runtime.templates import render_template

def response_payload(data) -> str:
    return json.dumps(data)


def normalize_agent_output(response):
    """Extrai texto final do objeto de resposta do Strands/Bedrock."""
    out = response
    if hasattr(out, "output"):
        out = out.output
    elif hasattr(out, "message"):
        out = out.message
    if isinstance(out, dict) and "content" in out:
        content = out.get("content", [])
        if (
            isinstance(content, list)
            and content
            and isinstance(content[0], dict)
            and "text" in content[0]
        ):
            out = content[0]["text"]
    return out


def response_to_assistant_text(normalized) -> str:
    if isinstance(normalized, str):
        return normalized
    if normalized is None:
        return ""
    return json.dumps(normalized, ensure_ascii=False)


def _maybe_parse_json(text: str):
    t = (text or "").strip()
    if not t:
        return None
    if not (t.startswith("{") or t.startswith("[")):
        return None
    try:
        return json.loads(t)
    except Exception:
        return None


def normalize_to_whatsapp_message(assistant_text: str) -> dict:
    """
    Normaliza a saída para um formato mais "WhatsApp-like":

    {
      "payload": "texto",
      "buttons": [{"text": "...", "id": "..."}, ...]
    }

    O agente pode retornar:
    - Texto puro
    - JSON com { "template_id": "...", "data": {...} }
    - JSON com { "payload": "...", "buttons": [...] }
    - JSON com { "text": "..." }
    """
    parsed = _maybe_parse_json(assistant_text)

    if isinstance(parsed, dict):
        if "template_id" in parsed:
            template_id = str(parsed.get("template_id") or "")
            data = parsed.get("data") if isinstance(parsed.get("data"), dict) else {}
            return render_template(template_id, data)

        if "payload" in parsed:
            payload = str(parsed.get("payload") or "")
            buttons = parsed.get("buttons")
            if isinstance(buttons, list):
                # garante formato mínimo
                normalized_buttons = []
                for b in buttons:
                    if isinstance(b, dict) and "text" in b:
                        out = {"text": str(b.get("text") or "")}
                        if b.get("id"):
                            out["id"] = str(b.get("id"))
                        normalized_buttons.append(out)
                    elif isinstance(b, str):
                        normalized_buttons.append({"text": b})
                return {"payload": payload, "buttons": normalized_buttons}
            return {"payload": payload, "buttons": []}

        if "text" in parsed:
            return {"payload": str(parsed.get("text") or ""), "buttons": []}

    # fallback: texto puro (sem botões)
    return {"payload": (assistant_text or ""), "buttons": []}
