"""
OpenClaw IoT Demo
-----------------
Sistema multi-agente para control inteligente de dispositivos IoT
basado en pronóstico climático.

Flujo:
  1. WeatherAgent      → consulta el clima de mañana (Open-Meteo)
  2. DecisionAgent     → decide cuándo apagar los dispositivos
  3. NotificationAgent → notifica por mail + consola
  4. SavingsRepository → persiste el ahorro de la corrida en el historial
"""

from src.agents.agent_factory import AgentFactory
from src.dashboard.metrics import estimate_savings, estimate_cost_savings
from src.repositories.device_repository import DeviceRepository
from src.repositories.savings_repository import SavingsRepository
from src.strategies.business_hours_strategy import BusinessHoursStrategy


def main():
    print("\n🦞 OpenClaw IoT Demo — Iniciando...\n")

    # 1. Consultar clima
    weather_agent = AgentFactory.create_weather_agent()
    weather_result = weather_agent.run()
    forecast = weather_result["forecast"]

    # 2. Tomar decisiones
    decision_agent = AgentFactory.create_decision_agent(forecast)
    decision_result = decision_agent.run()
    actions = decision_result["actions"]

    # 3. Notificar
    notification_agent = AgentFactory.create_notification_agent(forecast, actions)
    notification_agent.run()

    # 4. Guardar historial de ahorros
    devices = DeviceRepository().get_all()
    kwh = estimate_savings([d.to_dict() for d in devices])
    ars = estimate_cost_savings(kwh)
    strategy = BusinessHoursStrategy()
    shutdown_hour = strategy.decide_shutdown_hour(forecast)

    SavingsRepository().save_run(
        date=forecast.date,
        max_temp=forecast.max_temp,
        shutdown_hour=shutdown_hour,
        kwh=kwh,
        ars=ars,
    )
    print(f"[Historial] Corrida guardada — {kwh} kWh / ${ars} ARS ahorrados.")

    print("\n✅ Pipeline completado.\n")


if __name__ == "__main__":
    main()
