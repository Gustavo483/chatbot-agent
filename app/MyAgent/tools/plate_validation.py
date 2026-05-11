import re


def normalize_plate(raw: str) -> str:
    """Maiúsculas e só letras/números (sem hífen/espaço)."""
    return re.sub(r"[^A-Z0-9]", "", (raw or "").upper())


def validate_brazilian_plate(normalized: str) -> tuple[bool, str]:
    """
    Mercosul veículo: LLLNLNN (ex.: ABC1D23).
    Antiga: LLLNNNN (ex.: ABC1234).
    """
    if len(normalized) != 7:
        return (
            False,
            "Placa incompleta ou inválida: no Brasil a placa tem 7 caracteres "
            "(Mercosul, ex. ABC1D23, ou antiga, ex. ABC1234).",
        )
    if re.fullmatch(r"[A-Z]{3}\d{4}", normalized):
        return True, ""
    if re.fullmatch(r"[A-Z]{3}\d[A-Z]\d{2}", normalized):
        return True, ""
    return (
        False,
        "Formato de placa não reconhecido. Use Mercosul (3 letras, 1 número, "
        "1 letra, 2 números) ou formato antigo (3 letras e 4 números).",
    )
