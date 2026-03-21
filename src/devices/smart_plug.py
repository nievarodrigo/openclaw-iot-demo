from datetime import datetime
from src.devices.base_device import BaseDevice, DeviceState


class SmartPlug(BaseDevice):
    """Simulación de un enchufe inteligente."""

    def turn_on(self) -> None:
        self._state.status = "on"
        self._state.last_action = f"ON @ {datetime.now().isoformat()}"
        print(f"[{self.name}] Encendido ✅")

    def turn_off(self) -> None:
        self._state.status = "off"
        self._state.scheduled_off = None
        self._state.last_action = f"OFF @ {datetime.now().isoformat()}"
        print(f"[{self.name}] Apagado 🔴")

    def schedule_off(self, hour: int) -> None:
        self._state.scheduled_off = f"{hour:02d}:00"
        self._state.last_action = f"SCHEDULED OFF @ {hour:02d}:00 — {datetime.now().isoformat()}"
        print(f"[{self.name}] Apagado programado para las {hour:02d}:00 ⏰")
