from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DeviceState:
    id: str
    name: str
    location: str
    status: str          # "on" | "off"
    cold_chain: bool
    scheduled_off: Optional[str]
    last_action: Optional[str]


class BaseDevice(ABC):
    def __init__(self, state: DeviceState):
        self._state = state

    @property
    def id(self) -> str:
        return self._state.id

    @property
    def name(self) -> str:
        return self._state.name

    @property
    def is_on(self) -> bool:
        return self._state.status == "on"

    @property
    def is_cold_chain(self) -> bool:
        return self._state.cold_chain

    @abstractmethod
    def turn_on(self) -> None:
        pass

    @abstractmethod
    def turn_off(self) -> None:
        pass

    @abstractmethod
    def schedule_off(self, hour: int) -> None:
        pass

    def to_dict(self) -> dict:
        return {
            "id": self._state.id,
            "name": self._state.name,
            "location": self._state.location,
            "status": self._state.status,
            "cold_chain": self._state.cold_chain,
            "scheduled_off": self._state.scheduled_off,
            "last_action": self._state.last_action,
        }
