import json
import streamlit as st


# ── Helpers ───────────────────────────────────────────────────────────────────

def progress_dots(current: int, total: int = 7):
    dots = ""
    for i in range(1, total + 1):
        cls = "done" if i < current else ("active" if i == current else "")
        dots += f'<span class="step-dot {cls}"></span>'
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)


def load_guidance() -> dict:
    with open("data/universities.json") as f:
        return json.load(f)["career_guidance"]


def aps_gap_badge(learner_aps: int, required_aps: int) -> str:
    """Colour-coded badge showing how close the learner is to the APS requirement."""
    gap = learner_aps - required_aps
    if gap >= 0:
        colour = "#10b981"   # green
        msg    = f"✅ You qualify (+{gap} above minimum)"
    elif gap >= -5:
        colour = "#f59e0b"   # amber
        msg    = f"⚠️ Almost there ({abs(gap)} points below)"
    elif gap >= -10:
        colour = "#f97316"   # orange
        msg    = f"📈 Within reach ({abs(gap)} points below)"
    else:
        colour = "#ef4444"   # red
        msg    = f"🎯 Target to work toward ({abs(gap)} points below)"

    return f"""
    <span style="background:{colour}22;color:{colour};border:1px solid {colour}66;
                 border-radius:20px;padding:3px 10px;font-size:0.78rem;font-weight:600">
        {msg}
    </span>
    """


RANK_LABELS  = ["🥇 First Choice", "🥈 Second Choice", "🥉 Third Choice"]
RANK_COLOURS = ["#667eea", "#f5576c", "#00c6fb"]


# ── Main screen ───────────────────────────────────────────────────────────────

def show():
    progress_dots(6)

    learner_aps    = st.session_state.get("aps_score", 0)
    chosen_careers = st.session_state.get("chosen_careers", [])
    guidance_data  = load_guidance()
    name           = st.session_state.learner_name.split()[0]

    if not chosen_careers:
        st.warning("No careers selected. Please go back.")
        if st.button("← Go Back"):
            st.session_state.screen = "priority"
            st.rerun()
        return

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        f'<h1 class="hero-title">Your Roadmap, {name} 🎓</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-subtitle">'
        'Detailed university options, APS requirements, job roles '
        'and salary ranges for each of your chosen careers.</p>',
        unsafe_allow_html=True,
    )

    # ── APS reminder banner ───────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#667eea22,#764ba222);
                border:1px solid #667eea44;border-radius:12px;
                padding:0.9rem 1.2rem;margin-bottom:1.5rem;
                display:flex;align-items:center;gap:1rem">
        <div style="font-size:2rem">📋</div>
        <div>
            <div style="font-weight:700;color:#1f2937">Your current APS: {learner_aps}</div>
            <div style="font-size:0.85rem;color:#6b7280">
                The green badges below show which universities you currently qualify for.
                Use this as your study target guide.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs — one per chosen career ──────────────────────────────────────────
    tab_labels = []
    for i, result in enumerate(chosen_careers):
        c = result["career"]
        tab_labels.append(f"{RANK_LABELS[i].split()[0]} {c['icon']} {c['title']}")

    tabs = st.tabs(tab_labels)

    for tab_idx, (tab, result) in enumerate(zip(tabs, chosen_careers)):
        career    = result["career"]
        career_id = career["id"]
        colour    = RANK_COLOURS[tab_idx]
        guidance  = guidance_data.get(career_id)

        with tab:
            if not guidance:
                st.info("Detailed guidance for this career is coming soon.")
                continue

            # Career overview
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{colour}22,{colour}11);
                        border-left:4px solid {colour};border-radius:0 12px 12px 0;
                        padding:1rem 1.2rem;margin-bottom:1.5rem">
                <div style="font-size:0.75rem;color:{colour};
                            font-weight:700;text-transform:uppercase;
                            letter-spacing:0.05em">
                    {RANK_LABELS[tab_idx]}
                </div>
                <div style="font-size:1.4rem;font-weight:800;
                            color:#1f2937;margin:4px 0">
                    {career['icon']}  {career['title']}
                </div>
                <div style="color:#4b5563;font-size:0.9rem">
                    {career['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Quick stats row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="card" style="text-align:center;padding:0.9rem">
                    <div style="font-size:1.5rem">🎓</div>
                    <div style="font-size:0.7rem;color:#9ca3af">Qualification</div>
                    <div style="font-weight:700;color:#1f2937;
                                font-size:0.82rem;margin-top:2px">
                        {guidance['qualification']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="card" style="text-align:center;padding:0.9rem">
                    <div style="font-size:1.5rem">⏱️</div>
                    <div style="font-size:0.7rem;color:#9ca3af">Duration</div>
                    <div style="font-weight:700;color:#1f2937;
                                font-size:0.9rem;margin-top:2px">
                        {guidance['duration']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                sal = guidance["salary"]
                st.markdown(f"""
                <div class="card" style="text-align:center;padding:0.9rem">
                    <div style="font-size:1.5rem">💰</div>
                    <div style="font-size:0.7rem;color:#9ca3af">Senior Salary</div>
                    <div style="font-weight:700;color:#10b981;
                                font-size:0.82rem;margin-top:2px">
                        {sal['senior']} /yr
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Universities ──────────────────────────────────────────────────
            st.markdown(f"#### 🏫 Universities Offering This Programme")

            for uni in guidance["universities"]:
                badge = aps_gap_badge(learner_aps, uni["min_aps"])
                st.markdown(f"""
                <div class="card" style="margin-bottom:0.75rem">
                    <div style="display:flex;justify-content:space-between;
                                align-items:flex-start;flex-wrap:wrap;gap:8px">
                        <div>
                            <div style="font-weight:700;color:#1f2937;font-size:1rem">
                                {uni['name']}
                                <span style="color:#9ca3af;font-weight:400;
                                             font-size:0.82rem">
                                    ({uni['short']})
                                </span>
                            </div>
                            <div style="margin-top:4px">{badge}</div>
                        </div>
                        <div style="text-align:right">
                            <div style="font-size:0.75rem;color:#6b7280">Min APS</div>
                            <div style="font-size:1.6rem;font-weight:800;
                                        color:{colour};line-height:1">
                                {uni['min_aps']}
                            </div>
                        </div>
                    </div>
                    <div style="margin-top:10px;display:flex;
                                flex-wrap:wrap;gap:12px;font-size:0.82rem">
                        <span>
                            📚 <strong>Required:</strong> {uni['required_subjects']}
                        </span>
                        <span>
                            📅 <strong>Deadline:</strong> {uni['deadline']}
                        </span>
                    </div>
                    <div style="margin-top:6px;font-size:0.82rem;
                                color:#6b7280;font-style:italic">
                        💡 {uni['notes']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Salary ladder ─────────────────────────────────────────────────
            st.markdown("#### 💰 Salary Progression")
            sal = guidance["salary"]
            sc1, sc2, sc3 = st.columns(3)
            salary_stages = [
                (sc1, "Entry Level", sal["entry"], "0–3 years", "#94a3b8"),
                (sc2, "Mid Career",  sal["mid"],   "4–9 years", "#667eea"),
                (sc3, "Senior",      sal["senior"],"10+ years", "#10b981"),
            ]
            for col, stage, amount, years, clr in salary_stages:
                with col:
                    st.markdown(f"""
                    <div class="card" style="text-align:center;padding:0.9rem">
                        <div style="font-size:0.72rem;color:#9ca3af;
                                    text-transform:uppercase;font-weight:600">
                            {stage}
                        </div>
                        <div style="font-size:1rem;font-weight:800;
                                    color:{clr};margin:4px 0">
                            {amount}
                        </div>
                        <div style="font-size:0.72rem;color:#9ca3af">{years}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Job roles ─────────────────────────────────────────────────────
            st.markdown("#### 💼 Possible Job Roles")
            roles_html = "".join([
                f'<span style="background:#ede9fe;color:#7c3aed;'
                f'border-radius:20px;padding:4px 12px;font-size:0.82rem;'
                f'font-weight:500;margin:3px;display:inline-block">'
                f'{role}</span>'
                for role in guidance["job_roles"]
            ])
            st.markdown(
                f'<div style="display:flex;flex-wrap:wrap;gap:4px;'
                f'margin-bottom:1rem">{roles_html}</div>',
                unsafe_allow_html=True,
            )

            # ── Bursaries ─────────────────────────────────────────────────────
            st.markdown("#### 🏆 Bursary Opportunities")
            bursaries_html = "".join([
                f'<span style="background:#ecfdf5;color:#059669;'
                f'border-radius:20px;padding:4px 12px;font-size:0.82rem;'
                f'font-weight:500;margin:3px;display:inline-block">'
                f'✓ {b}</span>'
                for b in guidance["bursaries"]
            ])
            st.markdown(
                f'<div style="display:flex;flex-wrap:wrap;gap:4px;'
                f'margin-bottom:1rem">{bursaries_html}</div>',
                unsafe_allow_html=True,
            )

            # ── Application tips ──────────────────────────────────────────────
            st.markdown("#### 📌 Application Tips")
            st.markdown(f"""
            <div style="background:#fffbeb;border:1px solid #fcd34d;
                        border-radius:12px;padding:1rem 1.2rem;
                        color:#92400e;font-size:0.9rem;line-height:1.6">
                {guidance['application_tips']}
            </div>
            """, unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_back, col_next = st.columns(2)

    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = "priority"
            st.rerun()

    with col_next:
        if st.button("Generate My PDF Roadmap →", use_container_width=True):
            st.session_state.screen = "roadmap"
            st.rerun()