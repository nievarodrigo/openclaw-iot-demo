from datetime import datetime

from src.strategies.base_strategy import BaseStrategy
from src.devices.base_device import BaseDevice
from src.repositories.weather_repository import WeatherForecast
from src.config.settings import config


class BusinessHoursStrategy(BaseStrategy):
    """
    Estrategia basada en temperatura + horarios del negocio.

    Calcula la hora óptima de apagado de la cadena de frío considerando:
    - Temperatura del día siguiente (tolerancia de cadena de frío)
    - Hora de apertura según el día de la semana
    - 20 minutos de estabilización antes de la apertura
    - Viernes: el local cierra a las 02:00 → no apagar antes
    - Domingo: siesta 15:30 → 20:00 con ventana de apagado intermedio

    Fórmula base:
        apagado = apertura − ESTABILIZACIÓN − max_horas_sin_frío
    """

    # Hora de apertura por día (0=lunes … 6=domingo)
    OPENING_HOURS: dict[int, float] = {
        0: 10.5,   # Lunes:     10:30
        1:  9.0,   # Martes:    09:00
        2:  9.0,   # Miércoles: 09:00
        3:  9.0,   # Jueves:    09:00
        4:  9.0,   # Viernes:   09:00
        5:  9.0,   # Sábado:    09:00
        6:  9.0,   # Domingo:   09:00 (mañana)
    }

    # Cierre nocturno tardío: indexado por el día que ABRE esa mañana.
    # Sábado → el viernes el local cierra a las 02:00.
    LATE_CLOSING: dict[int, float] = {
        5: 2.0,
    }

    # Siesta del domingo
    SUNDAY_SIESTA_CLOSE  = 15.5   # 15:30
    SUNDAY_SIESTA_REOPEN = 20.0   # 20:00

    # Tolerancia de cadena de frío según temperatura
    MAX_OFF_HOURS_HOT    = 4.0    # días ≥ umbral °C
    MAX_OFF_HOURS_NORMAL = 6.0    # días < umbral °C

    STABILIZATION_H = 20 / 60    # 20 min de estabilización antes de apertura

    # ── helpers ──────────────────────────────────────────────────────────────

    def _weekday(self, forecast: WeatherForecast) -> int:
        return datetime.strptime(forecast.date, "%Y-%m-%d").weekday()

    def _max_off(self, forecast: WeatherForecast) -> float:
        if forecast.max_temp >= config.high_temp_threshold:
            return self.MAX_OFF_HOURS_HOT
        return self.MAX_OFF_HOURS_NORMAL

    @staticmethod
    def _fmt(hour_float: float) -> str:
        h = int(hour_float)
        m = int(round((hour_float % 1) * 60))
        return f"{h:02d}:{m:02d}"

    # ── interfaz pública ─────────────────────────────────────────────────────

    def decide_shutdown_hour(self, forecast: WeatherForecast) -> int:
        """Hora de apagado nocturno (entero, para apertura del día indicado)."""
        weekday = self._weekday(forecast)
        max_off = self._max_off(forecast)
        opening = self.OPENING_HOURS[weekday]

        # Apagar cuando el frío todavía aguanta + dejar margen de estabilización
        shutdown = opening - self.STABILIZATION_H - max_off

        # Restricción: si el negocio cierra tarde, no apagar antes de ese cierre
        late_close = self.LATE_CLOSING.get(weekday)
        if late_close is not None:
            shutdown = max(shutdown, late_close)

        return round(shutdown)

    def decide_siesta(self, forecast: WeatherForecast) -> tuple[float, float] | None:
        """
        Ventana de apagado en la siesta del domingo.
        Retorna (hora_apagado, hora_reconexión) como floats, o None si no es domingo.
        """
        if self._weekday(forecast) != 6:
            return None

        max_off  = self._max_off(forecast)
        siesta_on = self.SUNDAY_SIESTA_REOPEN - self.STABILIZATION_H  # ~19:40

        # Apagar lo más tarde posible después del cierre de siesta,
        # garantizando que el frío aguante hasta la reapertura.
        siesta_shutdown = max(self.SUNDAY_SIESTA_CLOSE, siesta_on - max_off)

        return siesta_shutdown, siesta_on

    def should_apply(self, device: BaseDevice) -> bool:
        return device.is_cold_chain

    def describe(self, forecast: WeatherForecast) -> str:
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        weekday   = self._weekday(forecast)
        opening   = self.OPENING_HOURS[weekday]
        shutdown  = self.decide_shutdown_hour(forecast)
        max_off   = self._max_off(forecast)
        temp_label = "caluroso" if forecast.max_temp >= config.high_temp_threshold else "normal"

        lines = [
            f"{day_names[weekday]} — apertura {self._fmt(opening)}, "
            f"{forecast.max_temp}°C ({temp_label}).",
            f"Cadena de frío aguanta {int(max_off)}h → apago a las {shutdown:02d}:00 "
            f"para estar lista antes de las {self._fmt(opening)}.",
        ]

        if weekday == 5:
            lines.append("Viernes cierra a las 02:00 → apagado no antes de las 02:00.")

        siesta = self.decide_siesta(forecast)
        if siesta:
            off_h, on_h = siesta
            lines.append(
                f"Siesta: apago a las {self._fmt(off_h)}, reconecto a las {self._fmt(on_h)}."
            )

        return " ".join(lines)
