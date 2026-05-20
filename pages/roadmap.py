import json
import streamlit as st
from logic.pdf_generator import generate_pdf


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


def load_personality_meta() -> tuple:
    with open("data/personality.json") as f:
        data = json.load(f)
    return data["personality_types"], data["type_descriptions"]


def build_pdf_data() -> dict:
    """
    Pull everything from session state into one clean dict
    for the PDF generator.
    """
    labels, descs = load_personality_meta()
    guidance      = load_guidance()

    chosen        = st.session_state.get("chosen_careers", [])
    primary       = chosen[0]["career"] if chosen else {}
    primary_pct   = chosen[0]["match_pct"] if chosen else 0

    top_pers_code = (st.session_state.get("top_personality") or ["ANL"])[0]
    top_pers_lbl  = labels.get(top_pers_code, "")
    top_pers_desc = descs.get(top_pers_code, "")

    aps           = st.session_state.get("aps_score", 0)
    target_aps    = min(aps + 5, 42)   # motivational target

    primary_id    = primary.get("id", "")
    qualification = guidance.get(primary_id, {}).get("qualification", "your qualification")

    return {
        "learner_name":          st.session_state.get("learner_name", "Learner"),
        "aps_score":             aps,
        "target_aps":            target_aps,
        "subject_count":         len(st.session_state.get("selected_subjects", {})),
        "subject_ratings":       st.session_state.get("selected_subjects", {}),
        "strong_subjects":       st.session_state.get("strong_subjects", []),
        "top_personality_code":  top_pers_code,
        "top_personality_label": top_pers_lbl,
        "top_personality_desc":  top_pers_desc,
        "personality_scores":    st.session_state.get("personality_scores", {}),
        "top_personality":       st.session_state.get("top_personality", []),
        "primary_career":        primary,
        "primary_match_pct":     primary_pct,
        "chosen_careers":        chosen,
        "guidance":              guidance,
        "qualification":         qualification,
    }


# ── Main screen ───────────────────────────────────────────────────────────────

def show():
    progress_dots(7)

    guidance      = load_guidance()
    chosen        = st.session_state.get("chosen_careers", [])
    name          = st.session_state.learner_name
    first_name    = name.split()[0]

    if not chosen:
        st.warning("Please complete the full journey before generating your PDF.")
        if st.button("← Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        return

    primary       = chosen[0]["career"]
    primary_pct   = chosen[0]["match_pct"]
    labels, descs = load_personality_meta()
    top_code      = (st.session_state.get("top_personality") or ["ANL"])[0]

    # ── Congratulations header ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                border-radius:20px;padding:2rem;text-align:center;
                margin-bottom:1.5rem">
        <div style="font-size:3rem;margin-bottom:0.5rem">🎉</div>
        <h1 style="color:white;margin:0;font-size:1.8rem;font-weight:800">
            You Did It, {first_name}!
        </h1>
        <p style="color:rgba(255,255,255,0.85);margin:8px 0 0 0;font-size:1rem">
            Your personalised career roadmap is ready to download.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── PDF preview card ──────────────────────────────────────────────────────
    st.markdown("### 📄 What's Inside Your PDF")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="card">
            <div style="font-weight:700;color:#1f2937;margin-bottom:0.75rem">
                📋 Page 1 — Your Manifesto
            </div>
            <div style="font-size:0.88rem;color:#4b5563;line-height:1.8">
                ✦ Future {primary['title']} — {name}<br>
                ✦ Your APS score: {st.session_state.aps_score}<br>
                ✦ Top personality: {labels.get(top_code, '')}<br>
                ✦ Your strongest subjects<br>
                ✦ All 3 career matches with scores<br>
                ✦ Personalised motivational quote
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        target_aps = min(st.session_state.aps_score + 5, 42)
        st.markdown(f"""
        <div class="card">
            <div style="font-weight:700;color:#1f2937;margin-bottom:0.75rem">
                🗺️ Page 2 — Your Action Plan
            </div>
            <div style="font-size:0.88rem;color:#4b5563;line-height:1.8">
                ✦ 5-Step personalised success roadmap<br>
                ✦ University targets with APS gaps<br>
                ✦ Subject improvement guide<br>
                ✦ Application checklist & deadlines<br>
                ✦ APS target: {target_aps}<br>
                ✦ Motivational closing message
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Journey summary ───────────────────────────────────────────────────────
    st.markdown("### 🏆 Your Journey Summary")

    c1, c2, c3, c4 = st.columns(4)
    summary_items = [
        (c1, "🎯", "Primary Career",    primary['title'],                          "#667eea"),
        (c2, "📋", "Your APS",          str(st.session_state.aps_score),           "#764ba2"),
        (c3, "🧠", "Personality",       labels.get(top_code, ""),                  "#f5576c"),
        (c4, "📊", "Match Score",       f"{primary_pct}%",                         "#10b981"),
    ]

    for col, icon, lbl, val, clr in summary_items:
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:0.9rem">
                <div style="font-size:1.5rem">{icon}</div>
                <div style="font-size:0.7rem;color:#9ca3af;
                            text-transform:uppercase;font-weight:600">
                    {lbl}
                </div>
                <div style="font-weight:800;color:{clr};
                            font-size:0.9rem;margin-top:4px">
                    {val}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Generate and download ─────────────────────────────────────────────────
    st.markdown("### ⬇️ Download Your PDF")

    # Generate PDF on page load (cache in session to avoid regenerating)
    if "pdf_bytes" not in st.session_state or st.session_state.pdf_bytes is None:
        with st.spinner("Building your personalised roadmap PDF..."):
            pdf_data  = build_pdf_data()
            pdf_bytes = generate_pdf(pdf_data)
            st.session_state.pdf_bytes = pdf_bytes
    else:
        pdf_bytes = st.session_state.pdf_bytes

    safe_name = name.replace(" ", "_")

    st.markdown("""
    <div style="background:#ecfdf5;border:1px solid #6ee7b7;
                border-radius:12px;padding:1rem 1.2rem;
                margin-bottom:1rem;font-size:0.9rem;color:#065f46">
        ✅ Your PDF is ready! Click the button below to download it.
        Print it, save it, share it with your parents or teacher.
        This is your personal success plan.
    </div>
    """, unsafe_allow_html=True)

    st.download_button(
        label="⬇️  Download My Career Roadmap PDF",
        data=pdf_bytes,
        file_name=f"Career_Roadmap_{safe_name}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Sharing tip ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="card" style="text-align:center;padding:1.2rem">
        <div style="font-size:1.5rem">📲</div>
        <div style="font-weight:700;color:#1f2937;margin:4px 0">
            Share the App
        </div>
        <div style="color:#6b7280;font-size:0.88rem">
            Know a learner who needs direction? Share this app with them.<br>
            It is completely free and built specifically for South African learners.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    col_back, col_restart = st.columns(2)

    with col_back:
        if st.button("← Back to Guidance", use_container_width=True):
            st.session_state.screen = "guidance"
            st.rerun()

    with col_restart:
        if st.button("🔄  Start a New Journey", use_container_width=True):
            # Clear all session state and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()