from strands import tool

from tools.plate_validation import normalize_plate, validate_brazilian_plate


@tool
def consult_vehicle_debts(plate: str):
    """
    Consulta débitos do veículo (IPVA, licenciamento, multas, total) pela placa.

    Só retorna débitos se a placa for válida após normalização.
    Retorno com "ok": false indica placa inválida — não invente valores nesse caso.

    Mercosul: ABC1D23. Antiga: ABC1234. Exatamente 7 caracteres após limpar hífen/espaço.
    """
    normalized = normalize_plate(plate)
    ok, error_message = validate_brazilian_plate(normalized)
    if not ok:
        return {
            "ok": False,
            "error": error_message,
            "plate_received": normalized,
        }

    return {
        "ok": True,
        "plate": normalized,
        "debts": [
            {"type": "IPVA", "value": 1200},
            {"type": "Licenciamento", "value": 180},
            {"type": "Multa", "value": 250},
        ],
        "total": 1630,
    }
