import httpx
from dataclasses import dataclass
from src.config.settings import config


@dataclass
class WeatherForecast:
    date: str
    max_temp: float
    min_temp: float
    precipitation: float
    description: str


class WeatherRepository:
    """Repository Pattern — abstrae el acceso a la API de Open-Meteo."""

    def get_tomorrow_forecast(self) -> WeatherForecast:
        params = {
            "latitude": config.weather.latitude,
            "longitude": config.weather.longitude,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": config.weather.timezone,
            "forecast_days": 2,
        }

        response = httpx.get(config.weather.base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # índice 1 = mañana (índice 0 = hoy)
        daily = data["daily"]
        max_temp = daily["temperature_2m_max"][1]
        min_temp = daily["temperature_2m_min"][1]
        precipitation = daily["precipitation_sum"][1]
        date = daily["time"][1]

        description = self._describe(max_temp, precipitation)

        return WeatherForecast(
            date=date,
            max_temp=max_temp,
            min_temp=min_temp,
            precipitation=precipitation,
            description=description,
        )

    def _describe(self, max_temp: float, precipitation: float) -> str:
        parts = []
        if max_temp >= config.high_temp_threshold:
            parts.append(f"día caluroso ({max_temp}°C)")
        else:
            parts.append(f"temperatura normal ({max_temp}°C)")
        if precipitation > 0:
            parts.append(f"lluvia esperada ({precipitation}mm)")
        return ", ".join(parts)
