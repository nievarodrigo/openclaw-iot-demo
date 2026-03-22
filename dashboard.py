"""
OpenClaw IoT Demo — Dashboard
Ejecutar con: streamlit run dashboard.py
"""

import json
import time
from datetime import datetime
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.dashboard.metrics import estimate_savings, estimate_cost_savings
from src.repositories.savings_repository import SavingsRepository
from src.repositories.weather_repository import WeatherRepository

st.set_page_config(
    page_title="OpenClaw IoT",
    page_icon="🦞",
    layout="wide",
)

# ── CSS minimalista ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 0; }
    h1 { font-size: 1.4rem !important; margin-bottom: 0 !important; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    hr { margin: 0.5rem 0 !important; }
    .device-row { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

DEVICES_PATH = Path("data/devices.json")


def load_devices() -> list[dict]:
    with open(DEVICES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["devices"]


@st.cache_data(ttl=300)
def load_forecast():
    try:
        return WeatherRepository().get_tomorrow_forecast()
    except Exception:
        return None


# ── Datos ─────────────────────────────────────────────────────────────────────
devices   = load_devices()
forecast  = load_forecast()
active    = sum(1 for d in devices if d["status"] == "on")
scheduled = sum(1 for d in devices if d.get("scheduled_off"))

savings_repo  = SavingsRepository()
total_kwh     = savings_repo.get_total_kwh()
total_ars     = savings_repo.get_total_ars()

# ── Header ────────────────────────────────────────────────────────────────────
left, right = st.columns([6, 2])
left.markdown("## 🦞 OpenClaw IoT Dashboard")
right.caption(f"🔄 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.divider()

# ── KPIs + Clima en una sola fila ─────────────────────────────────────────────
k1, k2, k3, k4, sep, w1, w2, w3 = st.columns([2, 2, 2, 2, 0.3, 2, 2, 2])

k1.metric("⚡ Activos",        f"{active}/{len(devices)}")
k2.metric("⏰ Programados",    scheduled)
k3.metric("💡 KWh acumulados", f"{total_kwh}")
k4.metric("💰 ARS acumulados", f"${total_ars:,.0f}")

sep.markdown("<div style='border-left:1px solid #ddd;height:60px;margin:auto'></div>", unsafe_allow_html=True)

if forecast:
    w1.metric("🌡️ Máx. mañana", f"{forecast.max_temp}°C")
    w2.metric("🌡️ Mín. mañana", f"{forecast.min_temp}°C")
    w3.metric("🌧️ Lluvia",       f"{forecast.precipitation}mm")
else:
    w1.warning("Sin pronóstico")

st.divider()

# ── Dispositivos ──────────────────────────────────────────────────────────────
st.markdown("**🔌 Dispositivos**")

header = st.columns([3, 2, 2, 4])
for col, label in zip(header, ["Nombre", "Estado", "Apagado", "Última acción"]):
    col.caption(label)

for device in devices:
    row = st.columns([3, 2, 2, 4])
    status_icon = "🟢" if device["status"] == "on" else "🔴"
    cold = " ❄️" if device["cold_chain"] else ""
    row[0].markdown(f"{status_icon} **{device['name']}**{cold}")
    row[1].markdown(f"`{device['status'].upper()}`")
    row[2].markdown(f"`{device['scheduled_off']}`" if device.get("scheduled_off") else "—")
    row[3].caption(device.get("last_action") or "—")

st.divider()

# ── Historial de ahorros ──────────────────────────────────────────────────────
savings_data = savings_repo.get_all()

if savings_data:
    st.markdown("**📈 Historial de Ahorros**")

    df = pd.DataFrame(savings_data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").drop_duplicates(subset="date", keep="last")
    df["fecha"] = df["date"].dt.strftime("%d/%m")

    total_kwh = round(df["kwh_saved"].sum(), 3)
    total_ars = round(df["ars_saved"].sum(), 2)

    c1, c2 = st.columns(2)

    chart_kwh = (
        alt.Chart(df)
        .mark_bar(color="#4CAF50", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("fecha:N", sort=None, title="Fecha", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("kwh_saved:Q", title="kWh ahorrados"),
            tooltip=[
                alt.Tooltip("fecha:N", title="Fecha"),
                alt.Tooltip("kwh_saved:Q", title="kWh", format=".3f"),
                alt.Tooltip("max_temp:Q", title="Temp. máx (°C)"),
                alt.Tooltip("shutdown_hour:Q", title="Hora apagado"),
            ],
        )
        .properties(height=220, title="💡 kWh ahorrados por día")
    )
    c1.altair_chart(chart_kwh, use_container_width=True)
    c1.caption(f"Total: **{total_kwh} kWh**")

    chart_ars = (
        alt.Chart(df)
        .mark_bar(color="#2196F3", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("fecha:N", sort=None, title="Fecha", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("ars_saved:Q", title="$ ARS ahorrados"),
            tooltip=[
                alt.Tooltip("fecha:N", title="Fecha"),
                alt.Tooltip("ars_saved:Q", title="ARS", format=",.2f"),
                alt.Tooltip("max_temp:Q", title="Temp. máx (°C)"),
                alt.Tooltip("shutdown_hour:Q", title="Hora apagado"),
            ],
        )
        .properties(height=220, title="💰 ARS ahorrados por día")
    )
    c2.altair_chart(chart_ars, use_container_width=True)
    c2.caption(f"Total: **${total_ars:,.2f} ARS**")

    st.divider()

st.caption(f"{'🌤️ ' + forecast.description.capitalize() if forecast else ''} · Actualización automática cada 30s")

# ── Auto-refresh ──────────────────────────────────────────────────────────────
with st.empty():
    time.sleep(30)
    st.rerun()
