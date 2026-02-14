import streamlit as st


def render_status(data):

    if not data:
        system_status = "IDLE"
        status_color = "gray"
        status_icon = "⚪"
    else:
        anomalies = data.get("anomalies", [])

        if any("CRITICAL" in alert.upper() for alert in anomalies):
            system_status = "CRITICAL"
            status_color = "red"
            status_icon = "🔴"
        elif anomalies:
            system_status = "WARNING"
            status_color = "orange"
            status_icon = "🟡"
        else:
            system_status = "HEALTHY"
            status_color = "green"
            status_icon = "🟢"

    st.markdown(
        f"""
        <div style="
            background-color:#1a1c24;
            padding:12px 20px;
            border-radius:12px;
            border-left:8px solid {status_color};
            width:320px;
            margin-bottom:20px;
            font-size:18px;
            font-weight:600;">
            {status_icon} SYSTEM STATUS: {system_status}
        </div>
        """,
        unsafe_allow_html=True,
    )
