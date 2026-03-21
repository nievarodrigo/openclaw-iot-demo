from typing import List
from src.agents.base_agent import BaseAgent
from src.notifications.base_notifier import BaseNotifier
from src.notifications.whatsapp_notifier import WhatsAppNotifier, ConsoleNotifier
from src.repositories.weather_repository import WeatherForecast


class NotificationAgent(BaseAgent):
    """Agente responsable de notificar los resultados al usuario."""

    def __init__(
        self,
        forecast: WeatherForecast,
        actions: list,
        notifiers: List[BaseNotifier] = None,
    ):
        self._forecast = forecast
        self._actions = actions
        self._notifiers = notifiers or [WhatsAppNotifier(), ConsoleNotifier()]

    @property
    def name(self) -> str:
        return "NotificationAgent"

    def run(self) -> dict:
        message = self._build_message()
        print(f"[{self.name}] Enviando notificaciones...")
        for notifier in self._notifiers:
            notifier.notify(message)
        return {"message_sent": message}

    def _build_message(self) -> str:
        lines = [
            "🦞 *OpenClaw IoT — Reporte Nocturno*",
            f"📅 Pronóstico para mañana: {self._forecast.description}",
            "",
            "⚡ *Acciones programadas:*",
        ]
        for action in self._actions:
            lines.append(f"• {action['device']}: {action['action']}")

        if not self._actions:
            lines.append("• Sin cambios — todo normal.")

        lines += [
            "",
            "🌡️ Cadena de frío protegida ✅",
        ]
        return "\n".join(lines)
