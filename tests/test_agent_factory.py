import pytest
from src.agents.agent_factory import AgentFactory
from src.agents.weather_agent import WeatherAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.notification_agent import NotificationAgent
from src.repositories.weather_repository import WeatherForecast


@pytest.fixture
def forecast():
    return WeatherForecast(
        date="2026-03-22",
        max_temp=25.0,
        min_temp=15.0,
        precipitation=0.0,
        description="temperatura normal (25°C)",
    )


class TestAgentFactory:

    def test_create_weather_agent_returns_correct_type(self):
        agent = AgentFactory.create_weather_agent()
        assert isinstance(agent, WeatherAgent)

    def test_create_decision_agent_returns_correct_type(self, forecast):
        agent = AgentFactory.create_decision_agent(forecast)
        assert isinstance(agent, DecisionAgent)

    def test_create_notification_agent_returns_correct_type(self, forecast):
        agent = AgentFactory.create_notification_agent(forecast, actions=[])
        assert isinstance(agent, NotificationAgent)

    def test_weather_agent_has_correct_name(self):
        agent = AgentFactory.create_weather_agent()
        assert agent.name == "WeatherAgent"

    def test_decision_agent_has_correct_name(self, forecast):
        agent = AgentFactory.create_decision_agent(forecast)
        assert agent.name == "DecisionAgent"

    def test_notification_agent_has_correct_name(self, forecast):
        agent = AgentFactory.create_notification_agent(forecast, actions=[])
        assert agent.name == "NotificationAgent"
