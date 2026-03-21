"""
OpenClaw IoT Demo
-----------------
Sistema multi-agente para control inteligente de dispositivos IoT
basado en pronóstico climático.

Flujo:
  1. WeatherAgent   → consulta el clima de mañana (Open-Meteo)
  2. DecisionAgent  → decide cuándo apagar los dispositivos
  3. NotificationAgent → notifica por WhatsApp + consola
"""

from src.agents.agent_factory import AgentFactory


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

    print("\n✅ Pipeline completado.\n")


if __name__ == "__main__":
    main()
