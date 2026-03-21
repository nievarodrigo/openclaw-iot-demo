from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Interfaz base para todos los agentes del sistema."""

    @abstractmethod
    def run(self) -> dict:
        """Ejecuta la tarea del agente y retorna un resultado."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
