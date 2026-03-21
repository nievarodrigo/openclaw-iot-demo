from src.agents.base_agent import BaseAgent
from src.repositories.weather_repository import WeatherRepository, WeatherForecast


class WeatherAgent(BaseAgent):
    """Agente responsable de consultar el pronóstico del clima."""

    def __init__(self):
        self._repo = WeatherRepository()

    @property
    def name(self) -> str:
        return "WeatherAgent"

    def run(self) -> dict:
        print(f"[{self.name}] Consultando pronóstico para mañana...")
        forecast = self._repo.get_tomorrow_forecast()
        print(f"[{self.name}] {forecast.description}")
        return {"forecast": forecast}
