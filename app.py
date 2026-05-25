import streamlit as st

# ── Page config (must be the very first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="InfoTech Career Navigator",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Load custom CSS ───────────────────────────────────────────────────────────
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── PWA meta tags (add-to-homescreen support) ─────────────────────────────────
st.markdown("""
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="CareerNav">
<meta name="theme-color" content="#667eea">
""", unsafe_allow_html=True)

# ── Session state — initialise all keys with defaults ────────────────────────
defaults = {
    "screen":                  "landing",
    "learner_name":            "",
    "selected_subjects":       {},
    "aps_score":               0,
    "strong_subjects":         [],
    "quiz_answers":            {},
    "personality_scores":      {},
    "top_personality":         [],
    "faculty_matches":         None,
    "selected_faculty":        None,
    "selected_faculty_data":   {},
    "career_matches":          None,
    "top_careers":             [],
    "chosen_careers":          [],
    "chosen_careers_indices":  [],
    "pdf_bytes":               None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ── Router — shows the correct screen based on session state ──────────────────
screen = st.session_state.screen

if screen == "landing":
    from pages.landing import show
    show()

elif screen == "subjects":
    from pages.subjects import show
    show()

elif screen == "personality":
    from pages.personality import show
    show()

elif screen == "results":
    from pages.results import show
    show()

elif screen == "priority":
    from pages.priority import show
    show()

elif screen == "guidance":
    from pages.guidance import show
    show()

elif screen == "roadmap":
    from pages.roadmap import show
    show()