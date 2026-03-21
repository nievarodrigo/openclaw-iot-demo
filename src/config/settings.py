from dataclasses import dataclass, field
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class WeatherConfig:
    latitude: float = -34.6037  # Buenos Aires por defecto
    longitude: float = -58.3816
    timezone: str = "America/Argentina/Buenos_Aires"
    base_url: str = "https://api.open-meteo.com/v1/forecast"


@dataclass
class DeviceConfig:
    data_path: str = "data/devices.json"


@dataclass
class NotificationConfig:
    whatsapp_number: Optional[str] = field(
        default_factory=lambda: os.getenv("WHATSAPP_NUMBER")
    )


@dataclass
class AppConfig:
    weather: WeatherConfig = field(default_factory=WeatherConfig)
    device: DeviceConfig = field(default_factory=DeviceConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    high_temp_threshold: float = 28.0   # °C — por encima se considera "caluroso"
    shutdown_hour_hot: int = 4          # día caluroso → apagar más tarde (ambiente calienta más rápido)
    shutdown_hour_normal: int = 2       # día normal → apagar más temprano (ambiente ayuda a mantener frío)


# Singleton de configuración
config = AppConfig()
