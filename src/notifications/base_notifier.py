from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """Observer Pattern — interfaz para todos los notificadores."""

    @abstractmethod
    def notify(self, message: str) -> None:
        pass
