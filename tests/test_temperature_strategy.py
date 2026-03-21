import pytest
from src.strategies.temperature_strategy import TemperatureStrategy
from src.repositories.weather_repository import WeatherForecast
from src.devices.base_device import DeviceState
from src.devices.smart_plug import SmartPlug


@pytest.fixture
def strategy():
    return TemperatureStrategy()


@pytest.fixture
def hot_forecast():
    return WeatherForecast(
        date="2026-03-22",
        max_temp=32.0,
        min_temp=20.0,
        precipitation=0.0,
        description="día caluroso (32°C)",
    )


@pytest.fixture
def normal_forecast():
    return WeatherForecast(
        date="2026-03-22",
        max_temp=22.0,
        min_temp=14.0,
        precipitation=0.0,
        description="temperatura normal (22°C)",
    )


@pytest.fixture
def cold_chain_device():
    return SmartPlug(DeviceState(
        id="plug_001",
        name="Heladera Principal",
        location="Depósito",
        status="on",
        cold_chain=True,
        scheduled_off=None,
        last_action=None,
    ))


@pytest.fixture
def non_cold_chain_device():
    return SmartPlug(DeviceState(
        id="plug_003",
        name="Aire Acondicionado",
        location="Local",
        status="off",
        cold_chain=False,
        scheduled_off=None,
        last_action=None,
    ))


class TestTemperatureStrategy:

    def test_hot_day_returns_early_shutdown(self, strategy, hot_forecast):
        assert strategy.decide_shutdown_hour(hot_forecast) == 2

    def test_normal_day_returns_late_shutdown(self, strategy, normal_forecast):
        assert strategy.decide_shutdown_hour(normal_forecast) == 4

    def test_applies_to_cold_chain_device(self, strategy, cold_chain_device):
        assert strategy.should_apply(cold_chain_device) is True

    def test_does_not_apply_to_non_cold_chain(self, strategy, non_cold_chain_device):
        assert strategy.should_apply(non_cold_chain_device) is False

    def test_describe_hot_day_mentions_temperature(self, strategy, hot_forecast):
        description = strategy.describe(hot_forecast)
        assert "32" in description
        assert "02:00" in description

    def test_describe_normal_day_mentions_temperature(self, strategy, normal_forecast):
        description = strategy.describe(normal_forecast)
        assert "22" in description
        assert "04:00" in description
