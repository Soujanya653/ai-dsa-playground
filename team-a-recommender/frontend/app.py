import streamlit as st
import requests
import streamlit.components.v1 as components

# -----------------------------
# Config
# -----------------------------
BACKEND_URL = "http://127.0.0.1:8000/recommend"

st.set_page_config(
    page_title="AI-DSA Recommender",
    page_icon="",
    layout="wide", 
)

# Premium UI Styling with Animations & Smooth Scroll Logic
st.markdown("""
    <style>
    /* Main App Background & Layout Reset */
    .stApp {
        background-color: #FDFCFE;
    }
    .block-container {
        padding-top: 1.5rem !important;
    }

    /* Keyframes for the 'Innovative' Entrance */
    @keyframes cardEntrance {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Hide 'Press Ctrl+Enter' and fix double background line */
    .stTextArea div[data-baseweb="textarea"] {
        background-color: white !important;
        border: 2px solid #BCB0D9 !important;
        border-radius: 12px !important;
    }
    .stTextArea textarea {
        background-color: white !important;
        color: #1E293B !important;
        padding: 15px !important;
    }
    .stTextArea div[data-baseweb="textarea"] + div { display: none !important; }

    /* Main Button - Vibrant Coral */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF5252 100%);
        color: white;
        font-weight: 800;
        font-size: 16px;
        border: 2px solid #FF3D3D;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(255, 107, 107, 0.4);
    }

    /* Card Layout */
    .recommendation-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 2px solid #BCB0D9; 
        box-shadow: 0 4px 6px rgba(124, 58, 237, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 280px; 
        opacity: 0; /* Starts hidden for animation */
        animation: cardEntrance 0.7s cubic-bezier(0.23, 1, 0.32, 1) forwards;
    }
    
    .recommendation-card:hover {
        border-color: #7C3AED;
        box-shadow: 0 12px 24px rgba(124, 58, 237, 0.15);
        transform: translateY(-5px);
    }

    .problem-title { color: #111827; font-size: 22px; font-weight: 800; margin: 0; line-height: 1.3; }
    .score-badge { font-weight: 700; color: #5B21B6; background: #F3E8FF; padding: 6px 14px; border-radius: 8px; border: 2px solid #DDD6FE; margin-top: 12px; display: inline-block; }
    
    .difficulty-tag { font-size: 11px; font-weight: 900; padding: 6px 14px; border-radius: 10px; text-transform: uppercase; }
    .easy { background-color: #DCFCE7; color: #14532D; border: 1px solid #BBF7D0; }
    .medium { background-color: #FEF9C3; color: #713F12; border: 1px solid #FEF08A; }
    .hard { background-color: #FEE2E2; color: #7F1D1D; border: 1px solid #FECACA; }

    .pattern-chip { background: #F8FAFC; color: #334155; font-size: 11px; font-weight: 700; padding: 5px 12px; border-radius: 6px; border: 1.5px solid #CBD5E1; }
    .footer-text { margin-top: auto; font-size: 13px; color: #475569; border-top: 2px solid #E2E8F0; padding-top: 15px; font-weight: 600; }
    
    /* Target for Smooth Scroll */
    #scroll-target {
        padding-bottom: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("<h2 style='color: #4C1D95; border-bottom: 3px solid #E9D5FF; padding-bottom: 10px;'> Settings</h2>", unsafe_allow_html=True)
    top_k = st.slider("Results to show", 1, 10, 5)
    st.divider()
    st.info("AI maps problem semantics to find optimal DSA patterns.")

# -----------------------------
# Main Content
# -----------------------------
_, mid_col, _ = st.columns([0.025, 0.95, 0.025]) 

with mid_col:
    st.markdown("<h1 style='font-size: 3rem; color: #111827; margin-bottom: 0;'> AI‑DSA Recommender</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #64748B; margin-bottom: 25px; font-weight: 500;'>Analyze coding patterns and discover matching LeetCode challenges.</h4>", unsafe_allow_html=True)
    
    query = st.text_area(
        "Problem description",
        placeholder="Paste a problem description here...",
        height=200 
    )

    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)

    if st.button("Generate Smart Recommendations"):
        if not query.strip():
            st.warning("Please enter a problem description.")
        else:
            # Anchor point for scrolling
            st.markdown('<div id="scroll-target"></div>', unsafe_allow_html=True)
            
            with st.spinner("Decoding algorithmic patterns..."):
                try:
                    response = requests.post(
                        BACKEND_URL,
                        json={"query": query, "top_k": top_k},
                        timeout=10,
                    )

                    if response.status_code == 200:
                        results = response.json().get("results", [])
                        if not results:
                            st.info("No recommendations found.")
                        else:
                            st.success(f"Discovered {len(results)} matches")
                            
                            # INNOVATIVE FIX: Auto-scroll JavaScript trigger
                            components.html(
                                f"""
                                <script>
                                    window.parent.document.getElementById('scroll-target').scrollIntoView({{
                                        behavior: 'smooth'
                                    }});
                                </script>
                                """,
                                height=0,
                            )

                            for i in range(0, len(results), 2):
                                cols = st.columns(2)
                                for j in range(2):
                                    if i + j < len(results):
                                        item = results[i + j]
                                        idx = i + j + 1
                                        diff = item['difficulty'].lower()
                                        diff_class = "easy" if "easy" in diff else "medium" if "medium" in diff else "hard"
                                        
                                        # Staggered animation delay calculation
                                        delay = (i + j) * 0.1
                                        
                                        with cols[j]:
                                            st.markdown(f"""
                                                <div class="recommendation-card" style="animation-delay: {delay}s;">
                                                    <div>
                                                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                                                            <h3 class="problem-title">{idx}. {item['title']}</h3>
                                                            <span class="difficulty-tag {diff_class}">{item['difficulty']}</span>
                                                        </div>
                                                        <span class="score-badge">Similarity: {item['score']}</span>
                                                        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 22px;">
                                                            {" ".join([f'<span class="pattern-chip">{t}</span>' for t in item.get('topics', [])])}
                                                        </div>
                                                    </div>
                                                    <div class="footer-text">
                                                         Logic Match: Similar algorithmic signature confirmed.
                                                    </div>
                                                </div>
                                            """, unsafe_allow_html=True)
                    else:
                        st.error("Backend error occurred.")
                except Exception:
                    st.error("Could not reach backend server.")