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
        chosen_index  = answers[qid]
        option_scores = q["options"][chosen_index]["scores"]
        for code, pts in option_scores.items():
            totals[code] = totals.get(code, 0) + pts

    return totals


def get_top_types(scores: dict, top_n: int = 3) -> list:
    """Return the top N personality type codes, sorted by score."""
    return sorted(scores, key=scores.get, reverse=True)[:top_n]


def render_question_card(q: dict, qid: int, options: list) -> None:
    """
    Render a single question as styled scenario cards.
    Replaces st.radio() — scoring logic stays identical.
    """
    prev          = st.session_state.quiz_answers.get(qid, None)
    answered      = prev is not None

    # Question header card
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#667eea15,#764ba215);
                border-left:4px solid #667eea;border-radius:12px;
                padding:1rem 1.2rem;margin-bottom:0.75rem">
        <div style="font-size:0.75rem;color:#667eea;font-weight:700;
                    text-transform:uppercase;letter-spacing:0.05em;
                    margin-bottom:0.3rem">
            Question {qid} of {len(st.session_state.get("_questions", []))}
        </div>
        <p style="font-weight:700;margin:0;color:#1f2937;font-size:1rem;
                  line-height:1.5">
            {q['question']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Option cards — two per row for mobile friendliness
    option_pairs = [options[i:i+2] for i in range(0, len(options), 2)]

    for pair_idx, pair in enumerate(option_pairs):
        cols = st.columns(len(pair))
        for col_idx, option_text in enumerate(pair):
            global_idx    = pair_idx * 2 + col_idx
            is_selected   = prev == global_idx

            border_color  = "#667eea" if is_selected else "#e5e7eb"
            bg_color      = "#ede9fe" if is_selected else "#ffffff"
            check_icon    = "✓ " if is_selected else ""
            text_color    = "#4c1d95" if is_selected else "#374151"
            shadow        = "0 0 0 3px #667eea33" if is_selected else "none"

            with cols[col_idx]:
                # Styled card as visual context
                st.markdown(f"""
                <div style="
                    border:2px solid {border_color};
                    background:{bg_color};
                    border-radius:12px;
                    padding:0.85rem 1rem;
                    margin-bottom:4px;
                    box-shadow:{shadow};
                    min-height:80px;
                    display:flex;
                    align-items:center;
                ">
                    <span style="color:{text_color};font-size:0.88rem;
                                 line-height:1.5;font-weight:{'600' if is_selected else '400'}">
                        {check_icon}{option_text}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                # Invisible select button sits under each card
                if st.button(
                    "Select" if not is_selected else "✓ Selected",
                    key=f"q{qid}_opt{global_idx}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                ):
                    st.session_state.quiz_answers[qid] = global_idx
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)


# ── Main screen ────────────────────────────────────────────────────────────────

def show():
    progress_dots(3)

    data      = load_personality_data()
    questions = data["questions"]
    icons     = data["type_icons"]
    descs     = data["type_descriptions"]
    labels    = data["personality_types"]

    # Store questions in session so render_question_card can access total count
    st.session_state["_questions"] = questions

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

    # Motivational label that changes as learner progresses
    if pct == 0:
        progress_label = "Let's find out who you are 🚀"
    elif pct < 40:
        progress_label = "Good start, keep going! 💪"
    elif pct < 75:
        progress_label = "You're halfway there! 🔥"
    elif pct < 100:
        progress_label = "Almost done, one more push! ⚡"
    else:
        progress_label = "All done — let's see your results! 🎉"

    st.markdown(f"""
    <div style="margin-bottom:1.5rem">
        <div style="display:flex;justify-content:space-between;
                    font-size:0.85rem;color:#6b7280;margin-bottom:4px">
            <span>{progress_label}</span>
            <span><strong>{answered}</strong> / {total_q} answered</span>
        </div>
        <div style="background:#e5e7eb;border-radius:99px;height:10px">
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        width:{pct}%;height:10px;border-radius:99px;
                        transition:width 0.3s ease">
            </div>
        </div>
        <div style="display:flex;justify-content:flex-end;
                    font-size:0.78rem;color:#667eea;
                    font-weight:600;margin-top:4px">
            {pct}% complete
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Questions rendered as scenario cards ──────────────────────────────────
    for q in questions:
        qid     = q["id"]
        options = [opt["text"] for opt in q["options"]]
        render_question_card(q, qid, options)

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

    # ── Completion celebration ─────────────────────────────────────────────────
    if answered_now == total_q:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#10b98115,#059e6f15);
                    border:2px solid #10b981;border-radius:16px;
                    padding:1.2rem;text-align:center;margin:1rem 0">
            <div style="font-size:2rem;margin-bottom:0.4rem">🎉</div>
            <div style="font-weight:800;color:#065f46;font-size:1rem">
                All questions answered!
            </div>
            <div style="color:#6b7280;font-size:0.88rem;margin-top:4px">
                Click below to see your career matches.
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