import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="InfoTech Career Navigator",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Load custom CSS ──────────────────────────────────────────────────────────
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Session state initialisation ─────────────────────────────────────────────
# This is how we pass data between screens without a database
defaults = {
    "screen": "landing",
    "learner_name": "",
    "selected_subjects": {},   # {subject_name: rating_1_to_7}
    "aps_score": 0,
    "personality_scores": {},  # {type: score}
    "top_careers": [],
    "chosen_careers": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ── Router: show the right screen based on session state ────────────────────
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