"""
db_service.py
=============
All database operations live here.
Pages never talk to Supabase directly — they call these functions.
Failures are caught silently so the app never crashes due to a DB issue.
"""

import streamlit as st
from datetime import datetime, timedelta, timezone
import secrets as token_lib
from supabase_client import get_supabase
from data_loader import load_personality_labels


def save_learner_result(session: dict) -> str | None:
    """
    Saves a completed Career Navigator session to Supabase.

    Call this once when the learner reaches the roadmap screen.

    Parameters
    ----------
    session : dict
        Pass dict(st.session_state) from your roadmap page.

    Returns
    -------
    str | None
        The UUID of the saved learner record.
        Returns None if the save failed (app continues normally).
    """
    try:
        db = get_supabase()

        # ── Resolve personality label ─────────────────────────────────────────
        p_labels        = load_personality_labels()
        personality_scores = session.get("personality_scores", {})
        top_personality    = session.get("top_personality", [])
        top_p_code         = top_personality[0] if top_personality else ""
        top_p_label        = p_labels.get(top_p_code, top_p_code)

        # ── Resolve faculty ───────────────────────────────────────────────────
        faculty_data = session.get("selected_faculty_data", {}) or {}
        faculty_id   = faculty_data.get("id", "")
        faculty_name = faculty_data.get("name", "")

        # ── Resolve career lists ──────────────────────────────────────────────
        chosen_careers    = session.get("chosen_careers", []) or []
        all_matches       = session.get("career_matches", []) or []

        chosen_career_ids = [c["career"]["id"]    for c in chosen_careers]
        all_match_ids     = [c["career"]["id"]    for c in all_matches]
        all_match_titles  = [c["career"]["title"] for c in all_matches]

        # ── Build learner row ─────────────────────────────────────────────────
        learner_row = {
            "name":                  session.get("learner_name", ""),
            "aps_score":             int(session.get("aps_score", 0)),
            "subject_ratings":       session.get("selected_subjects", {}),
            "subject_count":         len(session.get("selected_subjects", {})),
            "personality_scores":    personality_scores,
            "top_personality":       top_p_code,
            "top_personality_label": top_p_label,
            "faculty_id":            faculty_id,
            "faculty_name":          faculty_name,
            "top_career_ids":        all_match_ids,
            "top_career_titles":     all_match_titles,
            "chosen_career_ids":     chosen_career_ids,
            "app_version":           "1.0",
        }

        result     = db.table("learners").insert(learner_row).execute()
        learner_id = result.data[0]["id"]

        # ── Build career_results rows ─────────────────────────────────────────
        chosen_ids  = set(chosen_career_ids)
        career_rows = []

        for rank, match in enumerate(all_matches[:5], start=1):
            career = match["career"]
            career_rows.append({
                "learner_id":        learner_id,
                "career_id":         career["id"],
                "career_title":      career["title"],
                "faculty_id":        faculty_id,
                "rank":              rank,
                "match_pct":         int(match.get("match_pct", 0)),
                "subject_score":     int(match.get("subject_score", 0)),
                "aps_score":         int(match.get("aps_score", 0)),
                "personality_score": int(match.get("personality_score", 0)),
                "was_chosen":        career["id"] in chosen_ids,
            })

        if career_rows:
            db.table("career_results").insert(career_rows).execute()

        # ── Build personality_results row ─────────────────────────────────────
        sorted_p  = sorted(personality_scores.items(), key=lambda x: x[1], reverse=True)
        is_hybrid = (
            len(sorted_p) >= 2
            and abs(sorted_p[0][1] - sorted_p[1][1]) <= 3
        )

        personality_row = {
            "learner_id":        learner_id,
            "scores":            personality_scores,
            "top_type":          sorted_p[0][0] if sorted_p else "",
            "second_type":       sorted_p[1][0] if len(sorted_p) > 1 else None,
            "third_type":        sorted_p[2][0] if len(sorted_p) > 2 else None,
            "question_answers":  session.get("quiz_answers", {}),
            "is_hybrid":         is_hybrid,
        }

        db.table("personality_results").insert(personality_row).execute()

        return learner_id

    except Exception as e:
        st.warning(
            f"⚠️ Your results could not be saved to the cloud. "
            f"Your roadmap is still ready to download. (Details: {e})"
        )
        return None


def create_study_companion_transfer(learner_id: str, session: dict) -> str | None:
    """
    Creates a one-time transfer token so Study Companion can
    receive the learner's context automatically on arrival.

    Parameters
    ----------
    learner_id : str
        UUID returned by save_learner_result().
    session : dict
        Pass dict(st.session_state) from your roadmap page.

    Returns
    -------
    str | None
        The token string to append to the Study Companion URL.
        Returns None if creation failed.
    """
    try:
        db      = get_supabase()
        token   = token_lib.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=24)

        chosen_careers = session.get("chosen_careers", []) or []
        primary        = chosen_careers[0]["career"] if chosen_careers else {}
        top_p          = session.get("top_personality", [])

        row = {
            "learner_id":           learner_id,
            "learner_name":         session.get("learner_name", ""),
            "grade":                session.get("grade"),
            "subject_ratings":      session.get("selected_subjects", {}),
            "aps_score":            int(session.get("aps_score", 0)),
            "primary_career_id":    primary.get("id", ""),
            "primary_career_title": primary.get("title", ""),
            "personality_type":     top_p[0] if top_p else "",
            "transfer_token":       token,
            "token_expires_at":     expires.isoformat(),
        }

        db.table("study_companion_transfers").insert(row).execute()
        return token

    except Exception as e:
        return None