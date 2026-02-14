import streamlit as st


def render_kpis(data):

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Throughput", f"{data.get('requests_per_min', 0)} RPM")
    c2.metric("Error Rate", f"{data.get('error_rate', 0.0)*100:.1f}%")
    c3.metric("P95 Latency", f"{data.get('p95_latency', 0):.0f} ms")
    c4.metric("Est. Cost", f"${data.get('estimated_cost_usd', 0.0):.4f}")
