from src.agents.base_agent import BaseAgent
from src.agents.weather_agent import WeatherAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.notification_agent import NotificationAgent
from src.repositories.weather_repository import WeatherForecast


class AgentFactory:
    """Factory Pattern — centraliza la creación de agentes."""

    @staticmethod
    def create_weather_agent() -> WeatherAgent:
        return WeatherAgent()

    @staticmethod
    def create_decision_agent(forecast: WeatherForecast) -> DecisionAgent:
        return DecisionAgent(forecast=forecast)

    @staticmethod
    def create_notification_agent(forecast: WeatherForecast, actions: list) -> NotificationAgent:
        return NotificationAgent(forecast=forecast, actions=actions)
