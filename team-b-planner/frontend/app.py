
"""
Enhanced Streamlit frontend with analytics and personalization.

New features:
- Performance dashboard
- Topic mastery visualization
- Learning velocity tracking
- Personalized recommendations
"""

import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------
# Config
# --------------------------------

BACKEND_URL = "http://127.0.0.1:8000"
USER_ID = "default_user"

st.set_page_config(
    page_title="AI Practice Planner Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------
# Helper Functions
# --------------------------------


def get_analytics():
    """Fetch user analytics from backend."""
    try:
        res = requests.get(f"{BACKEND_URL}/analytics/{USER_ID}", timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"Failed to fetch analytics: {e}")
        return None


def get_profile():
    """Fetch user profile summary."""
    try:
        res = requests.get(f"{BACKEND_URL}/profile/{USER_ID}", timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return None


# --------------------------------
# Sidebar - User Stats
# --------------------------------

with st.sidebar:
    st.title("📊 Your Stats")
    
    profile = get_profile()
    if profile:
        stats = profile.get("statistics", {})
        
        st.metric("Total Sessions", stats.get("total_sessions", 0))
        st.metric("Problems Solved", stats.get("total_problems_solved", 0))
        st.metric("Current Streak", stats.get("current_streak", 0))
        st.metric("Longest Streak", stats.get("longest_streak", 0))
        
        if stats.get("total_practice_time", 0) > 0:
            hours = stats["total_practice_time"] / 60
            st.metric("Total Practice Time", f"{hours:.1f} hrs")
    
    st.divider()
    
    if st.button("🔄 Reset Profile", type="secondary"):
        try:
            res = requests.post(f"{BACKEND_URL}/reset_profile/{USER_ID}", timeout=10)
            if res.status_code == 200:
                st.success("Profile reset!")
                st.rerun()
        except Exception as e:
            st.error(f"Reset failed: {e}")


# --------------------------------
# Main App
# --------------------------------

st.title("🧠 AI Practice Planner Pro")
st.caption("Personalized LeetCode practice with intelligent adaptation")

# --------------------------------
# Tabs
# --------------------------------

tab1, tab2, tab3 = st.tabs(["📅 Plan", "📈 Analytics", "💡 Insights"])

# --------------------------------
# Tab 1: Plan Generation
# --------------------------------

with tab1:
    st.header("🕒 Study Settings")

    col1, col2, col3 = st.columns(3)

    with col1:
        time_limit = st.number_input(
            "Daily Time (minutes)", 
            min_value=10, 
            max_value=300, 
            value=60, 
            step=5
        )

    with col2:
        min_d = st.slider("Min Difficulty", 1, 10, 3)

    with col3:
        max_d = st.slider("Max Difficulty", 1, 10, 7)

    if st.button("🚀 Generate Personalized Plan", type="primary"):
        payload = {
            "time": time_limit, 
            "min_d": min_d, 
            "max_d": max_d,
            "user_id": USER_ID
        }

        try:
            with st.spinner("Generating your personalized plan..."):
                res = requests.post(
                    f"{BACKEND_URL}/generate_plan", 
                    json=payload, 
                    timeout=10
                )
                res.raise_for_status()
                response = res.json()

            plan = response.get("plan", [])
            recommendations = response.get("recommendations", {})
            
            if not plan:
                st.warning("No suitable problems found. Try adjusting difficulty range.")
            else:
                st.success(f"✅ Generated plan with {len(plan)} problems!")
                
                # Show recommendations
                if recommendations.get("status") != "no_data":
                    with st.expander("💡 Personalized Recommendations", expanded=True):
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric(
                                "Your Skill Level", 
                                recommendations.get("current_skill_level", "N/A")
                            )
                        
                        with col_b:
                            st.metric(
                                "Problems Solved", 
                                recommendations.get("total_problems_solved", 0)
                            )
                        
                        with col_c:
                            st.metric(
                                "Plan Efficiency",
                                recommendations.get("plan_efficiency", "N/A")
                            )
                        
                        # Weak topics
                        if recommendations.get("weak_topics"):
                            st.write("**🎯 Topics to Focus On:**")
                            for topic_info in recommendations["weak_topics"]:
                                st.write(f"• {topic_info['topic']}: {topic_info['mastery']}% mastery")
                
                st.session_state["plan"] = plan

        except Exception as e:
            st.error(f"Backend error: {e}")

    # Display Plan
    if "plan" in st.session_state:
        st.divider()
        st.header("📋 Your Personalized Study Plan")

        plan = st.session_state["plan"]
        
        for i, p in enumerate(plan, start=1):
            with st.container():
                col_main, col_meta = st.columns([3, 1])
                
                with col_main:
                    st.markdown(f"### {i}. {p['title']}")
                    st.markdown(f"**Topics:** {', '.join(p['topics'])}")
                    
                with col_meta:
                    # Show personalized vs base difficulty
                    if "personalized_difficulty" in p:
                        st.metric(
                            "Your Difficulty", 
                            p['personalized_difficulty'],
                            delta=f"{p['personalized_difficulty'] - p['difficulty']:.1f}"
                        )
                    else:
                        st.metric("Difficulty", p['difficulty'])
                    
                    est_time = p.get('estimated_time', p['duration'])
                    st.write(f"⏱️ ~{est_time} min")
                    
                    if p.get('priority_score'):
                        st.caption(f"Priority: {p['priority_score']}")
                
                st.divider()

    # Feedback Section
    if "plan" in st.session_state:
        st.header("📝 Submit Feedback")
        st.caption("Help the AI learn your skill level")

        feedback_list = []
        
        for p in st.session_state["plan"]:
            with st.container():
                col_name, col_time, col_feedback = st.columns([2, 1, 2])
                
                with col_name:
                    st.write(f"**{p['title']}**")
                
                with col_time:
                    time_spent = st.number_input(
                        "Time spent (min)",
                        min_value=1,
                        max_value=300,
                        value=p.get('estimated_time', p['duration']),
                        key=f"time_{p['id']}"
                    )
                
                with col_feedback:
                    choice = st.radio(
                        "Feedback",
                        ["too_easy", "just_right", "too_hard"],
                        horizontal=True,
                        key=f"fb_{p['id']}",
                        label_visibility="collapsed"
                    )

                feedback_list.append({
                    "problem_id": p["id"], 
                    "feedback": choice,
                    "time_spent": time_spent
                })

        if st.button("✅ Submit All Feedback", type="primary"):
            payload = {
                "feedback": feedback_list,
                "user_id": USER_ID
            }

            try:
                with st.spinner("Updating your profile..."):
                    res = requests.post(
                        f"{BACKEND_URL}/feedback", 
                        json=payload, 
                        timeout=10
                    )
                    res.raise_for_status()
                    result = res.json()

                st.success("✅ Feedback submitted! Your profile has been updated.")
                
                # Show insights
                insights = result.get("insights", {})
                if insights.get("status") == "active":
                    with st.expander("📊 Your Performance Insights", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Success Rate", f"{insights['success_rate']}%")
                        
                        with col2:
                            st.metric("Speed Factor", insights['speed_factor'])
                        
                        with col3:
                            velocity = insights['learning_velocity']
                            emoji = "📈" if velocity == "improving" else "📊" if velocity == "stable" else "📉"
                            st.metric("Learning Trend", f"{emoji} {velocity.title()}")
                        
                        if insights.get("recommendations"):
                            st.write("**💡 Recommendations:**")
                            for rec in insights["recommendations"]:
                                st.info(rec)
                
                # Keep the plan visible, don't restart
                st.session_state["feedback_submitted"] = True
                st.info("💡 Your profile has been updated! You can now generate a new plan with personalized recommendations, or adjust settings and try again.")

            except Exception as e:
                st.error(f"Failed to send feedback: {e}")


# --------------------------------
# Tab 2: Analytics
# --------------------------------

with tab2:
    st.header("📈 Performance Analytics")
    
    analytics = get_analytics()
    
    if analytics and analytics.get("insights", {}).get("status") == "active":
        insights = analytics["insights"]
        stats = analytics["statistics"]
        
        # Key Metrics
        st.subheader("🎯 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Success Rate", 
                f"{insights['success_rate']}%",
                help="Percentage of problems you've successfully solved"
            )
        
        with col2:
            st.metric(
                "Speed Factor", 
                insights['speed_factor'],
                help="Your solving speed vs average (1.0 = average)"
            )
        
        with col3:
            velocity = insights['learning_velocity']
            delta_color = "normal" if velocity == "stable" else "inverse" if velocity == "declining" else "off"
            st.metric(
                "Learning Velocity", 
                velocity.title(),
                help="Your learning trend over time"
            )
        
        with col4:
            st.metric(
                "Total Problems", 
                insights['total_problems']
            )
        
        st.divider()
        
        # Topic Mastery
        if analytics.get("topic_mastery"):
            st.subheader("🎓 Topic Mastery")
            
            topic_data = analytics["topic_mastery"]
            df = pd.DataFrame([
                {"Topic": topic, "Mastery": mastery * 100}
                for topic, mastery in topic_data.items()
            ]).sort_values("Mastery", ascending=False)
            
            if not df.empty:
                fig = px.bar(
                    df, 
                    x="Topic", 
                    y="Mastery",
                    color="Mastery",
                    color_continuous_scale="Viridis",
                    labels={"Mastery": "Mastery %"},
                    title="Mastery Level by Topic"
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Recommendations
        if insights.get("recommendations"):
            st.subheader("💡 Personalized Recommendations")
            for rec in insights["recommendations"]:
                st.info(rec)
    
    else:
        st.info("📊 Complete some practice sessions to see analytics!")


# --------------------------------
# Tab 3: Insights
# --------------------------------

with tab3:
    st.header("💡 Learning Insights")
    
    analytics = get_analytics()
    profile = get_profile()
    
    if analytics and profile:
        # Progress Overview
        st.subheader("📊 Progress Overview")
        
        stats = profile.get("statistics", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Session stats
            st.markdown("**Session Statistics**")
            st.write(f"• Total Sessions: {stats.get('total_sessions', 0)}")
            st.write(f"• Problems Attempted: {stats.get('total_problems_attempted', 0)}")
            st.write(f"• Problems Solved: {stats.get('total_problems_solved', 0)}")
            
            if stats.get('total_problems_attempted', 0) > 0:
                solve_rate = (stats['total_problems_solved'] / stats['total_problems_attempted']) * 100
                st.write(f"• Overall Solve Rate: {solve_rate:.1f}%")
        
        with col2:
            # Streak info
            st.markdown("**Streak Information**")
            st.write(f"• Current Streak: {stats.get('current_streak', 0)} days")
            st.write(f"• Longest Streak: {stats.get('longest_streak', 0)} days")
            
            if stats.get('total_practice_time', 0) > 0:
                hours = stats['total_practice_time'] / 60
                st.write(f"• Total Practice: {hours:.1f} hours")
                
                if stats.get('total_sessions', 0) > 0:
                    avg_session = stats['total_practice_time'] / stats['total_sessions']
                    st.write(f"• Avg Session: {avg_session:.1f} minutes")
        
        st.divider()
        
        # Topic insights
        if analytics.get("topic_mastery"):
            st.subheader("🎯 Topic Breakdown")
            
            topic_mastery = analytics["topic_mastery"]
            
            # Categorize topics
            strong_topics = [(t, m) for t, m in topic_mastery.items() if m > 0.7]
            developing_topics = [(t, m) for t, m in topic_mastery.items() if 0.4 <= m <= 0.7]
            weak_topics = [(t, m) for t, m in topic_mastery.items() if m < 0.4]
            
            col_strong, col_dev, col_weak = st.columns(3)
            
            with col_strong:
                st.markdown("**💪 Strong Topics**")
                if strong_topics:
                    for topic, mastery in sorted(strong_topics, key=lambda x: x[1], reverse=True):
                        st.write(f"• {topic}: {mastery*100:.0f}%")
                else:
                    st.caption("Keep practicing!")
            
            with col_dev:
                st.markdown("**📚 Developing Topics**")
                if developing_topics:
                    for topic, mastery in sorted(developing_topics, key=lambda x: x[1], reverse=True):
                        st.write(f"• {topic}: {mastery*100:.0f}%")
                else:
                    st.caption("No topics in this range")
            
            with col_weak:
                st.markdown("**🎓 Focus Areas**")
                if weak_topics:
                    for topic, mastery in sorted(weak_topics, key=lambda x: x[1]):
                        st.write(f"• {topic}: {mastery*100:.0f}%")
                else:
                    st.caption("Great work!")
    
    else:
        st.info("💡 Complete practice sessions to unlock insights!")


# --------------------------------
# Footer
# --------------------------------

st.divider()
st.caption("AI Practice Planner Pro v2.0 | Powered by intelligent adaptation")