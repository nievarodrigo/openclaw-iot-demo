from abc import ABC, abstractmethod
from typing import List
from src.devices.base_device import BaseDevice
from src.repositories.weather_repository import WeatherForecast


class BaseStrategy(ABC):
    """Strategy Pattern — define la interfaz para las reglas de decisión."""

    @abstractmethod
    def decide_shutdown_hour(self, forecast: WeatherForecast) -> int:
        """Retorna la hora (0-23) a la que se deben apagar los dispositivos."""
        pass

    @abstractmethod
    def should_apply(self, device: BaseDevice) -> bool:
        """Determina si esta estrategia aplica al dispositivo dado."""
        pass

    @abstractmethod
    def describe(self, forecast: WeatherForecast) -> str:
        """Explicación legible de la decisión tomada."""
        pass
