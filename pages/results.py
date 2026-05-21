import json
import streamlit as st
from logic.matcher import match_faculties, match_careers_in_faculty


# ── Helpers ───────────────────────────────────────────────────────────────────

def progress_dots(current: int, total: int = 7):
    dots = ""
    for i in range(1, total + 1):
        cls = "done" if i < current else ("active" if i == current else "")
        dots += f'<span class="step-dot {cls}"></span>'
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)


def load_personality_meta() -> tuple:
    with open("data/personality.json") as f:
        d = json.load(f)
    return d["personality_types"], d["type_icons"], d["type_descriptions"]


def match_bar(pct: int, color: str = "linear-gradient(135deg,#667eea,#764ba2)") -> str:
    return f"""
    <div style="margin:6px 0 10px 0">
        <div style="display:flex;justify-content:space-between;
                    font-size:0.78rem;color:#6b7280;margin-bottom:3px">
            <span>Match score</span>
            <span style="font-weight:700;color:#7c3aed">{pct}%</span>
        </div>
        <div style="background:#e5e7eb;border-radius:99px;height:8px">
            <div style="background:{color};width:{pct}%;height:8px;
                        border-radius:99px"></div>
        </div>
    </div>
    """


FACULTY_COLOURS = [
    "linear-gradient(135deg,#667eea,#764ba2)",
    "linear-gradient(135deg,#f093fb,#f5576c)",
    "linear-gradient(135deg,#4facfe,#00f2fe)",
]

CAREER_COLOURS = [
    "linear-gradient(135deg,#667eea,#764ba2)",
    "linear-gradient(135deg,#f093fb,#f5576c)",
    "linear-gradient(135deg,#4facfe,#00f2fe)",
]


# ── Stage 1 — Faculty Recommendations ────────────────────────────────────────

def _show_faculty_stage(labels, icons, descs):
    name = st.session_state.learner_name.split()[0]

    st.markdown(
        f'<h1 class="hero-title">Your Field of Interest, {name} 🎯</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-subtitle">'
        'Based on your personality, subjects and APS — here are the three '
        'fields where you have the strongest potential. '
        '<strong>Pick the one that excites you most.</strong>'
        '</p>',
        unsafe_allow_html=True,
    )

    # ── Run faculty matching (cache in session) ───────────────────────────────
    if not st.session_state.get("faculty_matches"):
        with st.spinner("Matching your profile to fields..."):
            results = match_faculties(
                personality_scores = st.session_state.personality_scores,
                subject_ratings    = st.session_state.selected_subjects,
                learner_aps        = st.session_state.aps_score,
                personality_labels = labels,
                personality_icons  = icons,
                top_n              = 3,
            )
        st.session_state.faculty_matches = results
    else:
        results = st.session_state.faculty_matches

    # ── Learner snapshot bar ──────────────────────────────────────────────────
    top_code  = (st.session_state.top_personality or ["ANL"])[0]
    top_label = labels.get(top_code, "")
    top_icon  = icons.get(top_code, "💡")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#667eea18,#764ba218);
                border:1px solid #667eea33;border-radius:12px;
                padding:0.8rem 1.2rem;margin-bottom:1.5rem;
                display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap">
        <span style="font-size:0.85rem;color:#4b5563">
            📋 <strong>APS {st.session_state.aps_score}</strong>
        </span>
        <span style="font-size:0.85rem;color:#4b5563">
            {top_icon} <strong>{top_label}</strong> personality
        </span>
        <span style="font-size:0.85rem;color:#4b5563">
            📚 <strong>{len(st.session_state.selected_subjects)}</strong> subjects
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Faculty cards ─────────────────────────────────────────────────────────
    st.markdown("### 🏛️ Your Top 3 Fields")

    for i, result in enumerate(results):
        faculty = result["faculty"]
        pct     = result["match_pct"]
        reasons = result["reasons"]
        colour  = FACULTY_COLOURS[i]
        rank    = ["🥇 Best Fit", "🥈 Strong Fit", "🥉 Good Fit"][i]

        st.markdown(f"""
        <div style="background:white;border:1.5px solid #e5e7eb;
                    border-radius:16px;padding:1.2rem 1.4rem;
                    margin-bottom:0.5rem;
                    box-shadow:0 2px 8px rgba(102,126,234,0.08)">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;flex-wrap:wrap;gap:8px">
                <div>
                    <span style="background:#ede9fe;color:#7c3aed;
                                 border-radius:20px;padding:2px 10px;
                                 font-size:0.72rem;font-weight:600">
                        {rank}
                    </span>
                    <div style="font-size:1.25rem;font-weight:800;
                                color:#1f2937;margin:6px 0 2px 0">
                        {faculty['icon']}  {faculty['title']}
                    </div>
                    <div style="font-size:0.85rem;color:#6b7280;
                                font-style:italic">
                        "{faculty['tagline']}"
                    </div>
                </div>
                <div style="text-align:right;min-width:60px">
                    <div style="font-size:2rem;font-weight:800;
                                background:{colour};
                                -webkit-background-clip:text;
                                -webkit-text-fill-color:transparent">
                        {pct}%
                    </div>
                    <div style="font-size:0.68rem;color:#9ca3af">match</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Match bar
        st.markdown(match_bar(pct, colour), unsafe_allow_html=True)

        # Why it matches
        for reason in reasons:
            st.markdown(
                f'<div style="padding:3px 0 3px 8px;font-size:0.87rem;'
                f'color:#374151;border-left:3px solid #667eea33">'
                f'{reason}</div>',
                unsafe_allow_html=True,
            )

        # Universities teaser
        st.markdown(
            f'<div style="font-size:0.78rem;color:#9ca3af;margin:8px 0 4px 0">'
            f'🏫 {faculty["example_unis"]}</div>',
            unsafe_allow_html=True,
        )

        # Select button
        btn_key = f"select_faculty_{faculty['id']}"
        if st.button(
            f"Explore {faculty['title']} →",
            key=btn_key,
            use_container_width=True,
        ):
            st.session_state.selected_faculty      = faculty["id"]
            st.session_state.selected_faculty_data = result
            st.session_state.career_matches        = None  # reset any old career matches
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Back navigation ───────────────────────────────────────────────────────
    if st.button("← Back to Personality Quiz", use_container_width=True):
        st.session_state.screen = "personality"
        st.rerun()


# ── Stage 2 — Careers Within Selected Faculty ────────────────────────────────

def _show_career_stage(labels, icons, descs):
    faculty_id   = st.session_state.selected_faculty
    faculty_data = st.session_state.get("selected_faculty_data", {})
    faculty_info = faculty_data.get("faculty", {})
    name         = st.session_state.learner_name.split()[0]

    # ── Selected faculty banner ───────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                border-radius:14px;padding:1rem 1.4rem;
                margin-bottom:1.5rem">
        <div style="color:rgba(255,255,255,0.75);font-size:0.78rem;
                    font-weight:600;text-transform:uppercase">
            Your Chosen Field
        </div>
        <div style="color:white;font-size:1.3rem;font-weight:800;margin:2px 0">
            {faculty_info.get('icon','')}  {faculty_info.get('title','')}
        </div>
        <div style="color:rgba(255,255,255,0.8);font-size:0.85rem">
            {faculty_info.get('description','')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<h1 class="hero-title">Your Career Options, {name} 💼</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-subtitle">'
        'These are the top careers within your chosen field, '
        'ranked specifically for your profile. '
        'Review them — then proceed to set your priorities.'
        '</p>',
        unsafe_allow_html=True,
    )

    # ── Run career matching within faculty (cache in session) ─────────────────
    if not st.session_state.get("career_matches"):
        with st.spinner("Finding your best career options..."):
            career_results = match_careers_in_faculty(
                faculty_id         = faculty_id,
                subject_ratings    = st.session_state.selected_subjects,
                learner_aps        = st.session_state.aps_score,
                personality_scores = st.session_state.personality_scores,
                top_personality    = st.session_state.top_personality,
                personality_labels = labels,
                personality_icons  = icons,
                top_n              = 3,
            )
        st.session_state.career_matches = career_results
    else:
        career_results = st.session_state.career_matches

    if not career_results:
        st.error("No career data found for this field. Please go back and try another.")
        if st.button("← Change Field"):
            st.session_state.selected_faculty = None
            st.rerun()
        return

    # ── Career cards ──────────────────────────────────────────────────────────
    rank_labels = ["🥇 Top Match", "🥈 Strong Match", "🥉 Good Match"]

    for i, result in enumerate(career_results):
        career  = result["career"]
        pct     = result["match_pct"]
        reasons = result["reasons"]
        colour  = CAREER_COLOURS[i]

        with st.expander(
            f"{rank_labels[i]} — {career['icon']} {career['title']}  ({pct}% match)",
            expanded=True,
        ):
            st.markdown(match_bar(pct, colour), unsafe_allow_html=True)

            # Career tagline
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#f8f9ff,#f0f4ff);
                        border-left:4px solid #667eea;border-radius:0 8px 8px 0;
                        padding:8px 12px;margin-bottom:0.75rem;
                        font-style:italic;color:#4b5563;font-size:0.9rem">
                "{career['tagline']}"
            </div>
            """, unsafe_allow_html=True)

            # Description
            st.markdown(
                f'<p style="color:#4b5563;font-size:0.9rem;'
                f'margin-bottom:0.75rem">{career["description"]}</p>',
                unsafe_allow_html=True,
            )

            # Why you match
            st.markdown(
                '<div style="font-weight:600;color:#1f2937;'
                'font-size:0.88rem;margin-bottom:4px">Why you match:</div>',
                unsafe_allow_html=True,
            )
            for reason in reasons:
                st.markdown(
                    f'<div style="padding:4px 0 4px 8px;font-size:0.87rem;'
                    f'color:#374151;border-left:3px solid #667eea55;'
                    f'margin-bottom:2px">{reason}</div>',
                    unsafe_allow_html=True,
                )

            # Score breakdown
            st.markdown("<br>", unsafe_allow_html=True)
            sc1, sc2, sc3 = st.columns(3)
            for col, lbl, val in [
                (sc1, "Subject Match",  result["subject_score"]),
                (sc2, "APS Match",      result["aps_score"]),
                (sc3, "Personality",    result["personality_score"]),
            ]:
                with col:
                    st.markdown(f"""
                    <div style="text-align:center;background:#f3f4f6;
                                border-radius:10px;padding:8px">
                        <div style="font-size:0.68rem;color:#9ca3af">{lbl}</div>
                        <div style="font-weight:700;color:#667eea">{val}%</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    col_back, col_next = st.columns(2)

    with col_back:
        if st.button("← Change Field", use_container_width=True):
            st.session_state.selected_faculty = None
            st.session_state.career_matches   = None
            st.rerun()

    with col_next:
        if st.button("Set My Priorities →", use_container_width=True):
            # Pass career matches to priority selection
            st.session_state.top_careers = career_results
            st.session_state.screen      = "priority"
            st.rerun()


# ── Main entry point ──────────────────────────────────────────────────────────

def show():
    progress_dots(4)

    labels, icons, descs = load_personality_meta()

    # Initialise faculty selection state
    if "selected_faculty" not in st.session_state:
        st.session_state.selected_faculty = None

    # Route to correct stage
    if st.session_state.selected_faculty is None:
        _show_faculty_stage(labels, icons, descs)
    else:
        _show_career_stage(labels, icons, descs)