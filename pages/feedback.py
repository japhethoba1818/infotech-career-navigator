import streamlit as st


def progress_dots(current: int, total: int = 7):
    dots = ""
    for i in range(1, total + 1):
        cls = "done" if i < current else ("active" if i == current else "")
        dots += f'<span class="step-dot {cls}"></span>'
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)


# ── Paste your Google Form embed URL here ─────────────────────────────────────
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/YOUR_FORM_ID_HERE/viewform"


def show():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                border-radius:16px;padding:1.5rem;text-align:center;
                margin-bottom:1.5rem">
        <div style="font-size:2rem">📊</div>
        <h2 style="color:white;margin:8px 0 4px 0;font-size:1.3rem">
            Help Us Help More Learners
        </h2>
        <p style="color:rgba(255,255,255,0.85);margin:0;font-size:0.9rem">
            Your honest answers help us improve this app and reach more
            rural learners across South Africa. It takes 2 minutes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-bottom:1rem">
        <strong>Why your feedback matters:</strong><br>
        <span style="color:#6b7280;font-size:0.88rem">
        We tested this app with real learners in Soshanguve and Tshwane.
        Your feedback helps us secure funding and partnerships to keep
        this tool free for every South African learner — forever.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Embed the Google Form ─────────────────────────────────────────────────
    st.components.v1.iframe(
        src=GOOGLE_FORM_URL + "?embedded=true",
        height=900,
        scrolling=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <p style="text-align:center;color:#9ca3af;font-size:0.78rem">
        Your responses are anonymous and used only to improve the app.<br>
        InfoTech Rural · Bridging the digital divide, one learner at a time.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("← Back to Home", use_container_width=True):
        st.session_state.screen = "landing"
        st.rerun()