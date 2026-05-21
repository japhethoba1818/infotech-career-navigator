import json
import streamlit as st


# ── Helpers ───────────────────────────────────────────────────────────────────

def progress_dots(current: int, total: int = 7):
    dots = ""
    for i in range(1, total + 1):
        cls = "done" if i < current else ("active" if i == current else "")
        dots += f'<span class="step-dot {cls}"></span>'
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)


def load_personality_data() -> dict:
    with open("data/personality.json") as f:
        return json.load(f)


def score_answers(questions: list, answers: dict) -> dict:
    """
    Tally personality scores from the learner's answers.

    Parameters
    ----------
    questions : list   — from personality.json
    answers   : dict   — {question_id: option_index (0-3)}

    Returns
    -------
    dict  — {personality_code: total_score}
    """
    totals = {"ANL": 0, "LDR": 0, "CRE": 0, "HLP": 0, "TEC": 0, "ENT": 0}

    for q in questions:
        qid = q["id"]
        if qid not in answers:
            continue
        chosen_index = answers[qid]
        option_scores = q["options"][chosen_index]["scores"]
        for code, pts in option_scores.items():
            totals[code] = totals.get(code, 0) + pts

    return totals


def get_top_types(scores: dict, top_n: int = 3) -> list:
    """Return the top N personality type codes, sorted by score."""
    return sorted(scores, key=scores.get, reverse=True)[:top_n]


# ── Main screen ────────────────────────────────────────────────────────────────

def show():
    progress_dots(3)

    data      = load_personality_data()
    questions = data["questions"]
    icons     = data["type_icons"]
    descs     = data["type_descriptions"]
    labels    = data["personality_types"]

    name = st.session_state.learner_name.split()[0]

    st.markdown(
        f'<h1 class="hero-title">Who Are You, {name}? 🧠</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-subtitle">Answer these 8 quick questions honestly. '
        'There are no right or wrong answers — just go with your first instinct.</p>',
        unsafe_allow_html=True,
    )

    # ── Progress bar ──────────────────────────────────────────────────────────
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}

    answered = len(st.session_state.quiz_answers)
    total_q  = len(questions)
    pct      = int((answered / total_q) * 100)

    st.markdown(f"""
    <div style="margin-bottom:1.5rem">
        <div style="display:flex;justify-content:space-between;
                    font-size:0.85rem;color:#6b7280;margin-bottom:4px">
            <span>Questions answered</span>
            <span><strong>{answered}</strong> / {total_q}</span>
        </div>
        <div style="background:#e5e7eb;border-radius:99px;height:8px">
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        width:{pct}%;height:8px;border-radius:99px;
                        transition:width 0.3s ease">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Questions ─────────────────────────────────────────────────────────────
    for q in questions:
        qid     = q["id"]
        options = [opt["text"] for opt in q["options"]]

        # Work out what was previously selected (if anything)
        prev = st.session_state.quiz_answers.get(qid, None)
        prev_text = options[prev] if prev is not None else None

        st.markdown(f"""
        <div class="card">
            <p style="font-weight:600;margin:0 0 0.75rem 0;color:#1f2937">
                {qid}. {q['question']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        chosen = st.radio(
            label=f"q{qid}",
            options=options,
            index=prev if prev is not None else None,
            key=f"radio_{qid}",
            label_visibility="collapsed",
        )

        # Save answer as index immediately
        if chosen:
            st.session_state.quiz_answers[qid] = options.index(chosen)

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Live personality preview ───────────────────────────────────────────────
    answered_now = len(st.session_state.quiz_answers)

    if answered_now >= 4:
        scores    = score_answers(questions, st.session_state.quiz_answers)
        top_types = get_top_types(scores, top_n=3)

        st.markdown("### 👀 Your Emerging Personality Profile")
        st.markdown(
            '<p style="color:#6b7280;font-size:0.85rem;margin-top:-0.5rem">'
            'Based on your answers so far — this updates as you answer more.</p>',
            unsafe_allow_html=True,
        )

        cols = st.columns(3)
        for i, code in enumerate(top_types):
            with cols[i]:
                rank_label = ["🥇 Primary", "🥈 Secondary", "🥉 Third"][i]
                st.markdown(f"""
                <div class="card" style="text-align:center;padding:1rem">
                    <div style="font-size:2rem">{icons[code]}</div>
                    <div style="font-size:0.75rem;color:#7c3aed;
                                font-weight:600;margin:4px 0">{rank_label}</div>
                    <div style="font-weight:700;color:#1f2937">{labels[code]}</div>
                    <div style="font-size:0.8rem;color:#6b7280;margin-top:4px">
                        {descs[code]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    col_back, col_next = st.columns(2)

    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = "subjects"
            st.rerun()

    with col_next:
        if st.button("See My Career Matches →", use_container_width=True):
            if answered_now < total_q:
                remaining = total_q - answered_now
                st.warning(
                    f"Please answer all questions. "
                    f"You still have {remaining} question(s) to go."
                )
            else:
                # Final scoring — save to session state
                final_scores    = score_answers(questions, st.session_state.quiz_answers)
                top_personality = get_top_types(final_scores, top_n=3)

                st.session_state.personality_scores = final_scores
                st.session_state.top_personality    = top_personality
                st.session_state.screen             = "results"
                st.rerun()