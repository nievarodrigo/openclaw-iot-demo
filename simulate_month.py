"""
simulate_month.py
-----------------
Simula 30 días del pipeline usando temperaturas REALES históricas de Open-Meteo.
Aplica BusinessHoursStrategy con los horarios del negocio.
No envía notificaciones ni modifica el estado de los dispositivos.
Persiste los resultados en logs/savings_history.json.

Uso:
    python simulate_month.py
"""

import httpx
from datetime import date, timedelta

from src.config.settings import config
from src.repositories.weather_repository import WeatherForecast
from src.repositories.device_repository import DeviceRepository
from src.repositories.savings_repository import SavingsRepository
from src.strategies.business_hours_strategy import BusinessHoursStrategy
from src.dashboard.metrics import DEVICE_KW, DEFAULT_KW

HISTORICAL_API = "https://archive-api.open-meteo.com/v1/archive"


def fetch_historical_forecasts(days: int = 30) -> list[WeatherForecast]:
    """Trae los últimos N días de datos reales desde Open-Meteo Historical API."""
    end   = date.today() - timedelta(days=1)   # ayer (dato completo seguro)
    start = end - timedelta(days=days - 1)

    params = {
        "latitude":   config.weather.latitude,
        "longitude":  config.weather.longitude,
        "daily":      ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone":   config.weather.timezone,
        "start_date": start.isoformat(),
        "end_date":   end.isoformat(),
    }
    response = httpx.get(HISTORICAL_API, params=params, timeout=15)
    response.raise_for_status()
    data  = response.json()
    daily = data["daily"]

    forecasts = []
    for i in range(len(daily["time"])):
        max_temp      = daily["temperature_2m_max"][i]
        min_temp      = daily["temperature_2m_min"][i]
        precipitation = daily["precipitation_sum"][i] or 0.0
        date_str      = daily["time"][i]

        desc = f"día {'caluroso' if max_temp >= config.high_temp_threshold else 'normal'} ({max_temp}°C)"
        if precipitation > 0:
            desc += f", lluvia ({precipitation}mm)"

        forecasts.append(WeatherForecast(
            date=date_str,
            max_temp=max_temp,
            min_temp=min_temp,
            precipitation=precipitation,
            description=desc,
        ))
    return forecasts


def calc_savings(
    devices,
    strategy: BusinessHoursStrategy,
    forecast: WeatherForecast,
) -> tuple[float, float]:
    """
    Calcula kWh y ARS ahorrados para un día dado.
    Considera apagado nocturno + siesta del domingo.
    """
    shutdown_hour = strategy.decide_shutdown_hour(forecast)
    weekday       = strategy._weekday(forecast)
    opening       = strategy.OPENING_HOURS[weekday]
    stab          = strategy.STABILIZATION_H

    nightly_off_h = (opening - stab) - shutdown_hour

    siesta_off_h = 0.0
    siesta = strategy.decide_siesta(forecast)
    if siesta:
        siesta_shutdown, siesta_on = siesta
        siesta_off_h = siesta_on - siesta_shutdown

    total_kwh = 0.0
    for d in devices:
        if not d.is_cold_chain:
            continue
        kw = DEVICE_KW.get(d.name, DEFAULT_KW)
        total_kwh += kw * (nightly_off_h + siesta_off_h)

    return round(total_kwh, 3), round(total_kwh * 120.0, 2)


def main():
    strategy     = BusinessHoursStrategy()
    devices      = DeviceRepository().get_all()
    savings_repo = SavingsRepository()

    print("\n🦞 OpenClaw IoT — Simulación mensual (datos históricos reales)\n")
    forecasts = fetch_historical_forecasts(days=30)
    print(f"  Período: {forecasts[0].date} → {forecasts[-1].date}  ({len(forecasts)} días)\n")

    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    print(f"  {'Fecha':<12} {'Día':<5} {'Máx':<7} {'Lluvia':<9} {'Apagado':<9} {'Siesta':<14} {'kWh':<8} {'ARS'}")
    print("  " + "─" * 72)

    week_kwh = 0.0
    week_ars = 0.0

    for i, forecast in enumerate(forecasts):
        weekday       = strategy._weekday(forecast)
        shutdown_hour = strategy.decide_shutdown_hour(forecast)
        kwh, ars      = calc_savings(devices, strategy, forecast)
        rain          = f"{forecast.precipitation:.1f}mm" if forecast.precipitation > 0 else "—"
        flag          = " 🌡️" if forecast.max_temp >= config.high_temp_threshold else ""

        siesta = strategy.decide_siesta(forecast)
        siesta_str = (
            f"{strategy._fmt(siesta[0])}→{strategy._fmt(siesta[1])}"
            if siesta else "—"
        )

        print(
            f"  {forecast.date:<12} {day_names[weekday]:<5} {forecast.max_temp:<7.1f} "
            f"{rain:<9} {shutdown_hour:02d}:00{'':<4} {siesta_str:<14} {kwh:<8.3f} ${ars:,.2f}{flag}"
        )

        week_kwh += kwh
        week_ars += ars

        savings_repo.save_run(
            date=forecast.date,
            max_temp=forecast.max_temp,
            shutdown_hour=shutdown_hour,
            kwh=kwh,
            ars=ars,
        )

        # Subtotal semanal cada 7 días
        if (i + 1) % 7 == 0:
            print(f"  {'':>55} {'─'*8} {'─'*9}")
            print(f"  {'  Subtotal semana':<58} {week_kwh:<8.3f} ${week_ars:,.2f}")
            print()
            week_kwh = 0.0
            week_ars = 0.0

    print("  " + "═" * 72)
    total_kwh = savings_repo.get_total_kwh()
    total_ars = savings_repo.get_total_ars()
    print(f"\n  ✅ TOTAL 30 días: {total_kwh:.3f} kWh / ${total_ars:,.2f} ARS\n")


if __name__ == "__main__":
    main()
