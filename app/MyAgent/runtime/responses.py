import json


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
