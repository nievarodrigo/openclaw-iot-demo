import json
from datetime import datetime
from pathlib import Path


HISTORY_PATH = Path("logs/savings_history.json")


class SavingsRepository:
    """Persiste el historial de ahorros de cada corrida del pipeline."""

    def __init__(self, path: Path = None):
        self._path = path or HISTORY_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def save_run(self, date: str, max_temp: float, shutdown_hour: int, kwh: float, ars: float) -> None:
        history = self._load()
        history.append({
            "timestamp": datetime.now().isoformat(),
            "date": date,
            "max_temp": max_temp,
            "shutdown_hour": shutdown_hour,
            "kwh_saved": kwh,
            "ars_saved": ars,
        })
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def get_all(self) -> list[dict]:
        return self._load()

    def get_total_kwh(self) -> float:
        return round(sum(r["kwh_saved"] for r in self._load()), 3)

    def get_total_ars(self) -> float:
        return round(sum(r["ars_saved"] for r in self._load()), 2)

    def _load(self) -> list[dict]:
        if not self._path.exists():
            return []
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)
