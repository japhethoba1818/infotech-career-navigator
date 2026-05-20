import streamlit as st


def progress_dots(current: int, total: int = 7):
    """Render step progress dots."""
    dots = ""
    for i in range(1, total + 1):
        if i < current:
            cls = "done"
        elif i == current:
            cls = "active"
        else:
            cls = ""
        dots += f'<span class="step-dot {cls}"></span>'
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)


def show():
    progress_dots(1)

    # ── Hero ────────────────────────────────────────────────────────────────
    st.markdown('<div class="tag">🇿🇦 Built for South African Learners</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">InfoTech Career<br>Navigator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Discover the career path that matches your strengths,<br>subjects, and personality — in under 5 minutes.</p>', unsafe_allow_html=True)

    # ── Feature highlights ───────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card" style="text-align:center">
            <div style="font-size:2rem">📚</div>
            <strong>Subject-Based</strong>
            <p style="font-size:0.85rem;color:#6b7280;margin-top:4px">Your school subjects shape your path</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card" style="text-align:center">
            <div style="font-size:2rem">🧠</div>
            <strong>Personality Match</strong>
            <p style="font-size:0.85rem;color:#6b7280;margin-top:4px">Quick quiz to reveal your strengths</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card" style="text-align:center">
            <div style="font-size:2rem">📄</div>
            <strong>Your Roadmap PDF</strong>
            <p style="font-size:0.85rem;color:#6b7280;margin-top:4px">Download your personal success plan</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Name input ───────────────────────────────────────────────────────────
    st.markdown("### What's your name?")
    name = st.text_input(
        label="Your name",
        placeholder="e.g. Naledi Mokoena",
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CTA Button ───────────────────────────────────────────────────────────
    if st.button("🚀  Start Your Journey", use_container_width=True):
        if not name.strip():
            st.warning("Please enter your name to continue.")
        else:
            st.session_state.learner_name = name.strip()
            st.session_state.screen = "subjects"
            st.rerun()

    # ── Footer ───────────────────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#9ca3af;font-size:0.8rem">'
        '🔒 No data stored · Free to use · Made for township & rural learners'
        '</p>',
        unsafe_allow_html=True,
    )