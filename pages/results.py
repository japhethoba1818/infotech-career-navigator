import json
import streamlit as st
from logic.matcher import match_careers


# ── Helpers ───────────────────────────────────────────────────────────────────

def progress_dots(current: int, total: int = 7):
    dots = ""
    for i in range(1, total + 1):
        cls = "done" if i < current else ("active" if i == current else "")
        dots += f'<span class="step-dot {cls}"></span>'
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)


def load_personality_meta() -> tuple:
    with open("data/personality.json") as f:
        data = json.load(f)
    return data["personality_types"], data["type_icons"], data["type_descriptions"]


def match_bar(pct: int, color: str = "linear-gradient(135deg,#667eea,#764ba2)") -> str:
    return f"""
    <div style="margin: 6px 0 12px 0">
        <div style="display:flex;justify-content:space-between;
                    font-size:0.8rem;color:#6b7280;margin-bottom:3px">
            <span>Match score</span>
            <span style="font-weight:700;color:#7c3aed">{pct}%</span>
        </div>
        <div style="background:#e5e7eb;border-radius:99px;height:10px">
            <div style="background:{color};width:{pct}%;height:10px;
                        border-radius:99px;transition:width 0.5s ease">
            </div>
        </div>
    </div>
    """


RANK_COLORS = [
    "linear-gradient(135deg,#667eea,#764ba2)",   # 1st — purple
    "linear-gradient(135deg,#f093fb,#f5576c)",   # 2nd — pink
    "linear-gradient(135deg,#4facfe,#00f2fe)",   # 3rd — blue
]

RANK_LABELS = ["🥇 Best Match", "🥈 Strong Match", "🥉 Good Match"]


# ── Main screen ───────────────────────────────────────────────────────────────

def show():
    progress_dots(4)

    labels, icons, descs = load_personality_meta()
    name  = st.session_state.learner_name.split()[0]

    # ── Run the matcher ───────────────────────────────────────────────────────
    # Cache results in session so they don't recalculate on every interaction
    if "top_careers" not in st.session_state or not st.session_state.top_careers:
        with st.spinner("Matching your profile to careers..."):
            results = match_careers(
                subject_ratings    = st.session_state.selected_subjects,
                learner_aps        = st.session_state.aps_score,
                personality_scores = st.session_state.personality_scores,
                top_personality    = st.session_state.top_personality,
                personality_labels = labels,
                personality_icons  = icons,
                top_n              = 3,
            )
        st.session_state.top_careers = results
    else:
        results = st.session_state.top_careers

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        f'<h1 class="hero-title">Your Matches, {name} 🎯</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-subtitle">Based on your subjects, APS score and personality — '
        'here are the three careers where you have the strongest potential.</p>',
        unsafe_allow_html=True,
    )

    # ── Learner snapshot ──────────────────────────────────────────────────────
    top_type_code = st.session_state.top_personality[0] if st.session_state.top_personality else "ANL"
    top_type_name = labels.get(top_type_code, "")
    top_type_icon = icons.get(top_type_code, "💡")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:1rem">
            <div style="font-size:1.8rem">📋</div>
            <div style="font-size:0.75rem;color:#6b7280">Your APS Score</div>
            <div style="font-size:1.8rem;font-weight:800;
                        background:linear-gradient(135deg,#667eea,#764ba2);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent">
                {st.session_state.aps_score}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:1rem">
            <div style="font-size:1.8rem">{top_type_icon}</div>
            <div style="font-size:0.75rem;color:#6b7280">Top Personality</div>
            <div style="font-size:1rem;font-weight:700;color:#1f2937;margin-top:2px">
                {top_type_name}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        subj_count = len(st.session_state.selected_subjects)
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:1rem">
            <div style="font-size:1.8rem">📚</div>
            <div style="font-size:0.75rem;color:#6b7280">Subjects Captured</div>
            <div style="font-size:1.8rem;font-weight:800;
                        background:linear-gradient(135deg,#667eea,#764ba2);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent">
                {subj_count}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🏆 Your Top 3 Career Matches")

    # ── Career result cards ───────────────────────────────────────────────────
    for i, result in enumerate(results):
        career  = result["career"]
        pct     = result["match_pct"]
        reasons = result["reasons"]
        color   = RANK_COLORS[i]
        rank    = RANK_LABELS[i]

        with st.expander(
            f"{rank} — {career['icon']} {career['title']}  ({pct}% match)",
            expanded=(i == 0),   # first card open by default
        ):
            # Match bar
            st.markdown(match_bar(pct, color), unsafe_allow_html=True)

            # Tagline
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#f8f9ff,#f0f4ff);
                        border-left:4px solid #667eea;border-radius:0 8px 8px 0;
                        padding:10px 14px;margin-bottom:1rem;
                        font-style:italic;color:#4b5563">
                "{career['tagline']}"
            </div>
            """, unsafe_allow_html=True)

            # Description
            st.markdown(
                f'<p style="color:#4b5563;font-size:0.95rem">{career["description"]}</p>',
                unsafe_allow_html=True,
            )

            # Why you match
            st.markdown("**Why you match:**")
            for reason in reasons:
                st.markdown(
                    f'<div style="padding:6px 0;color:#374151;font-size:0.9rem">'
                    f'&nbsp;&nbsp;{reason}</div>',
                    unsafe_allow_html=True,
                )

            # Score breakdown
            st.markdown("<br>", unsafe_allow_html=True)
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown(f"""
                <div style="text-align:center;background:#f3f4f6;
                            border-radius:10px;padding:8px">
                    <div style="font-size:0.7rem;color:#9ca3af">Subject Match</div>
                    <div style="font-weight:700;color:#667eea">
                        {result['subject_score']}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with sc2:
                st.markdown(f"""
                <div style="text-align:center;background:#f3f4f6;
                            border-radius:10px;padding:8px">
                    <div style="font-size:0.7rem;color:#9ca3af">APS Match</div>
                    <div style="font-weight:700;color:#667eea">
                        {result['aps_score']}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with sc3:
                st.markdown(f"""
                <div style="text-align:center;background:#f3f4f6;
                            border-radius:10px;padding:8px">
                    <div style="font-size:0.7rem;color:#9ca3af">Personality</div>
                    <div style="font-weight:700;color:#667eea">
                        {result['personality_score']}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    col_back, col_next = st.columns(2)

    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = "personality"
            st.rerun()

    with col_next:
        if st.button("Choose My Priorities →", use_container_width=True):
            st.session_state.screen = "priority"
            st.rerun()