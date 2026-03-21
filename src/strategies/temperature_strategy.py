from src.strategies.base_strategy import BaseStrategy
from src.devices.base_device import BaseDevice
from src.repositories.weather_repository import WeatherForecast
from src.config.settings import config


class TemperatureStrategy(BaseStrategy):
    """
    Estrategia basada en temperatura:
    - Día caluroso (>= umbral): apagar más temprano para no romper cadena de frío
    - Día normal: apagar más tarde
    Solo aplica a dispositivos de cadena de frío.
    """

    def decide_shutdown_hour(self, forecast: WeatherForecast) -> int:
        if forecast.max_temp >= config.high_temp_threshold:
            return config.shutdown_hour_hot
        return config.shutdown_hour_normal

    def should_apply(self, device: BaseDevice) -> bool:
        return device.is_cold_chain

    def describe(self, forecast: WeatherForecast) -> str:
        hour = self.decide_shutdown_hour(forecast)
        if forecast.max_temp >= config.high_temp_threshold:
            return (
                f"Mañana se esperan {forecast.max_temp}°C — día caluroso. "
                f"Apago los dispositivos de cadena de frío a las {hour:02d}:00 "
                f"para proteger la temperatura antes del calor del día."
            )
        return (
            f"Mañana se esperan {forecast.max_temp}°C — temperatura normal. "
            f"Apago los dispositivos de cadena de frío a las {hour:02d}:00."
        )
