import pytest
from unittest.mock import patch, MagicMock
from src.repositories.weather_repository import WeatherRepository, WeatherForecast


MOCK_API_RESPONSE = {
    "daily": {
        "time": ["2026-03-21", "2026-03-22"],
        "temperature_2m_max": [25.0, 32.5],
        "temperature_2m_min": [15.0, 21.0],
        "precipitation_sum": [0.0, 5.2],
    }
}


@pytest.fixture
def repo():
    return WeatherRepository()


class TestWeatherRepository:

    @patch("src.repositories.weather_repository.httpx.get")
    def test_get_tomorrow_forecast_returns_forecast(self, mock_get, repo):
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_get.return_value = mock_response

        forecast = repo.get_tomorrow_forecast()

        assert isinstance(forecast, WeatherForecast)

    @patch("src.repositories.weather_repository.httpx.get")
    def test_get_tomorrow_returns_index_1(self, mock_get, repo):
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_get.return_value = mock_response

        forecast = repo.get_tomorrow_forecast()

        # Índice 1 = mañana
        assert forecast.max_temp == 32.5
        assert forecast.min_temp == 21.0
        assert forecast.precipitation == 5.2
        assert forecast.date == "2026-03-22"

    @patch("src.repositories.weather_repository.httpx.get")
    def test_hot_day_description(self, mock_get, repo):
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_get.return_value = mock_response

        forecast = repo.get_tomorrow_forecast()

        assert "caluroso" in forecast.description

    @patch("src.repositories.weather_repository.httpx.get")
    def test_description_includes_precipitation(self, mock_get, repo):
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_get.return_value = mock_response

        forecast = repo.get_tomorrow_forecast()

        assert "lluvia" in forecast.description
