from typing import List
from src.agents.base_agent import BaseAgent
from src.repositories.device_repository import DeviceRepository
from src.repositories.weather_repository import WeatherForecast
from src.strategies.base_strategy import BaseStrategy
from src.strategies.temperature_strategy import TemperatureStrategy


class DecisionAgent(BaseAgent):
    """Agente responsable de tomar decisiones sobre los dispositivos."""

    def __init__(self, forecast: WeatherForecast, strategies: List[BaseStrategy] = None):
        self._forecast = forecast
        self._repo = DeviceRepository()
        self._strategies = strategies or [TemperatureStrategy()]

    @property
    def name(self) -> str:
        return "DecisionAgent"

    def run(self) -> dict:
        print(f"[{self.name}] Analizando dispositivos...")
        devices = self._repo.get_all()
        actions = []

        for device in devices:
            for strategy in self._strategies:
                if strategy.should_apply(device):
                    hour = strategy.decide_shutdown_hour(self._forecast)
                    device.schedule_off(hour)
                    actions.append({
                        "device": device.name,
                        "action": f"Apagado programado a las {hour:02d}:00",
                        "reason": strategy.describe(self._forecast),
                    })

        self._repo.save(devices)
        print(f"[{self.name}] {len(actions)} acción(es) programada(s).")
        return {"actions": actions}
