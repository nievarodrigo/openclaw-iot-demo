import json
import pytest
from pathlib import Path
from src.repositories.device_repository import DeviceRepository
from src.devices.smart_plug import SmartPlug


MOCK_DEVICES = {
    "devices": [
        {
            "id": "plug_001",
            "name": "Heladera Principal",
            "location": "Depósito",
            "status": "on",
            "cold_chain": True,
            "scheduled_off": None,
            "last_action": None,
        },
        {
            "id": "plug_002",
            "name": "Freezer Exhibidor",
            "location": "Local",
            "status": "on",
            "cold_chain": True,
            "scheduled_off": None,
            "last_action": None,
        },
        {
            "id": "plug_003",
            "name": "Aire Acondicionado",
            "location": "Local",
            "status": "off",
            "cold_chain": False,
            "scheduled_off": None,
            "last_action": None,
        },
    ]
}


@pytest.fixture
def devices_file(tmp_path):
    path = tmp_path / "devices.json"
    path.write_text(json.dumps(MOCK_DEVICES), encoding="utf-8")
    return path


@pytest.fixture
def repo(devices_file):
    return DeviceRepository(path=str(devices_file))


class TestDeviceRepository:

    def test_get_all_returns_all_devices(self, repo):
        devices = repo.get_all()
        assert len(devices) == 3

    def test_get_all_returns_smart_plugs(self, repo):
        devices = repo.get_all()
        assert all(isinstance(d, SmartPlug) for d in devices)

    def test_get_cold_chain_devices_filters_correctly(self, repo):
        cold_chain = repo.get_cold_chain_devices()
        assert len(cold_chain) == 2
        assert all(d.is_cold_chain for d in cold_chain)

    def test_save_persists_device_state(self, repo, devices_file):
        devices = repo.get_all()
        devices[0].schedule_off(3)
        repo.save(devices)

        saved = json.loads(devices_file.read_text())
        assert saved["devices"][0]["scheduled_off"] == "03:00"

    def test_device_names_are_correct(self, repo):
        devices = repo.get_all()
        names = [d.name for d in devices]
        assert "Heladera Principal" in names
        assert "Freezer Exhibidor" in names
        assert "Aire Acondicionado" in names
