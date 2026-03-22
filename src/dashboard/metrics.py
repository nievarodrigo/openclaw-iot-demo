from src.devices.base_device import DeviceState


# KW estimados por tipo de dispositivo (consumo comercial real)
DEVICE_KW = {
    # Heladeras verticales (lácteos, fiambres, bebidas)
    "Heladera Lácteos":    0.15,
    "Heladera Fiambres":   0.15,
    "Heladera Bebidas 1":  0.15,
    "Heladera Bebidas 2":  0.15,
    # Exhibidoras horizontales
    "Exhibidora Carnes":   0.20,
    "Exhibidora Quesos":   0.20,
    # Freezers
    "Freezer Helados":     0.25,
    "Freezer Congelados":  0.25,
    # Legacy
    "Heladera Principal":  0.15,
    "Freezer Exhibidor":   0.20,
    "Aire Acondicionado":  1.50,
}

DEFAULT_KW = 0.15


def estimate_savings(devices: list[dict]) -> float:
    """
    Calcula KW ahorrados estimados para los dispositivos con apagado programado.
    Asume que sin el sistema estarían encendidos hasta las 8am.
    """
    total = 0.0
    for d in devices:
        if not d.get("scheduled_off"):
            continue
        shutdown_hour = int(d["scheduled_off"].split(":")[0])
        # Horas ahorradas = desde apagado hasta las 8am
        hours_saved = max(0, 8 - shutdown_hour)
        kw = DEVICE_KW.get(d["name"], DEFAULT_KW)
        total += kw * hours_saved
    return round(total, 3)


def estimate_cost_savings(kwh: float, price_per_kwh: float = 120.0) -> float:
    """Costo ahorrado en pesos argentinos."""
    return round(kwh * price_per_kwh, 2)
