import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from src.notifications.base_notifier import BaseNotifier


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "rodronieva1@gmail.com"
PASSWORD_FILE = Path.home() / ".openclaw" / "gmail-password.txt"


class EmailNotifier(BaseNotifier):
    """Envía notificaciones por mail via Gmail SMTP."""

    def __init__(self, to: str = None):
        self._to = to or SENDER_EMAIL  # por defecto se manda a sí mismo
        self._password = self._load_password()

    def notify(self, message: str) -> None:
        if not self._password:
            print("[Email] Contraseña no configurada.")
            return

        try:
            msg = self._build_message(message)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, self._password)
                server.sendmail(SENDER_EMAIL, self._to, msg.as_string())
            print(f"[Email] Reporte enviado a {self._to} ✅")
        except smtplib.SMTPAuthenticationError:
            print("[Email] Error de autenticación — verificar app password")
        except Exception as e:
            print(f"[Email] Error al enviar: {e}")

    def _build_message(self, body: str) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🦞 OpenClaw IoT — Reporte Nocturno"
        msg["From"] = SENDER_EMAIL
        msg["To"] = self._to

        # Versión texto plano
        text = body.replace("*", "").replace("🦞", "[OpenClaw]")
        msg.attach(MIMEText(text, "plain"))

        # Versión HTML
        html = self._to_html(body)
        msg.attach(MIMEText(html, "html"))

        return msg

    def _to_html(self, body: str) -> str:
        lines = body.split("\n")
        html_lines = []
        for line in lines:
            line = line.replace("*", "<b>", 1).replace("*", "</b>", 1)
            if line.startswith("•"):
                html_lines.append(f"<li>{line[1:].strip()}</li>")
            elif line.strip() == "":
                html_lines.append("<br>")
            else:
                html_lines.append(f"<p>{line}</p>")
        return f"""
        <html><body style="font-family:sans-serif;max-width:500px;margin:auto;padding:20px">
            {"".join(html_lines)}
            <hr>
            <small style="color:#888">Generado por OpenClaw IoT Demo</small>
        </body></html>
        """

    def _load_password(self) -> str:
        try:
            return PASSWORD_FILE.read_text().strip()
        except FileNotFoundError:
            print(f"[Email] Archivo de contraseña no encontrado: {PASSWORD_FILE}")
            return ""
