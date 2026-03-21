import json
from typing import List
from src.devices.base_device import DeviceState
from src.devices.smart_plug import SmartPlug
from src.config.settings import config


class DeviceRepository:
    """Repository Pattern — abstrae el acceso y persistencia de dispositivos."""

    def __init__(self, path: str = None):
        self._path = path or config.device.data_path

    def get_all(self) -> List[SmartPlug]:
        data = self._load()
        return [
            SmartPlug(DeviceState(**d))
            for d in data["devices"]
        ]

    def get_cold_chain_devices(self) -> List[SmartPlug]:
        return [d for d in self.get_all() if d.is_cold_chain]

    def save(self, devices: List[SmartPlug]) -> None:
        data = {"devices": [d.to_dict() for d in devices]}
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load(self) -> dict:
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)
