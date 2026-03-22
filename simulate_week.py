"""
simulate_week.py
----------------
Simula 7 días del pipeline usando el pronóstico REAL de Open-Meteo.
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
from src.strategies.temperature_strategy import TemperatureStrategy
from src.dashboard.metrics import estimate_savings, estimate_cost_savings


def fetch_week_forecasts() -> list[WeatherForecast]:
    """Trae 7 días de pronóstico desde Open-Meteo (hoy + 6 días)."""
    params = {
        "latitude": config.weather.latitude,
        "longitude": config.weather.longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": config.weather.timezone,
        "forecast_days": 7,
    }
    response = httpx.get(config.weather.base_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    daily = data["daily"]

    forecasts = []
    for i in range(7):
        max_temp = daily["temperature_2m_max"][i]
        min_temp = daily["temperature_2m_min"][i]
        precipitation = daily["precipitation_sum"][i]
        date_str = daily["time"][i]

        if max_temp >= config.high_temp_threshold:
            desc = f"día caluroso ({max_temp}°C)"
        else:
            desc = f"temperatura normal ({max_temp}°C)"
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


def main():
    strategy = TemperatureStrategy()
    devices = DeviceRepository().get_all()
    savings_repo = SavingsRepository()

    print("\n🦞 OpenClaw IoT — Simulación semanal (pronóstico real)\n")
    forecasts = fetch_week_forecasts()

    print(f"  {'Fecha':<12} {'Máx':<7} {'Mín':<7} {'Lluvia':<9} {'Apagado':<10} {'kWh':<8} {'ARS'}")
    print("  " + "─" * 62)

    for forecast in forecasts:
        shutdown_hour = strategy.decide_shutdown_hour(forecast)

        # Aplicar el apagado simulado a los dispositivos de cadena de frío
        devices_sim = []
        for d in devices:
            d_dict = d.to_dict()
            if d.is_cold_chain:
                d_dict["scheduled_off"] = f"{shutdown_hour:02d}:00"
            devices_sim.append(d_dict)

        kwh = estimate_savings(devices_sim)
        ars = estimate_cost_savings(kwh)

        savings_repo.save_run(
            date=forecast.date,
            max_temp=forecast.max_temp,
            shutdown_hour=shutdown_hour,
            kwh=kwh,
            ars=ars,
        )

        flag = " 🌡️" if forecast.max_temp >= config.high_temp_threshold else ""
        rain = f"{forecast.precipitation}mm" if forecast.precipitation > 0 else "—"
        print(
            f"  {forecast.date:<12} {forecast.max_temp:<7.1f} {forecast.min_temp:<7.1f} "
            f"{rain:<9} {shutdown_hour:02d}:00{'':<5} {kwh:<8.3f} ${ars:,.2f}{flag}"
        )

    print("  " + "─" * 62)
    total_kwh = savings_repo.get_total_kwh()
    total_ars = savings_repo.get_total_ars()
    print(f"\n  ✅ Total acumulado: {total_kwh:.3f} kWh / ${total_ars:,.2f} ARS\n")


if __name__ == "__main__":
    main()
