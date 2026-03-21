# 🦞 OpenClaw IoT Demo

Sistema multi-agente para control inteligente de dispositivos IoT basado en pronóstico climático, construido con **MCP + OpenClaw + Claude**.

> Proyecto demo para LinkedIn — muestra la potencia de orquestar agentes de IA para automatizar decisiones reales.

---

## ¿Qué hace?

Cada noche el sistema:

1. **WeatherAgent** → consulta el pronóstico del día siguiente via [Open-Meteo](https://open-meteo.com/) (gratis, sin API key)
2. **DecisionAgent** → analiza los dispositivos y decide a qué hora apagarlos para proteger la cadena de frío
3. **NotificationAgent** → te manda un resumen por WhatsApp con las acciones tomadas

```
🦞 OpenClaw IoT — Reporte Nocturno
📅 Pronóstico para mañana: día caluroso (32°C)

⚡ Acciones programadas:
• Heladera Principal: Apagado programado a las 02:00
• Freezer Exhibidor: Apagado programado a las 02:00

🌡️ Cadena de frío protegida ✅
```

---

## Stack

| Componente | Tecnología |
|---|---|
| Orquestador de agentes | [OpenClaw](https://openclaw.ai) |
| Protocolo | MCP (Model Context Protocol) |
| LLM | Claude Sonnet 4.6 (Anthropic API) |
| Clima | Open-Meteo API |
| IoT | Enchufes inteligentes simulados (JSON) |
| Notificaciones | WhatsApp via wacli |
| Lenguaje | Python 3.10+ |

---

## Patrones de Diseño

- **Strategy** — reglas de decisión intercambiables (`TemperatureStrategy`, etc.)
- **Repository** — acceso a datos desacoplado (clima, dispositivos)
- **Observer** — notificadores pluggables (WhatsApp, consola, email...)
- **Factory** — creación centralizada de agentes

---

## Estructura del Proyecto

```
openclaw-iot-demo/
├── src/
│   ├── agents/          # WeatherAgent, DecisionAgent, NotificationAgent, Factory
│   ├── devices/         # BaseDevice, SmartPlug
│   ├── strategies/      # BaseStrategy, TemperatureStrategy
│   ├── repositories/    # WeatherRepository, DeviceRepository
│   ├── notifications/   # WhatsAppNotifier, ConsoleNotifier
│   └── config/          # Settings centralizados
├── data/
│   └── devices.json     # Estado de dispositivos (actualizado en cada run)
├── main.py              # Entry point
└── requirements.txt
```

---

## Instalación

```bash
# Clonar el repo
git clone https://github.com/nievarodrigo/openclaw-iot-demo.git
cd openclaw-iot-demo

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu número de WhatsApp
```

## Uso

```bash
python main.py
```

---

## Configuración

Editá `src/config/settings.py` para personalizar:

- **Ubicación** — latitud/longitud (por defecto: Buenos Aires)
- **Umbral de temperatura** — a partir de cuántos °C se considera "caluroso" (defecto: 28°C)
- **Hora de apagado** — en día caluroso (02:00) vs día normal (04:00)

Para agregar dispositivos, editá `data/devices.json`.

---

## Escalabilidad

El sistema está diseñado para crecer fácilmente:

- **Nueva estrategia**: crear una clase que extienda `BaseStrategy`
- **Nuevo notificador**: crear una clase que extienda `BaseNotifier`
- **Nuevo dispositivo**: crear una clase que extienda `BaseDevice`
- **Nuevo agente**: crear una clase que extienda `BaseAgent` y registrarlo en `AgentFactory`

---

## Autor

**Rodrigo Nieva** — [@nievarodrigo](https://github.com/nievarodrigo)

*Construido con OpenClaw + Claude + demasiado café ☕*
