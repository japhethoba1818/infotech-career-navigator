import json
import streamlit as st
from logic.aps_calculator import calculate_aps, get_strong_subjects


# ── Helpers ──────────────────────────────────────────────────────────────────

def progress_dots(current: int, total: int = 7):
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


def load_subjects() -> list:
    with open("data/subjects.json") as f:
        return json.load(f)["subjects"]


def group_by_category(subjects: list) -> dict:
    """Group subjects by their category for organised display."""
    groups = {}
    for s in subjects:
        cat = s["category"]
        groups.setdefault(cat, []).append(s)
    return groups


CATEGORY_LABELS = {
    "language":    "🗣️  Languages",
    "core":        "🔢  Mathematics",
    "science":     "🔬  Sciences",
    "commerce":    "💼  Commerce",
    "humanities":  "🌍  Humanities",
    "technology":  "💻  Technology",
    "arts":        "🎨  Arts",
    "compulsory":  "📋  Compulsory",
}

RATING_LABELS = {
    1: "Level 1 — 0–29%",
    2: "Level 2 — 30–39%",
    3: "Level 3 — 40–49%",
    4: "Level 4 — 50–59%",
    5: "Level 5 — 60–69%",
    6: "Level 6 — 70–79%",
    7: "Level 7 — 80–100%",
}


# ── Main screen ───────────────────────────────────────────────────────────────

def show():
    progress_dots(2)

    name = st.session_state.learner_name

    st.markdown(
        f'<h1 class="hero-title">Your Subjects, {name.split()[0]} 📚</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-subtitle">Select the subjects you take at school and '
        'rate your current performance level for each one.</p>',
        unsafe_allow_html=True,
    )

    # ── Instructions card ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="card">
        <strong>How to use this page:</strong><br>
        <span style="color:#6b7280;font-size:0.9rem">
        1. Tick the box next to each subject you take.<br>
        2. Use the slider to select your current performance level (1–7).<br>
        3. Be honest — this helps us recommend the best career for you.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Load subjects and build selection UI ─────────────────────────────────
    all_subjects = load_subjects()
    grouped = group_by_category(all_subjects)

    selected_subjects = {}   # will hold {code: rating}

    for category, label in CATEGORY_LABELS.items():
        subjects_in_group = grouped.get(category, [])
        if not subjects_in_group:
            continue

        st.markdown(f"### {label}")

        for subject in subjects_in_group:
            code = subject["code"]
            name_display = subject["name"]

            # Use a unique key per subject to avoid Streamlit key conflicts
            checkbox_key = f"chk_{code}"
            slider_key   = f"sldr_{code}"

            col1, col2 = st.columns([1, 2])

            with col1:
                selected = st.checkbox(
                    name_display,
                    key=checkbox_key,
                    value=(code in st.session_state.get("selected_subjects", {})),
                )

            with col2:
                if selected:
                    previous_rating = st.session_state.get(
                        "selected_subjects", {}
                    ).get(code, 4)

                    rating = st.select_slider(
                        f"Performance for {name_display}",
                        options=[1, 2, 3, 4, 5, 6, 7],
                        value=previous_rating,
                        format_func=lambda x: RATING_LABELS[x],
                        key=slider_key,
                        label_visibility="collapsed",
                    )
                    selected_subjects[code] = rating
                else:
                    st.markdown(
                        '<span style="color:#d1d5db;font-size:0.85rem">'
                        'Tick to select this subject</span>',
                        unsafe_allow_html=True,
                    )

        st.markdown("---")

    # ── Live APS preview ──────────────────────────────────────────────────────
    if selected_subjects:
        aps_result = calculate_aps(selected_subjects)
        aps_score  = aps_result["capped_aps"]
        aps_label  = aps_result["level_label"]
        count      = aps_result["subject_count"]

        st.markdown(f"""
        <div class="card" style="text-align:center;border:2px solid #667eea;">
            <p style="margin:0;color:#6b7280;font-size:0.85rem">
                Your estimated APS ({count} subjects · Life Orientation excluded)"
            </p>
            <p style="margin:4px 0;font-size:3rem;font-weight:800;
                      background:linear-gradient(135deg,#667eea,#764ba2);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                {aps_score}
            </p>
            <p style="margin:0;color:#4b5563;font-size:0.9rem">{aps_label}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <p style="color:#9ca3af;margin:0">
                Select your subjects above to see your APS score here.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    col_back, col_next = st.columns(2)

    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = "landing"
            st.rerun()

    with col_next:
        if st.button("Next — Personality Quiz →", use_container_width=True):
            if len(selected_subjects) < 3:
                st.warning("Please select at least 3 subjects before continuing.")
            else:
                aps_result = calculate_aps(selected_subjects)
                st.session_state.selected_subjects = selected_subjects
                st.session_state.aps_score          = aps_result["capped_aps"]
                st.session_state.strong_subjects     = get_strong_subjects(selected_subjects)
                st.session_state.screen              = "personality"
                st.rerun()