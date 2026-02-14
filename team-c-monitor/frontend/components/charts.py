import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def render_charts(data, history):

    st.subheader("📈 Performance Trends")

    col1, col2 = st.columns(2)

    # ---------------- THROUGHPUT ----------------
    with col1:
        if not history.empty:
            st.line_chart(
                history.set_index("Time")["Throughput"]
            )
        else:
            st.info("No throughput data yet.")

    # ---------------- ERROR RATE ----------------
    with col2:
        if not history.empty:
            st.line_chart(
                history.set_index("Time")["ErrorRate"]
            )
        else:
            st.info("No error data yet.")

    # -------- DISTRIBUTION SECTION --------
    st.markdown("---")

    col_l, col_r = st.columns(2)

    # ---------------- LATENCY PERCENTILES ----------------
    with col_l:
        st.subheader("Latency Percentiles")

        lat_data = pd.DataFrame({
            "Level": ["P50", "P95", "P99"],
            "ms": [
                data.get("p50_latency", 0),
                data.get("p95_latency", 0),
                data.get("p99_latency", 0),
            ],
        }).set_index("Level")

        st.bar_chart(lat_data)

    # ---------------- USER DISTRIBUTION ----------------
    with col_r:
        st.subheader("User Distribution")

        user_counts = data.get("per_user_requests", {})

        if user_counts:

            user_df = pd.DataFrame.from_dict(
                user_counts, orient="index", columns=["Requests"]
            ).sort_values("Requests")

            fig, ax = plt.subplots()

            fig.patch.set_facecolor("#0e1117")
            ax.set_facecolor("#0e1117")

            pastel_colors = [
                "#ffadad", "#ffd6a5", "#fdffb6",
                "#caffbf", "#9bf6ff", "#a0c4ff",
                "#bdb2ff", "#ffc6ff"
            ]

            ax.barh(
                user_df.index,
                user_df["Requests"],
                color=pastel_colors[:len(user_df)]
            )

            ax.set_xlabel("Requests", color="white")
            ax.set_ylabel("Users", color="white")
            ax.set_title("Requests per User (Sliding Window)", color="white")

            ax.tick_params(colors="white")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color("white")
            ax.spines['bottom'].set_color("white")

            ax.grid(axis='x', linestyle='--', alpha=0.3)

            st.pyplot(fig)

        else:
            st.info("No active user data in window.")
