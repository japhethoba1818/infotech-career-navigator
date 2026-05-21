"""
Career Matcher — Faculty-First Architecture
===========================================

STAGE 1 — Faculty Matching
    Score every faculty using three signals:
    · Personality match  (55%) — dominant signal, drives differentiation
    · Subject match      (30%) — separates similar personalities by subjects
    · APS accessibility  (15%) — ensures realism

STAGE 2 — Career Matching Within Faculty
    Once learner selects a faculty, score careers within it:
    · Subject match      (40%)
    · APS match          (30%)
    · Personality match  (30%)
"""

import json


# ── Data loaders ──────────────────────────────────────────────────────────────

def load_careers() -> list:
    with open("data/careers.json") as f:
        return json.load(f)["careers"]


def load_faculties() -> list:
    with open("data/faculties.json") as f:
        return json.load(f)["faculties"]


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 1 — FACULTY MATCHING
# ══════════════════════════════════════════════════════════════════════════════

def _faculty_personality_score(faculty: dict, personality_scores: dict) -> float:
    """
    Score how well the learner's personality fits this faculty.
    Max learner score per type = 8 questions × 3 pts = 24.
    """
    weights      = faculty.get("personality_weights", {})
    max_possible = sum(w * 24 for w in weights.values())
    raw          = sum(
        weights.get(code, 0) * personality_scores.get(code, 0)
        for code in weights
    )
    if max_possible == 0:
        return 50.0
    return round(min((raw / max_possible) * 100, 100), 1)


def _faculty_subject_score(faculty: dict, subject_ratings: dict) -> float:
    """
    Score how well the learner's subjects align with this faculty.
    """
    indicators = faculty.get("subject_indicators", [])
    if not indicators:
        return 50.0
    max_possible = len(indicators) * 7.0
    raw          = sum(subject_ratings.get(code, 0) for code in indicators)
    return round((raw / max_possible) * 100, 1)


def _faculty_aps_score(faculty: dict, learner_aps: int) -> float:
    """Score APS accessibility for this faculty."""
    min_aps = faculty.get("min_aps", 20)
    gap     = learner_aps - min_aps
    if gap >= 0:
        return 100.0
    elif gap >= -5:
        return 75.0
    elif gap >= -10:
        return 45.0
    else:
        return 20.0


def _faculty_reasons(
    faculty: dict,
    personality_scores: dict,
    subject_ratings: dict,
    personality_labels: dict,
    personality_icons: dict,
) -> list:
    """Build 2-3 personalised explanation bullets for a faculty match."""
    reasons = []
    weights = faculty.get("personality_weights", {})

    # Find personality types that both the faculty values AND the learner has
    type_contributions = [
        (code, weights.get(code, 0) * personality_scores.get(code, 0))
        for code in weights
        if weights.get(code, 0) >= 2 and personality_scores.get(code, 0) > 3
    ]
    type_contributions.sort(key=lambda x: x[1], reverse=True)

    for code, _ in type_contributions[:2]:
        label = personality_labels.get(code, code)
        icon  = personality_icons.get(code, "💡")
        reasons.append(f"{icon} Your {label} personality is a strong match for this field")

    # Subject reasons
    indicators   = faculty.get("subject_indicators", [])
    strong_match = [
        c for c in indicators
        if c in subject_ratings and subject_ratings[c] >= 5
    ]
    good_match   = [
        c for c in indicators
        if c in subject_ratings and 3 <= subject_ratings[c] < 5
    ]

    if strong_match:
        reasons.append(f"📚 You are performing well in {_codes_to_names(strong_match[:2])}")
    elif good_match:
        reasons.append(f"📚 Your {_codes_to_names(good_match[:2])} background is a solid foundation")

    return reasons if reasons else ["This field aligns with your overall academic and personal profile."]


def match_faculties(
    personality_scores: dict,
    subject_ratings: dict,
    learner_aps: int,
    personality_labels: dict,
    personality_icons: dict,
    top_n: int = 3,
) -> list:
    """
    Score all faculties and return the top N.

    Returns list of dicts:
        faculty           : full faculty dict from JSON
        match_pct         : overall match percentage
        personality_score : sub-score
        subject_score     : sub-score
        aps_score         : sub-score
        reasons           : list of explanation strings
    """
    faculties = load_faculties()
    scored    = []

    for faculty in faculties:
        p = _faculty_personality_score(faculty, personality_scores)
        s = _faculty_subject_score(faculty, subject_ratings)
        a = _faculty_aps_score(faculty, learner_aps)

        total   = (p * 0.55) + (s * 0.30) + (a * 0.15)
        reasons = _faculty_reasons(
            faculty, personality_scores, subject_ratings,
            personality_labels, personality_icons,
        )

        scored.append({
            "faculty":            faculty,
            "match_pct":          round(total),
            "personality_score":  round(p),
            "subject_score":      round(s),
            "aps_score":          round(a),
            "reasons":            reasons,
        })

    scored.sort(key=lambda x: x["match_pct"], reverse=True)
    return scored[:top_n]


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 2 — CAREER MATCHING WITHIN A FACULTY
# ══════════════════════════════════════════════════════════════════════════════

def match_careers_in_faculty(
    faculty_id: str,
    subject_ratings: dict,
    learner_aps: int,
    personality_scores: dict,
    top_personality: list,
    personality_labels: dict,
    personality_icons: dict,
    top_n: int = 3,
) -> list:
    """
    Score and return the top N careers within a specific faculty.

    Returns same structure as old match_careers() so priority.py,
    guidance.py and roadmap.py all work without changes.
    """
    faculties = load_faculties()
    faculty   = next((f for f in faculties if f["id"] == faculty_id), None)

    if not faculty:
        return []

    career_ids    = faculty.get("career_ids", [])
    all_careers   = load_careers()
    subset        = [c for c in all_careers if c["id"] in career_ids]

    scored = []
    for career in subset:
        s = _subject_score(career, subject_ratings)
        a = _aps_score(career, learner_aps)
        p = _career_personality_score(career, personality_scores)

        total   = (s * 0.40) + (a * 0.30) + (p * 0.30)
        reasons = _build_reasons(
            career, subject_ratings, learner_aps,
            top_personality, personality_labels, personality_icons,
        )

        scored.append({
            "career":            career,
            "match_pct":         round(total),
            "subject_score":     round(s),
            "aps_score":         round(a),
            "personality_score": round(p),
            "reasons":           reasons,
        })

    scored.sort(key=lambda x: x["match_pct"], reverse=True)
    return scored[:top_n]


# ── Career-level scoring helpers ──────────────────────────────────────────────

def _subject_score(career: dict, subject_ratings: dict) -> float:
    raw   = 0.0
    max_r = 0.0

    for code in career.get("required_subjects", []):
        max_r += 3.0
        if code in subject_ratings:
            raw += 3.0 * (subject_ratings[code] / 7.0)

    for code in career.get("preferred_subjects", []):
        max_r += 1.0
        if code in subject_ratings:
            raw += 1.0 * (subject_ratings[code] / 7.0)

    if max_r == 0:
        return 60.0
    return round((raw / max_r) * 100, 1)


def _aps_score(career: dict, learner_aps: int) -> float:
    min_aps = career.get("min_aps", 0)
    gap     = learner_aps - min_aps

    if gap >= 0:
        return 100.0
    elif gap >= -5:
        return 70.0
    elif gap >= -10:
        return 40.0
    else:
        return 15.0


def _career_personality_score(career: dict, personality_scores: dict) -> float:
    weights   = career.get("personality_match", {})
    max_score = sum(w * 24 for w in weights.values())
    raw       = sum(
        weights.get(code, 0) * personality_scores.get(code, 0)
        for code in weights
    )
    if max_score == 0:
        return 50.0
    return round(min((raw / max_score) * 100, 100), 1)


def _build_reasons(
    career: dict,
    subject_ratings: dict,
    learner_aps: int,
    top_personality: list,
    personality_labels: dict,
    personality_icons: dict,
) -> list:
    reasons = []

    matched_req  = [c for c in career.get("required_subjects", []) if c in subject_ratings]
    matched_pref = [c for c in career.get("preferred_subjects", []) if c in subject_ratings]

    if matched_req:
        reasons.append(f"📚 You take {_codes_to_names(matched_req)} — a key subject for this career")
    if matched_pref and len(reasons) < 2:
        reasons.append(f"✅ Your {_codes_to_names(matched_pref[:2])} background is an advantage")

    min_aps = career.get("min_aps", 0)
    gap     = learner_aps - min_aps
    if gap >= 0:
        reasons.append(f"🎯 Your APS of {learner_aps} meets the minimum requirement of {min_aps}")
    elif gap >= -5:
        reasons.append(
            f"📈 Your APS of {learner_aps} is close — just {abs(gap)} points "
            f"below the {min_aps} requirement"
        )

    weights      = career.get("personality_match", {})
    matched_pers = [t for t in top_personality if weights.get(t, 0) >= 2]
    if matched_pers:
        label = personality_labels.get(matched_pers[0], matched_pers[0])
        icon  = personality_icons.get(matched_pers[0], "💡")
        reasons.append(f"{icon} Your {label} personality is a strong fit for this career")

    return reasons if reasons else ["This career aligns well with your overall profile."]


def _codes_to_names(codes: list) -> str:
    code_map = {
        "MATH": "Mathematics", "MATLIT": "Mathematical Literacy",
        "PHY_SCI": "Physical Sciences", "LIFE_SCI": "Life Sciences",
        "AGR_SCI": "Agricultural Sciences", "ACC": "Accounting",
        "BUS_STU": "Business Studies", "ECON": "Economics",
        "GEO": "Geography", "HIST": "History",
        "IT": "IT", "CAT": "CAT",
        "EGD": "Engineering Graphics & Design",
        "VIS_ARTS": "Visual Arts", "DRAM": "Dramatic Arts",
        "ENG_HL": "English", "ENG_FAL": "English FAL",
        "AFR_HL": "Afrikaans", "ZUL_HL": "IsiZulu",
    }
    names = [code_map.get(c, c) for c in codes]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{', '.join(names[:-1])} and {names[-1]}"