import subprocess
from src.notifications.base_notifier import BaseNotifier
from src.config.settings import config


class WhatsAppNotifier(BaseNotifier):
    """Envía notificaciones via wacli (skill de OpenClaw)."""

    def __init__(self, number: str = None):
        self._number = number or config.notification.whatsapp_number

    def notify(self, message: str) -> None:
        if not self._number:
            print(f"[WhatsApp] Número no configurado. Mensaje: {message}")
            return

        try:
            result = subprocess.run(
                ["wacli", "send", "--to", self._number, "--message", message],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0:
                print(f"[WhatsApp] Mensaje enviado a {self._number} ✅")
            else:
                print(f"[WhatsApp] Error al enviar: {result.stderr}")
        except FileNotFoundError:
            # wacli no instalado — modo simulación
            print(f"[WhatsApp SIMULADO] → {self._number}: {message}")
        except subprocess.TimeoutExpired:
            print("[WhatsApp] Timeout al enviar mensaje")


class ConsoleNotifier(BaseNotifier):
    """Notificador de consola — útil para desarrollo y testing."""

    def notify(self, message: str) -> None:
        print(f"\n{'='*50}")
        print(f"📱 NOTIFICACIÓN")
        print(f"{'='*50}")
        print(message)
        print(f"{'='*50}\n")
