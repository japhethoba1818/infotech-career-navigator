import streamlit as st


# ── Helpers ───────────────────────────────────────────────────────────────────

def progress_dots(current: int, total: int = 7):
    dots = ""
    for i in range(1, total + 1):
        cls = "done" if i < current else ("active" if i == current else "")
        dots += f'<span class="step-dot {cls}"></span>'
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)


RANK_STYLES = [
    {
        "label":   "🥇 First Choice",
        "subtext": "Your primary career goal",
        "bg":      "linear-gradient(135deg,#667eea 0%,#764ba2 100%)",
        "text":    "white",
        "border":  "#667eea",
    },
    {
        "label":   "🥈 Second Choice",
        "subtext": "Your backup career path",
        "bg":      "linear-gradient(135deg,#f093fb 0%,#f5576c 100%)",
        "text":    "white",
        "border":  "#f5576c",
    },
    {
        "label":   "🥉 Third Choice",
        "subtext": "Your alternative option",
        "bg":      "linear-gradient(135deg,#4facfe 0%,#00f2fe 100%)",
        "text":    "white",
        "border":  "#4facfe",
    },
]


def career_option_label(result: dict) -> str:
    """Build a display string for the selectbox option."""
    c = result["career"]
    return f"{c['icon']}  {c['title']}  —  {result['match_pct']}% match"


# ── Main screen ───────────────────────────────────────────────────────────────

def show():
    progress_dots(5)

    name    = st.session_state.learner_name.split()[0]
    results = st.session_state.get("top_careers", [])

    if not results:
        st.warning("No career matches found. Please go back and complete the quiz.")
        if st.button("← Go Back"):
            st.session_state.screen = "results"
            st.rerun()
        return

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        f'<h1 class="hero-title">Your Priorities, {name} 🏆</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-subtitle">'
        'Rank your three career matches in order of preference. '
        'Your first choice will anchor your personalised roadmap PDF.'
        '</p>',
        unsafe_allow_html=True,
    )

    # ── Quick career recap ────────────────────────────────────────────────────
    st.markdown("### Your 3 Matches — Quick Recap")

    for i, result in enumerate(results):
        c   = result["career"]
        pct = result["match_pct"]
        st.markdown(f"""
        <div class="card" style="display:flex;align-items:center;
                                  gap:1rem;padding:0.9rem 1.2rem">
            <div style="font-size:2rem">{c['icon']}</div>
            <div style="flex:1">
                <div style="font-weight:700;color:#1f2937;font-size:1rem">
                    {c['title']}
                </div>
                <div style="font-size:0.82rem;color:#6b7280;margin-top:2px">
                    {c['tagline']}
                </div>
            </div>
            <div style="text-align:right;min-width:64px">
                <div style="font-size:1.3rem;font-weight:800;
                            background:linear-gradient(135deg,#667eea,#764ba2);
                            -webkit-background-clip:text;
                            -webkit-text-fill-color:transparent">
                    {pct}%
                </div>
                <div style="font-size:0.7rem;color:#9ca3af">match</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Priority selectors ────────────────────────────────────────────────────
    st.markdown("### Now Rank Them — Drag Your Thinking Here")
    st.markdown(
        '<p style="color:#6b7280;font-size:0.88rem;margin-top:-0.5rem">'
        'Select a different career for each priority slot. '
        'No two slots can hold the same career.</p>',
        unsafe_allow_html=True,
    )

    options = [career_option_label(r) for r in results]

    # Build default selections: 1st=index 0, 2nd=index 1, 3rd=index 2
    prev_choices = st.session_state.get("chosen_careers_indices", [0, 1, 2])

    chosen_indices = []

    for rank_num in range(3):
        style = RANK_STYLES[rank_num]

        st.markdown(f"""
        <div style="background:{style['bg']};border-radius:12px;
                    padding:10px 16px 4px 16px;margin-bottom:4px">
            <div style="color:{style['text']};font-weight:700;font-size:1rem">
                {style['label']}
            </div>
            <div style="color:rgba(255,255,255,0.8);font-size:0.8rem;
                        margin-bottom:6px">
                {style['subtext']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        default_idx = prev_choices[rank_num] if rank_num < len(prev_choices) else rank_num

        chosen = st.selectbox(
            label=f"rank_{rank_num}",
            options=options,
            index=default_idx,
            key=f"priority_select_{rank_num}",
            label_visibility="collapsed",
        )

        chosen_indices.append(options.index(chosen))
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Duplicate validation ──────────────────────────────────────────────────
    has_duplicates = len(set(chosen_indices)) < 3

    if has_duplicates:
        st.warning(
            "⚠️  You've selected the same career in more than one slot. "
            "Please choose a different career for each priority."
        )

    # ── Live confirmation preview ─────────────────────────────────────────────
    if not has_duplicates:
        st.markdown("---")
        st.markdown("### ✅ Your Priority Plan")
        st.markdown(
            '<p style="color:#6b7280;font-size:0.88rem;margin-top:-0.5rem">'
            'This is how your roadmap will be structured.</p>',
            unsafe_allow_html=True,
        )

        for rank_num, idx in enumerate(chosen_indices):
            career  = results[idx]["career"]
            pct     = results[idx]["match_pct"]
            style   = RANK_STYLES[rank_num]

            st.markdown(f"""
            <div style="background:{style['bg']};border-radius:14px;
                        padding:1rem 1.2rem;margin-bottom:0.75rem;
                        display:flex;align-items:center;gap:1rem">
                <div style="font-size:2.2rem">{career['icon']}</div>
                <div>
                    <div style="color:rgba(255,255,255,0.75);
                                font-size:0.75rem;font-weight:600">
                        {style['label']}
                    </div>
                    <div style="color:white;font-weight:700;font-size:1.05rem">
                        {career['title']}
                    </div>
                    <div style="color:rgba(255,255,255,0.8);font-size:0.82rem">
                        {pct}% match · {career['tagline']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    col_back, col_next = st.columns(2)

    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = "results"
            st.rerun()

    with col_next:
        btn_label = "View University Guidance →"
        if st.button(btn_label, use_container_width=True, disabled=has_duplicates):
            # Save the ordered chosen careers to session state
            ordered = [results[i] for i in chosen_indices]
            st.session_state.chosen_careers         = ordered
            st.session_state.chosen_careers_indices = chosen_indices
            st.session_state.screen                 = "guidance"
            st.rerun()