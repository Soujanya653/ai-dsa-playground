from components.status_box import render_status
from components.kpis import render_kpis
from components.charts import render_charts
from utils.api_client import fetch_metrics, send_log
from utils.log_factory import build_log
import streamlit as st

from datetime import datetime, timezone
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import matplotlib.pyplot as plt

# ------------------ CONFIG ------------------
API_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 3

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI API Real-Time Monitor",
    page_icon="📊",
    layout="wide",
)

# ------------------ AUTO REFRESH (5 sec) ------------------
st_autorefresh(interval=5000, key="data_refresh")

# ------------------ SESSION STATE ------------------
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["Time", "Throughput", "ErrorRate"]
    )

if "auto_running" not in st.session_state:
    st.session_state.auto_running = False

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙ Log Generation Control")

mode = st.sidebar.radio(
    "Select Mode",
    ["Manual Log Entry", "Auto Generate Logs"]
)

# =========================================================
# MANUAL MODE
# =========================================================
if mode == "Manual Log Entry":

    st.session_state.auto_running = False  # Stop auto if manual selected

    st.sidebar.subheader("📝 Manual Parameters")

    latency_ms = st.sidebar.slider("Latency (ms)", 200, 5000, 800)
    tokens_used = st.sidebar.slider("Tokens Used", 0, 5000, 200)
    is_error = st.sidebar.toggle("Is Error?", value=False)

    if st.sidebar.button(" Generating Logs", use_container_width=True):

        log = build_log(
            latency_ms=latency_ms,  
            tokens_used=tokens_used,
            is_error=is_error
        )

        send_log(log,1.0)
        st.sidebar.success("Log sent to backend!")



else:

    st.sidebar.subheader("🤖 Auto Generation")

    auto_running = st.sidebar.toggle(
        "Start Auto Generation",
        value=st.session_state.auto_running
    )

    st.session_state.auto_running = auto_running

    # ==============================
    # WHEN AUTO IS RUNNING
    # ==============================
    if st.session_state.auto_running:

        for _ in range(5):
            log = build_log()

            send_log(log,0.3)
        st.sidebar.success("Auto generating logs...")

    # ==============================
    # WHEN AUTO IS STOPPED
    # ==============================
    else:

        st.sidebar.info("Auto generation stopped.")

        #  BUTTON ONLY VISIBLE WHEN AUTO IS OFF
        if st.sidebar.button(" Generate 50 Logs", use_container_width=True):

            success_count = 0

            for _ in range(50):

                log = build_log()
               
                if send_log(log,1.0):
                    success_count += 1

            st.sidebar.success(f"{success_count} logs generated!")


data = fetch_metrics(timeout=REQUEST_TIMEOUT)

if data is None:
    st.error("Backend unreachable. Start FastAPI server.")
    st.stop()




# =========================================================
# UPDATE HISTORY
# =========================================================
new_entry = {
    "Time": datetime.now().strftime("%H:%M:%S"),
    "Throughput": data.get("requests_per_min", 0),
    "ErrorRate": data.get("error_rate", 0.0) * 100,
}

st.session_state.history = pd.concat(
    [st.session_state.history, pd.DataFrame([new_entry])],
    ignore_index=True,
).tail(20)

# =========================================================
# MAIN DASHBOARD UI
# =========================================================
st.title("AI API Real-Time Monitor")


render_status(data)


# -------- KPI CARDS --------
render_kpis(data)
st.markdown("---")

# -------- PERFORMANCE TRENDS --------
st.subheader("Performance Trends")

render_charts(data, st.session_state.history)

# -------- INCIDENT LOG --------


st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")



