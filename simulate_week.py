"""
simulate_week.py
----------------
Simula 7 días del pipeline usando el pronóstico REAL de Open-Meteo.
Aplica la estrategia de horarios del negocio (BusinessHoursStrategy).
No envía notificaciones ni modifica el estado de los dispositivos.
Persiste los resultados en logs/savings_history.json.

Uso:
    python simulate_week.py
"""

import httpx

from src.config.settings import config
from src.repositories.weather_repository import WeatherForecast
from src.repositories.device_repository import DeviceRepository
from src.repositories.savings_repository import SavingsRepository
from src.strategies.business_hours_strategy import BusinessHoursStrategy
from src.dashboard.metrics import DEVICE_KW, DEFAULT_KW


def fetch_week_forecasts() -> list[WeatherForecast]:
    """Trae 7 días de pronóstico desde Open-Meteo (hoy + 6 días)."""
    params = {
        "latitude":  config.weather.latitude,
        "longitude": config.weather.longitude,
        "daily":     ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone":  config.weather.timezone,
        "forecast_days": 7,
    }
    response = httpx.get(config.weather.base_url, params=params, timeout=10)
    response.raise_for_status()
    data  = response.json()
    daily = data["daily"]

    forecasts = []
    for i in range(7):
        max_temp      = daily["temperature_2m_max"][i]
        min_temp      = daily["temperature_2m_min"][i]
        precipitation = daily["precipitation_sum"][i]
        date_str      = daily["time"][i]

        desc = f"día {'caluroso' if max_temp >= config.high_temp_threshold else 'normal'} ({max_temp}°C)"
        if precipitation > 0:
            desc += f", lluvia esperada ({precipitation}mm)"

        forecasts.append(WeatherForecast(
            date=date_str,
            max_temp=max_temp,
            min_temp=min_temp,
            precipitation=precipitation,
            description=desc,
        ))
    return forecasts


def calc_savings(devices, strategy: BusinessHoursStrategy, forecast: WeatherForecast) -> tuple[float, float]:
    """
    Calcula kWh ahorrados para un día dado.
    Considera el apagado nocturno + siesta del domingo (si aplica).
    Usa la hora de apertura real (no la fórmula genérica de 8am).
    """
    shutdown_hour = strategy.decide_shutdown_hour(forecast)
    weekday       = strategy._weekday(forecast)
    opening       = strategy.OPENING_HOURS[weekday]
    stab          = strategy.STABILIZATION_H

    # Horas apagado nocturno = desde shutdown hasta que se reconecta (opening - stab)
    nightly_off_hours = (opening - stab) - shutdown_hour

    # Horas apagado siesta (solo domingo)
    siesta_off_hours = 0.0
    siesta = strategy.decide_siesta(forecast)
    if siesta:
        siesta_shutdown, siesta_on = siesta
        siesta_off_hours = siesta_on - siesta_shutdown

    total_kwh = 0.0
    for d in devices:
        if not d.is_cold_chain:
            continue
        kw = DEVICE_KW.get(d.name, DEFAULT_KW)
        total_kwh += kw * (nightly_off_hours + siesta_off_hours)

    return round(total_kwh, 3), round(total_kwh * 120.0, 2)


def main():
    strategy     = BusinessHoursStrategy()
    devices      = DeviceRepository().get_all()
    savings_repo = SavingsRepository()

    print("\n🦞 OpenClaw IoT — Simulación semanal con horarios del negocio\n")
    forecasts = fetch_week_forecasts()

    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    print(f"  {'Fecha':<12} {'Día':<11} {'Máx':<7} {'Lluvia':<9} {'Apagado':<9} {'Siesta':<14} {'kWh':<8} {'ARS'}")
    print("  " + "─" * 78)

    for forecast in forecasts:
        weekday       = strategy._weekday(forecast)
        shutdown_hour = strategy.decide_shutdown_hour(forecast)
        kwh, ars      = calc_savings(devices, strategy, forecast)
        rain          = f"{forecast.precipitation}mm" if forecast.precipitation > 0 else "—"
        flag          = " 🌡️" if forecast.max_temp >= config.high_temp_threshold else ""

        siesta = strategy.decide_siesta(forecast)
        siesta_str = (
            f"{strategy._fmt(siesta[0])}→{strategy._fmt(siesta[1])}"
            if siesta else "—"
        )

        print(
            f"  {forecast.date:<12} {day_names[weekday]:<11} {forecast.max_temp:<7.1f} "
            f"{rain:<9} {shutdown_hour:02d}:00{'':<4} {siesta_str:<14} {kwh:<8.3f} ${ars:,.2f}{flag}"
        )

        savings_repo.save_run(
            date=forecast.date,
            max_temp=forecast.max_temp,
            shutdown_hour=shutdown_hour,
            kwh=kwh,
            ars=ars,
        )

    print("  " + "─" * 78)
    total_kwh = savings_repo.get_total_kwh()
    total_ars = savings_repo.get_total_ars()
    print(f"\n  ✅ Total acumulado: {total_kwh:.3f} kWh / ${total_ars:,.2f} ARS\n")


if __name__ == "__main__":
    main()
